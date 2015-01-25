#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


import logging

from mna.model import db
from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


def get_articles_by_group(group_oid, unread_only=False, sorting=None):
    """ Get list articles for all sources in current group.

    Args:
        group_oid (int/long): id group of sources
        unread_only (bool): filter articles by read flag
        sorting (str): name of column to sort; default - "updated"

    Return:
        list of Article objects
    """
    _LOG.debug('get_articles_by_group(%r, %r, %r)', group_oid, unread_only,
               sorting)
    assert isinstance(group_oid, (int, long)), "Invalid argument"
    session = db.Session()
    articles = session.query(DBO.Article).\
                join(DBO.Article.source).\
                filter(DBO.Source.group_id == group_oid)
    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)


def get_articles_by_source(source_oid, unread_only=False, sorting=None):
    """ Get list articles for source. If `unread_only` filter articles by
        `read` flag.

    Args:
        source_oid (int/long): id group
        unread_only (bool): filter articles by read flag
        sorting (str): name of column to sort; default - "updated"

    Return:
        list of Article objects
    """
    _LOG.debug('get_articles_by_source(%r, %r, %r)', source_oid, unread_only,
               sorting)
    assert isinstance(source_oid, (int, long)), "Invalid argument"
    session = db.Session()
    articles = session.query(DBO.Article).\
        filter(DBO.Article.source_id == source_oid)
    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)
