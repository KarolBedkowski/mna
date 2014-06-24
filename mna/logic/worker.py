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
_LONG_SLEEP = 2  # sleep when no source processed
_SHORT_SLEEP = 0.5  # sleep after retrieve articles from source
_WORKERS = 2  # number of background workers
_DB_LOCK = multiprocessing.Lock()


class Worker(multiprocessing.Process):
    """Worker process source and write articles to database. """

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.enabled = True

    def process(self):
        """ One worker run. """
        if not self.enabled:
            return False
        # find configuration
        session = DBO.Session()
        now = datetime.datetime.now()
        query = session.query(DBO.Source)
        query = query.filter(DBO.Source.enabled == 1,
                             DBO.Source.next_refresh < now,
                             DBO.Source.processing == 0)
        query = query.order_by(DBO.Source.next_refresh)
        with _DB_LOCK:
            source_cfg = query.first()
            if not source_cfg:
                _LOG.debug("Worker %s no sources", self.name)
                return False
            # mark as busy
            source_cfg.processing = True
            session.commit()
        _LOG.debug("Worker %s processing %s/%s", self.name, source_cfg.name,
                   source_cfg.title)
        # find pluign
        source_cls = plugins.SOURCES.get(source_cfg.name)
        if not source_cls:
            _LOG.error("Worker: unknown source: %s in %r", source_cls,
                       source_cfg)
            source_cfg.enabled = False
            _on_error(session, source_cfg, "unknown source")
            return False
        source = source_cls(source_cfg)
        cnt = 0
        for cnt, article in enumerate(source.get_items()):
            article.source_id = source_cfg.oid
            session.add(article)
        _LOG.debug("Worker %s loaded %d from %s/%s", self.name, cnt,
                   source_cfg.name, source_cfg.title)
        source_cfg.processing = False
        now = datetime.datetime.now()
        source_cfg.next_refresh = now + \
                datetime.timedelta(seconds=source_cfg.interval)
        source_cfg.last_refreshed = now
        session.commit()
        return True

    def run(self):
        """ Start worker; run Worker.process in loop. """
        _LOG.info("Starting worker %s", self.name)
        time.sleep(random.randrange(_LONG_SLEEP, _LONG_SLEEP * 2))
        while self.enabled:
            if not self.process():
                time.sleep(_LONG_SLEEP)
            else:
                time.sleep(_SHORT_SLEEP)


def _on_error(session, source_cfg, error_msg):
    if source_cfg:
        now = datetime.datetime.now()
        source_cfg.processing = False
        source_cfg.last_error = error_msg
        source_cfg.last_error_date = now
        source_cfg.next_refresh = now + datetime.timedelta(
            seconds=source_cfg.interval)
        source_cfg.last_refreshed = now
        session.commit()


def start_workers():
    """Start all background workers"""
    workers = [Worker(name="worker-%d" % idx) for idx in xrange(_WORKERS)]
    for worker in workers:
        worker.start()
#    worker = Worker(name="worker-1")
#    worker.run()
