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


def worker(queue, name):
    """ One worker run. """
    while True:
        task = queue.get()
        if not task:
            queue.task_done()
            return
        # find configuration
        session = DBO.Session()
        source_cfg = session.merge(task)
        _LOG.debug("Worker %s processing %s/%s", name, source_cfg.name,
                   source_cfg.title)
        # find pluign
        source_cls = plugins.SOURCES.get(source_cfg.name)
        if not source_cls:
            _LOG.error("Worker: unknown source: %s in %r", source_cls,
                       source_cfg)
            source_cfg.enabled = False
            _on_error(session, source_cfg, "unknown source")
            queue.task_done()
            continue
        source = source_cls(source_cfg)
        cnt = 0
        for article in source.get_items():
            cnt += 1
            article.source_id = source_cfg.oid
            session.add(article)
        _LOG.debug("Worker %s loaded %d from %s/%s", name, cnt,
                   source_cfg.name, source_cfg.title)
        source_cfg.processing = False
        now = datetime.datetime.now()
        source_cfg.next_refresh = now + \
                datetime.timedelta(seconds=source_cfg.interval)
        source_cfg.last_refreshed = now
        session.commit()
        queue.task_done()


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


class MainWorker(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        super(MainWorker, self).__init__(*args, **kwargs)
        self.queue = multiprocessing.JoinableQueue()
        workers = [multiprocessing.Process(target=worker,
                                           args=(self.queue, "worker-%d" % idx))
                   for idx in xrange(_WORKERS)]
        for wkr in workers:
            wkr.daemon = True
            wkr.start()

    def _process(self):
        print '_process start'
        session = DBO.Session()
        now = datetime.datetime.now()
        query = session.query(DBO.Source)
        query = query.filter(DBO.Source.enabled == 1,
                             DBO.Source.next_refresh < now,
                             DBO.Source.processing == 0)
        query = query.order_by(DBO.Source.next_refresh)
        for source_cfg in query:
            self.queue.put(source_cfg)
        session.commit()
        print '_processing: ', self.queue.qsize()
        self.queue.join()
        print '_process end'

    def run(self):
        """ Start worker; run Worker.process in loop. """
        _LOG.info("Starting worker %s", self.name)
        time.sleep(random.randrange(_LONG_SLEEP, _LONG_SLEEP * 2))
        while True:
            if not self._process():
                time.sleep(_LONG_SLEEP)
            else:
                time.sleep(_SHORT_SLEEP)


def start_workers():
    """Start all background workers"""
    main_worker = MainWorker()
    main_worker.start()
#    worker = Worker(name="worker-1")
#    worker.run()
