#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"


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


def delete_source(source_oid):
    """ Delete `source`. """
    _LOG.info("delete_source %r", source_oid)
    source = db.get_one(DBO.Source, oid=source_oid)
    if source:
        db.delete(source, True)
    _LOG.info("delete_source done")
    return True


def force_refresh_all():
    """ Force refresh all sources. """
    _LOG.info("Sources.force_refresh_all()")
    session = db.Session()
    session.query(DBO.Source).\
        filter_by(processing=0).\
        update({"next_refresh": datetime.datetime.now()})
    session.commit()


def force_refresh(source_oid):
    _LOG.info("Sources.force_refresh(%r)", source_oid)
    session = db.Session()
    session.query(DBO.Source).\
        filter_by(oid=source_oid, processing=0).\
        update({"next_refresh": datetime.datetime.now()})
    session.commit()


def force_refresh_by_group(group_oid):
    _LOG.info("Sources.force_refresh_by_group(%r)", group_oid)
    session = db.Session()
    session.query(DBO.Source).\
        filter_by(group_id=group_oid, processing=0).\
        update({"next_refresh": datetime.datetime.now()})
    session.commit()


def get_source_info(session, source_oid):
    """ Get title, unread count and icon_id for source. """
    session = session or db.Session()
    title, unread, icon_id = \
        session.query(DBO.Source.title, DBO.Source.unread,
                      DBO.Source.icon_id).\
        filter(DBO.Source.oid == source_oid).first()
    return title, unread, icon_id
