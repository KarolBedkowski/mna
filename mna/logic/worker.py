#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Worker """

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"

import logging
import datetime
import time

from PyQt4 import QtCore

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
class Worker(QtCore.QRunnable):
    """ Worker - process one source and store result in database.

    Arguments:
        source_id: source to process
    """
    def __init__(self, source_id):
        QtCore.QRunnable.__init__(self)  # pylint:disable=no-member
        self.source_id = source_id
        self.aconf = appconfig.AppConfig()
        self._p_name = "Worker: id=%d src=%d" % (id(self), source_id)

    def run(self):
        session = db.Session(autoflush=False, autocommit=False)
        source_cfg = self._get_and_check_source(session)
        if not source_cfg or source_cfg.processing:
            _LOG.warn("%s not processing %r", self._p_name, source_cfg)
            return

        _LOG.debug("%s processing %s/%s", self._p_name, source_cfg.name,
                   source_cfg.title)
        now = datetime.datetime.now()

        source_cfg.processing = 1
        session.commit()

        # find pluign
        source_cls = plugins.SOURCES.get(source_cfg.name)
        if not source_cls:
            _LOG.error("%s unknown source: %s in %r", self._p_name,
                       source_cls, source_cfg)
            source_cfg.enabled = False
            _on_error(session, source_cfg, "unknown source")
            return

        source = source_cls(source_cfg)
        cnt = 0
        aconf = self.aconf
        try:
            articles = source.get_items(
                session,
                aconf.get('articles.max_num_load', 0),
                aconf.get('articles.max_age_load', 0))
            if source_cfg.conf.get('filter.enabled', True):
                articles = self._filter_articles(articles, session, source_cfg)
            cnt = sum(_save_articls(articles, session, source_cfg))
        except base.GetArticleException, err:
            # some processing error occurred
            _LOG.exception("%s Load articles from %s/%s error: %r",
                           self._p_name, source_cfg.name, source_cfg.title,
                           err)
            _on_error(session, source_cfg, str(err))
            return
        else:
            _LOG.debug("%s Loaded %d from %s/%s", self._p_name, cnt,
                       source_cfg.name, source_cfg.title)

        # sanity check
        source_cfg = self._get_and_check_source(session)
        if not source_cfg or not source_cfg.processing:
            _LOG.warn("%s finished problem - sanity check failed: %d - %r",
                      self._p_name, self.source_id, source_cfg)
            _on_error(session, source_cfg, str(err))
            return

        source_cfg.next_refresh = now + \
                datetime.timedelta(seconds=source_cfg.interval)
        source_cfg.last_refreshed = now
        source_cfg.processing = 0

        if not source_cfg.icon_id:
            self._get_icon(source, session, source_cfg)

        session.commit()
        _emit_updated(source_cfg.oid, source_cfg.group_id, source_cfg.title,
                      cnt)
        _LOG.debug("%s finished", self._p_name)
        return

    def _get_and_check_source(self, session):
        source_cfg = db.get_one(DBO.Source, session=session,
                                oid=self.source_id)
        if not source_cfg or \
                source_cfg.next_refresh > datetime.datetime.now():
            return None
        return source_cfg

    def _load_filters(self, source_cfg, session):
        for fltr in source_cfg.get_filters():
            fltr_cls = plugins.FILTERS.get(fltr.name)
            if not fltr_cls:
                _LOG.error("%s unknown filter: %s in %r", self._p_name,
                           fltr.name, fltr.oid)
                _on_error(session, source_cfg, "unknown filter")
                return
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
    source_cfg.processing = 0
    source_cfg.last_error = error_msg
    source_cfg.last_error_date = now
    source_cfg.next_refresh = now + datetime.timedelta(
        seconds=source_cfg.interval)
    # source_cfg.last_refreshed = now
    source_cfg.add_log("ERROR", error_msg)
    session.commit()


def _emit_updated(source_oid, group_oid, source_title, new_articles_cnt):
    """ Inform application about source updates. """
    if new_articles_cnt:
        messenger.MESSENGER.emit_source_updated(source_oid, group_oid)
        messenger.MESSENGER.emit_announce(
            u"%s updated - %d new articles" %
            (source_title, new_articles_cnt))
    else:
        messenger.MESSENGER.emit_announce(u"%s updated" % source_title)


def _process_sources():
    """ Process all sources with `next_refresh` date in past """
    _LOG.debug("MainWorker: start processing")
    session = db.Session()
    now = datetime.datetime.now()
    query = session.query(DBO.Source).\
        filter(DBO.Source.enabled == 1,
               DBO.Source.next_refresh < now).\
        order_by(DBO.Source.next_refresh)
    sources = [src.oid for src in query]
    session.expunge_all()
    session.close()
    _LOG.debug("MainWorker: processing %d sources", len(sources))
    if len(sources) > 0:
        messenger.MESSENGER.emit_announce(u"Starting sources update")
        pool = QtCore.QThreadPool()  # pylint:disable=no-member
        pool.setMaxThreadCount(_WORKERS)
        for source_id in sources:
            worker = Worker(source_id)
            pool.start(worker)
        pool.waitForDone()
        messenger.MESSENGER.emit_announce(u"Update finished")
    _LOG.debug("MainWorker: processing finished")
    return 0


# pylint:disable=no-member,no-init,too-few-public-methods
class MainWorker(QtCore.QThread):
    def run(self):  # pylint:disable=no-self-use
        """ Start worker; run _process_sources in loop. """
        _LOG.info("Starting worker")
        # Random sleep before first processing
        time.sleep(_SHORT_SLEEP * 2)
        while True:
            if not _process_sources():
                # no source to process
                time.sleep(_LONG_SLEEP)
            else:
                time.sleep(_SHORT_SLEEP)
