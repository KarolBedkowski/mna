#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Worker """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"

import logging
import datetime
import multiprocessing
import time
import random

from mna.model import dbobjects as DBO
from mna import plugins


_LOG = logging.getLogger(__name__)
_LONG_SLEEP = 15  # sleep when no source processed
_SHORT_SLEEP = 1  # sleep after retrieve articles from source
_WORKERS = 2  # number of background workers


def worker(task):
    """ Worker - process one source.

    :param task: source to process
    :return: number of loaded article."""
    _p_name = multiprocessing.current_process().name
    session = DBO.Session()
    source_cfg = session.merge(task)
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
    try:
        for article in source.get_items():
            cnt += 1
            article.source_id = source_cfg.oid
            session.add(article)
    except plugins.GetArticleException, err:
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
    _LOG.debug("%s: finished", _p_name)
    return cnt


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
    source_cfg.last_refreshed = now
    session.commit()


def _process_sources():
    """ Process all sources with next_refresh date in past """
    _LOG.info("MainWorker: start processing")
    session = DBO.Session()
    now = datetime.datetime.now()
    query = session.query(DBO.Source)
    query = query.filter(DBO.Source.enabled == 1,
                         DBO.Source.next_refresh < now)
    query = query.order_by(DBO.Source.next_refresh)
    tasks = list(query)
    session.flush()
    _LOG.debug("MainWorker: processing %d sources", len(tasks))
    loaded_articles = 0
    if len(tasks) > 0:
        pool = multiprocessing.Pool(processes=_WORKERS)
        loaded_articles = sum(pool.map(worker, tasks))
        pool.close()
    _LOG.debug("MainWorker: processing finished; loaded %d articles",
               loaded_articles)
    return loaded_articles > 0


class MainWorker(multiprocessing.Process):
    def run(self):
        """ Start worker; run _process_sources in loop. """
        _LOG.info("Starting worker %s", self.name)
        # Random sleep before first processing
        time.sleep(random.randrange(_LONG_SLEEP, _LONG_SLEEP * 2))
        while True:
            if not _process_sources():
                # no task to process
                time.sleep(_LONG_SLEEP)
            else:
                time.sleep(_SHORT_SLEEP)
