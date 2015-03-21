#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Worker """

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"

import logging
import datetime
import threading
import time
import Queue
import multiprocessing
from multiprocessing import queues

from mna.model import db
from mna.model import dbobjects as DBO
from mna import plugins
from mna.model import base
from mna.lib import appconfig
from mna.common import messenger
from mna.model import repo

_LOG = logging.getLogger(__name__)
_LONG_SLEEP = 15  # sleep when no source processed
_SHORT_SLEEP = 1  # sleep after retrieve articles from source
_WORKERS = 3  # number of background workers


# pylint:disable=no-member,too-few-public-methods
class Worker(multiprocessing.Process):
    """ Worker - process one source and store result in database.

    Arguments:
        source_id: source to process
    """
    def __init__(self, update_q, terminate_event, gui_update_queue):
        super(Worker, self).__init__()
        self.update_q = update_q
        self.gui_update_queue = gui_update_queue
        self.aconf = appconfig.AppConfig()
        self.terminate_event = terminate_event
        self._p_name = "Worker: id=%d" % id(self)

    def run(self):
        while not self.terminate_event.is_set():
            source_id = self.update_q.get()
            self._p_name = "Worker: id=%d src=%d" % (id(self), source_id)
            _LOG.debug("%s in queue: %d", self._p_name, self.update_q.qsize())
            try:
                self._run(source_id)
            finally:
                self.update_q.task_done()

    def _run(self, source_id):
        session = db.Session(autoflush=False, autocommit=False)
        source_cfg = self._get_and_check_source(session, source_id)
        if not source_cfg or source_cfg.processing:
            _LOG.warn("%s not processing %r", self._p_name, source_cfg)
            self.gui_update_queue.put(('source_update_error',
                                       (source_cfg.oid, source_cfg.group_id,
                                        source_cfg.title)))
            return

        _LOG.debug("%s processing %s/%s", self._p_name, source_cfg.name,
                   source_cfg.title)
        now = datetime.datetime.now()
        source_cfg.processing = 1
        session.commit()
        last_conf_updated = source_cfg.conf_updated

        # find plugin
        source = self._get_source(session, source_cfg)
        if not source:
            _LOG.error("%s source class not found for %r %r",
                       self._p_name, source_cfg.name, source_cfg.title)
            source_cfg.add_log("ERROR", "Internal error: source not found")
            return
        # load articles
        cnt = self._load_articles(source, source_cfg, session)
        if cnt < 0:
            self.gui_update_queue.put(('source_update_error',
                                       (source_cfg.oid, source_cfg.group_id,
                                        source_cfg.title)))
            return
        # update configuration
        force_update = bool(source_cfg.last_error) or \
            last_conf_updated != source_cfg.conf_updated

        interval = source_cfg.interval or self.aconf.get(
            'articles.update_interval', 60)
        source_cfg.next_refresh = now + datetime.timedelta(minutes=interval)
        source_cfg.last_refreshed = now
        source_cfg.processing = 0
        source_cfg.failure_counter = 0
        source_cfg.last_error = None
        source_cfg.last_error_date = None

        # store resources in repository
        repository = repo.Reporitory()
        for res_name, res_content in source.get_resources():
            repository.store_file(res_name, res_content)

        session.commit()
        self.gui_update_queue.put(('source_update',
                                   (source_cfg.oid, source_cfg.group_id,
                                    source_cfg.title, cnt, force_update)))
        _LOG.debug("%s finished", self._p_name)
        return

    def _load_articles(self, source, source_cfg, session):
        cnt = 0
        try:
            articles = source.get_items(
                session,
                self.aconf.get('articles.max_num_load', 0),
                self.aconf.get('articles.max_age_load', 0))
            if articles:
                if source_cfg.conf.get('filter.enabled', True):
                    articles = self._filter_articles(articles, session,
                                                     source_cfg)
                    cnt = sum(_save_articls(articles, session, source_cfg))
                    source_cfg.add_log('info', "Found new %d articles" % cnt)
        except base.GetArticleException, err:
            # some processing error occurred
            _LOG.error("%s Load articles from %s/%s error: %r",
                       self._p_name, source_cfg.name, source_cfg.title,
                       err)
            _on_error(session, source_cfg, str(err))
            return -1
        except Exception, err:  # pylint:disable=broad-except
            _LOG.exception("%s Load articles from %s/%s error: %r",
                           self._p_name, source_cfg.name, source_cfg.title,
                           err)
            _on_error(session, source_cfg, str(err))
            return -1
        else:
            _LOG.debug("%s Loaded %d from %s/%s", self._p_name, cnt,
                       source_cfg.name, source_cfg.title)
        return cnt

    # pylint: disable=no-self-use
    def _get_and_check_source(self, session, source_id):
        source_cfg = db.get_one(DBO.Source, session=session,
                                oid=source_id)
        if not source_cfg or \
                source_cfg.next_refresh > datetime.datetime.now():
            return None
        return source_cfg

    def _get_source(self, session, source_cfg):
        source_cls = plugins.SOURCES.get(source_cfg.name)
        if not source_cls:
            _LOG.error("%s unknown source: %s in %r", self._p_name,
                       source_cls, source_cfg)
            source_cfg.enabled = False
            _on_error(session, source_cfg, "unknown source")
            return None
        source = source_cls(source_cfg)
        return source

    def _load_filters(self, source_cfg, session):
        for fltr in source_cfg.get_filters():
            fltr_cls = plugins.FILTERS.get(fltr.name)
            if not fltr_cls:
                _LOG.error("%s unknown filter: %s in %r", self._p_name,
                           fltr.name, fltr.oid)
                _on_error(session, source_cfg, "unknown filter")
                continue
            yield fltr_cls(fltr)

    def _get_min_score(self, source_cfg):
        min_score = -999
        if source_cfg.conf.get('filter.score', True):
            min_score = self.aconf.get('filter.min_score') \
                if source_cfg.conf.get('filter.use_default_score') \
                else source_cfg.conf.get('filter.min_score', 0)
        return min_score

    def _filter_articles(self, articles, session, source_cfg):
        filters = list(self._load_filters(source_cfg, session))
        min_score = self._get_min_score(source_cfg)
        for article in articles:
            for ftr in filters:
                article = ftr.filter(article)
            # score
            article.score = max(min(article.score, 100), -100)
            if article.score < min_score:
                _LOG.debug('%s article %r to low score (min: %d)',
                           self._p_name, article.title, min_score)
                continue
            yield article

    # pylint:disable=no-self-use
    def _get_icon(self, source, _session, source_cfg):
        iconname = source.get_icon()
        if iconname and iconname[0]:
            icon, icon_name = iconname
            name = "_".join(('src', str(source_cfg.oid), icon_name))
            repo.Reporitory().store_file(name, icon)
            source_cfg.icon_id = name


def _save_articls(articles, session, source_cfg):
    for article in articles:
        article.source_id = source_cfg.oid
        session.merge(article)
        yield 1


def _on_error(session, source_cfg, error_msg):
    """ Save processing errors to database. """
    if not source_cfg:
        return
    now = datetime.datetime.now()
    aconf = appconfig.AppConfig()
    source_cfg.processing = 0
    source_cfg.last_error = error_msg
    source_cfg.last_error_date = now
    source_cfg.failure_counter += 1
    max_faulures = aconf.get('sources.max_faulures')
    if max_faulures and source_cfg.failure_counter == max_faulures:
        source_cfg.enabled = False
        source_cfg.add_log('info', "Source disabled due max failures occurred")
    interval = source_cfg.interval or aconf.get('articles.update_interval', 60)
    source_cfg.next_refresh = now + datetime.timedelta(minutes=interval)
    # source_cfg.last_refreshed = now
    source_cfg.add_log("ERROR", error_msg)
    session.commit()


def _emit_updated(source_oid, group_oid, source_title, new_articles_cnt,
                  force=False):
    """ Inform application about source updates. """
    if new_articles_cnt or force:
        messenger.MESSENGER.emit_source_updated(source_oid, group_oid)
    if new_articles_cnt:
        messenger.MESSENGER.emit_announce(
            u"%s updated - %d new articles" % (source_title, new_articles_cnt))
    else:
        messenger.MESSENGER.emit_announce(u"%s updated" % source_title)


def _process_sources(update_q):
    """ Process all sources with `next_refresh` date in past """
    _LOG.debug("MainWorker: start processing")
    session = db.Session()
    now = datetime.datetime.now()
    query = session.query(DBO.Source).\
        filter(DBO.Source.enabled == 1,
               DBO.Source.next_refresh < now,
               DBO.Source.deleted == None).\
        order_by(DBO.Source.next_refresh)
    sources = [src.oid for src in query]
    session.expunge_all()
    session.close()
    new_sources = []
    if len(sources) > 0:
        sources_in_queue = update_q.get_queue()
        new_sources = [source_id for source_id in sources
                       if source_id not in sources_in_queue]
        _LOG.debug("MainWorker: processing %d sources", len(new_sources))
        if new_sources:
            for source_id in new_sources:
                update_q.put_nowait(source_id)

            messenger.MESSENGER.emit_announce(u"Starting sources update")
            messenger.MESSENGER.emit_updating_status(
                messenger.ST_UPDATE_STARTED, len(new_sources))
    _LOG.debug("MainWorker: end processing")
    return len(new_sources)


class WorkerDbCheck(threading.Thread):
    """ Worker: check sources for updating. """

    def __init__(self, update_q):
        super(WorkerDbCheck, self).__init__()
        self.daemon = True
        self.update_q = update_q
        self.command_q = multiprocessing.JoinableQueue()
        self._enable_flag = multiprocessing.Event()

    def run(self):
        _LOG.info("Starting worker")
        while True:
            try:
                cmd = self.command_q.get(True, _LONG_SLEEP)
            except Queue.Empty:
                pass
            else:
                if cmd == 'exit':
                    _LOG.debug("WorkerDbCheck.run exiting")
                    return
            if not self._enable_flag.is_set():
                _LOG.debug('WorkerDbCheck.run _enable_flag not set')
                continue
            while _process_sources(self.update_q):
                self.update_q.join()
                messenger.MESSENGER.emit_announce(u"Update finished")
                messenger.MESSENGER.emit_updating_status(
                    messenger.ST_UPDATE_FINISHED)
            _LOG.debug("WorkerDbCheck.run loop finished")

    def enable_updates(self, enable):
        """ Enable/disable thread processing """
        if enable:
            self._enable_flag.set()
        else:
            self._enable_flag.clear()


class WorkerGuiUpdate(threading.Thread):
    """ Worker: periodically check for message queue and generate
    gui-related events. """

    def __init__(self, messages_queue):
        super(WorkerGuiUpdate, self).__init__()
        self.daemon = True
        self.messages_queue = messages_queue

    def run(self):
        _LOG.info("WorkerGuiUpdate: starting")
        while True:
            cmd = self.messages_queue.get()
            if cmd is None:
                return
            _LOG.debug("WorkerGuiUpdate: cmd %r", cmd)
            cmd, args = cmd
            if cmd == 'update_finished':
                messenger.MESSENGER.emit_announce(u"Update finished")
                messenger.MESSENGER.emit_updating_status(
                    messenger.ST_UPDATE_FINISHED)
            elif cmd == 'source_update':
                _emit_updated(*args)  # pylint: disable=star-args
                messenger.MESSENGER.emit_updating_status(
                    messenger.ST_UPDATE_PING)
            elif cmd == 'source_update_error':
                _source_oid, _group_oid, source_title = args
                messenger.MESSENGER.emit_announce(
                    u"%s updated - update error" % source_title)
                messenger.MESSENGER.emit_updating_status(
                    messenger.ST_UPDATE_PING)
        _LOG.debug("WorkerGuiUpdate: exit")


class MyQueue(queues.JoinableQueue):

    def unfinished_tasks(self):
        with self._cond:
            # pylint: disable=protected-access
            return not self._unfinished_tasks._semlock._is_zero()

    def get_queue(self):
        with self._cond:
            return list(self._buffer)


class BgJobsManager(object):
    def __init__(self):
        # stop all background process
        self._src_update_wrks_terminate = multiprocessing.Event()
        self._src_update_q = MyQueue()
        self._src_update_wkrs = []
        # background worker that periodically check database for sources to
        # update and put its id to _src_update_q
        self._db_check_wkr = None
        # queue for updating gui events
        self._gui_update_q = multiprocessing.Queue()
        # worker that generating events from _gui_update_q queue
        self._gui_update_wkr = None

    def start_workers(self):
        _LOG.info("BgJobsManager.start_workers")

        self._gui_update_wkr = WorkerGuiUpdate(self._gui_update_q)
        self._gui_update_wkr.start()

        for _dummy in xrange(_WORKERS):
            wkr = Worker(self._src_update_q, self._src_update_wrks_terminate,
                         self._gui_update_q)
            wkr.daemon = True
            wkr.start()
            self._src_update_wkrs.append(wkr)

        self._db_check_wkr = WorkerDbCheck(self._src_update_q)
        self._db_check_wkr.start()

        self._db_check_wkr.enable_updates(True)
        _LOG.debug("BgJobsManager.start_workers done")

    def stop_workers(self):
        _LOG.info("BgJobsManager.stop_workers")
        self._db_check_wkr.command_q.put('exit')
        self._gui_update_q.put(None)
        self._src_update_wrks_terminate.set()
        self.empty_queue()
        self._src_update_q.close()
        time.sleep(3)
        for wkr in self._src_update_wkrs:
            if wkr.is_alive():
                wkr.terminate()
        _LOG.debug("BgJobsManager.stop_workers joining queue")
        self._src_update_q.join_thread()
        _LOG.debug("BgJobsManager.stop_workers done")

    def empty_queue(self):
        _LOG.info("BgJobsManager.empty_queue")
        try:
            while True:
                itm = self._src_update_q.get(False)
                _LOG.debug("empty_queue: found %r", itm)
                self._src_update_q.task_done()
        except Queue.Empty:
            pass
        _LOG.debug("BgJobsManager.empty_queue done")

    def is_updating(self):
        return self._src_update_q.unfinished_tasks()

    def enable_updating(self, enable):
        self._db_check_wkr.enable_updating(enable)

    def wakeup_db_check(self):
        _LOG.info("BgJobsManager.wakeup_db_check")
        if self._db_check_wkr.is_alive() and not self.is_updating() and \
                self._db_check_wkr.command_q.empty():
            self._db_check_wkr.command_q.put('start')
            _LOG.debug("BgJobsManager.wakeup_db_check thread wakeup")
        _LOG.debug("BgJobsManager.wakeup_db_check done")


BG_JOBS_MNGR = BgJobsManager()
