#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


import logging
import datetime

from sqlalchemy import func

from mna.model import dbobjects as DBO
from mna.lib import appconfig


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
    _LOG.info("save_source done")


def delete_source(source):
    """ Delete `source`. """
    _LOG.info("delete_source %r", source)
    source.delete(True)
    _LOG.info("delete_source done")
    return True


def delete_old_articles():
    """ Find and delete old articles for all sources.
    Source can have own configuration (num_articles_to_keep > 0,
    age_articles_to_keep > 0), use app defaults (=0) or keep all articles (-1,
    or delete_old_articles=False).
    """
    _LOG.info("delete_old_articles START")
    session = DBO.Session()
    # globals settings
    appconf = appconfig.AppConfig()
    delete_articles = appconf.get('articles.delete_old', False)
    # delete by age
    del_older = appconf.get('articles.keep_older', -1) if delete_articles \
            else -1
    srcs = session.query(DBO.Source). \
            filter(DBO.Source.delete_old_articles == 1)
    if del_older > -1:
        # also with default setting
        srcs = srcs.filter(DBO.Source.age_articles_to_keep > -1)
    else:
        # no defaults settings
        srcs = srcs.filter(DBO.Source.age_articles_to_keep > 0)

    for src in srcs:
        keep = src.age_articles_to_keep or del_older
        del_date = datetime.datetime.now() - datetime.timedelta(days=keep)
        arts = session.query(DBO.Article).\
                filter(DBO.Article.source_id == src.oid,
                       DBO.Article.updated < del_date)
        num_deleted = arts.delete()
        _LOG.debug("delete_old_articles: %d deleted by age for (%r, %r)",
                   num_deleted, src.oid, src.title)
    # delete by number
    keep_num = appconf.get('articles.keep_num', -1) if delete_articles else -1
    srcs = session.query(DBO.Source). \
            filter(DBO.Source.delete_old_articles == 1)
    if keep_num > -1:
        # also with default setting
        srcs = srcs.filter(DBO.Source.num_articles_to_keep > -1)
    else:
        # no defaults settings
        srcs = srcs.filter(DBO.Source.num_articles_to_keep > 0)

    for src in srcs:
        keep = src.num_articles_to_keep or keep_num
        sel_min_stmt = session.query(DBO.Article.oid).\
                filter(DBO.Article.source_id == src.oid).\
                order_by(DBO.Article.updated.desc()).\
                limit(keep).subquery()
        min_oid = session.query(func.min(sel_min_stmt.c.oid)).\
                scalar()
        if min_oid > 0:
            arts = session.query(DBO.Article).\
                    filter(DBO.Article.source_id == src.oid,
                           DBO.Article.oid < min_oid)
            num_deleted = arts.delete()
            _LOG.debug("delete_old_articles: %d deleted by num for (%r, %r)",
                       num_deleted, src.oid, src.title)

    session.commit()
    _LOG.info("delete_old_articles FINISHED")
