#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


import logging

from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


def add_source(clazz, params):
    """ Add new source.

    :param clazz: source class to add
    :param params: dictionary of params.
    :return: DBO.Group object if success."""
    # TODO check name uniques
    group = DBO.Group()
    group.name = params.get('name')
    group.save(True)
    return group


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
    session = DBO.Session()
    for sid in source_ids:
        _LOG.debug("mark_source_read(%r, %r)", sid, read)
        s_cnt = session.query(DBO.Article).\
                filter(DBO.Article.source_id == sid,
                       DBO.Article.read == (0 if read else 1)).\
                update({'read': (1 if read else 0)})
        cnt += s_cnt
        results[sid] = s_cnt
    session.commit()
    _LOG.debug("mark_source_read -> %r", cnt)
    return cnt, results


def save_source(source):
    _LOG.info("save_source %r", source)
    source.save(True)
