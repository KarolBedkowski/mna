#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


import logging
import datetime

from mna.model import db
from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


def mark_source_read(source_ids, read=True):
    """ Mark all article from source(s) read.

    Args:
        source_ids (int/[int]): one or list source id to update
        read (bool): mark articles read/unread
    Return:
        (total updated articles, map[source_id] -> number of updated articles)
    """
    if not isinstance(source_ids, (list, tuple)):
        source_ids = [source_ids]
    cnt = 0
    results = {}
    session = db.Session()
    for sid in source_ids:
        _LOG.debug("mark_source_read(%r, %r)", sid, read)
        s_cnt = db.get_all(DBO.Article, session=session,
                           source_id=sid, read=(0 if read else 1)).\
            with_lockmode('update').\
            update({'read': (1 if read else 0)})
        cnt += s_cnt
        results[sid] = s_cnt
    session.commit()
    _LOG.debug("mark_source_read -> %r", cnt)
    return cnt, results


def save_source(source):
    _LOG.info("save_source %r", source)
    db.save(source, True)
    _LOG.info("save_source done")


def delete_source(source):
    """ Delete `source`. """
    _LOG.info("delete_source %r", source)
    db.delete(source, True)
    _LOG.info("delete_source done")
    return True


def force_refresh_all():
    """ Force refresh all sources. """
    _LOG.info("Sources.force_refresh_all()")
    session = db.Session()
    session.query(DBO.Source).update({"next_refresh": datetime.datetime.now()})
    session.commit()


def get_last_article(source_id, session=None):
    """  Find last article for `source_id` """
    session = session or db.Session()
    article = session.query(DBO.Article).\
        filter(DBO.Article.source_id == source_id).\
        order_by(DBO.Article.updated.desc()).first()
    return article
