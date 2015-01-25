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


def get_articles_by_group(group, unread_only=False, sorting=None):
    """ Get list articles for all sources in current group.

    Args:
        unread_only (bool): filter articles by read flag
        sorting (str): name of column to sort; default - "updated"

    Return:
        list of Article objects
    """
    if isinstance(group, DBO.Group):
        session = db.Session.object_session(group) or db.Session()
        articles = session.query(DBO.Article).\
                    join(DBO.Article.source).\
                    filter(DBO.Source.group_id == group.oid)
    elif isinstance(group, (int, long)):
        session = db.Session()
        articles = session.query(DBO.Article).\
                    join(DBO.Article.source).\
                    filter(DBO.Source.group_id == group)
    else:
        raise RuntimeError("Invalid argument: group=%r" % group)

    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)


def get_articles_by_source(source, unread_only=False, sorting=None):
    """ Get list articles for source. If `unread_only` filter articles by
        `read` flag.
    """
    if isinstance(source, DBO.Source):
        session = db.Session.object_session(source) or db.Session()
        articles = session.query(DBO.Article).\
                    filter(DBO.Article.source_id == source.oid)
    elif isinstance(source, (int, long)):
        session = db.Session()
        articles = session.query(DBO.Article).\
                    filter(DBO.Article.source_id == source)
    else:
        raise RuntimeError("Invalid argument: source=%r" % source)

    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)
