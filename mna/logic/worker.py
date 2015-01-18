#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Worker """

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"

import logging
import datetime
import time

from PyQt4 import QtCore

from mna.model import dbobjects as DBO
from mna import plugins
from mna.model import base
from mna.lib import appconfig
from mna.common import messenger

_LOG = logging.getLogger(__name__)
_LONG_SLEEP = 15  # sleep when no source processed
_SHORT_SLEEP = 1  # sleep after retrieve articles from source
_WORKERS = 3  # number of background workers


class Worker(QtCore.QRunnable):
    """ Worker - process one source and store result in database.

    Arguments:
        source_id: source to process
    """
    def __init__(self, source_id):
        QtCore.QRunnable.__init__(self)
        self.source_id = source_id

    def run(self):
        _p_name = "Worker%d" % id(self)
        session = DBO.Session()
        source_cfg = DBO.Source.get(session=session, oid=self.source_id)
        _LOG.debug("%s processing %s/%s", _p_name, source_cfg.name,
                   source_cfg.title)
        # find pluign
        source_cls = plugins.SOURCES.get(source_cfg.name)
        if not source_cls:
            _LOG.error("%s: unknown source: %s in %r", _p_name, source_cls,
                       source_cfg)
            source_cfg.enabled = False
            _on_error(session, source_cfg, "unknown source")
            return 0

        source = source_cls(source_cfg)
        cnt = 0
        aconf = appconfig.AppConfig()
        max_num_load = aconf.get('articles.max_num_load', 0)
        max_age_load = aconf.get('articles.max_age_load', 0)
        try:
            for article in source.get_items(session, max_num_load,
                                            max_age_load):
                cnt += 1
                article.source_id = source_cfg.oid
                # TODO: filtrowanie artykułów
                session.merge(article)
        except base.GetArticleException, err:
            # some processing error occurred
            _LOG.exception("%s: Load articles from %s/%s error: %r",
                           _p_name, source_cfg.name, source_cfg.title, err)
            _on_error(session, source_cfg, str(err))
            return 0
        else:
            _LOG.debug("%s: Loaded %d from %s/%s", _p_name, cnt,
                       source_cfg.name, source_cfg.title)
        now = datetime.datetime.now()
        source_cfg.next_refresh = now + \
                datetime.timedelta(seconds=source_cfg.interval)
        source_cfg.last_refreshed = now
        session.commit()
        _emit_updated(source_cfg.oid, source_cfg.group_id, source_cfg.title,
                      cnt)
        _LOG.debug("%s: finished", _p_name)


def _on_error(session, source_cfg, error_msg):
    """ Save processing errors to database. """
    if not source_cfg:
        return
    now = datetime.datetime.now()
    source_cfg.processing = False
    source_cfg.last_error = error_msg
    source_cfg.last_error_date = now
    source_cfg.next_refresh = now + datetime.timedelta(
        seconds=source_cfg.interval)
    # source_cfg.last_refreshed = now
    source_cfg.add_to_log("ERROR", error_msg)
    session.commit()


def _emit_updated(source_oid, group_oid, source_title, new_articles_cnt):
    """ Inform application about source updates. """
    if new_articles_cnt:
        messenger.MESSENGER.emit_source_updated(source_oid, group_oid)
        messenger.MESSENGER.emit_announce(u"%s updated - %d new articles" %
                                        (source_title, new_articles_cnt))
    else:
        messenger.MESSENGER.emit_announce(u"%s updated" % source_title)


def _process_sources():
    """ Process all sources with `next_refresh` date in past """
    _LOG.debug("MainWorker: start processing")
    session = DBO.Session()
    now = datetime.datetime.now()
    query = session.query(DBO.Source)
    query = query.filter(DBO.Source.enabled == 1,
                         DBO.Source.next_refresh < now)
    query = query.order_by(DBO.Source.next_refresh)
    sources = [src.oid for src in query]
    session.expunge_all()
    session.close()
    _LOG.debug("MainWorker: processing %d sources", len(sources))
    if len(sources) > 0:
        messenger.MESSENGER.emit_announce(u"Starting sources update")
        pool = QtCore.QThreadPool()
        pool.setMaxThreadCount(_WORKERS)
        for source_id in sources:
            worker = Worker(source_id)
            pool.start(worker)
        pool.waitForDone()
        messenger.MESSENGER.emit_announce(u"Update finished")
    _LOG.debug("MainWorker: processing finished")
    return 0


class MainWorker(QtCore.QThread):
    def run(self):
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
