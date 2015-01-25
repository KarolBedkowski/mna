#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Articles logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2014-06-15"


import logging
import datetime

from sqlalchemy import func, orm

from mna.lib import appconfig
from mna.model import db
from mna.model import dbobjects as DBO
from mna import plugins


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


def get_all_articles(unread_only=False, sorting=None):
    """ Get list of all articles for source. If `unread_only` filter articles by
        `read` flag.

    Args:
        unread_only (bool): filter articles by read flag
        sorting (str): name of column to sort; default - "updated"

    Return:
        list of Article objects
    """
    _LOG.debug('get_all_articles(%r, %r)', unread_only, sorting)
    session = db.Session()
    articles = session.query(DBO.Article)
    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)


def get_starred_articles(unread_only=False, sorting=None):
    """ Get list of starred articles for source. If `unread_only` filter
    articles by `read` flag.

    Args:
        unread_only (bool): filter articles by read flag
        sorting (str): name of column to sort; default - "updated"

    Return:
        list of Article objects
    """
    _LOG.debug('get_starred_articles(%r, %r)', unread_only, sorting)
    session = db.Session()
    articles = session.query(DBO.Article).filter(DBO.Article.starred == 1)
    if unread_only:
        articles = articles.filter(DBO.Article.read == 0)
    if sorting:
        articles = articles.order_by(sorting)
    else:
        articles = articles.order_by("updated")
    return list(articles)


def delete_old_articles():
    """ Find and delete old articles for all sources.
    Source can have own configuration (num_articles_to_keep > 0,
    age_articles_to_keep > 0), use app defaults (=0) or keep all articles (-1,
    or delete_old_articles=False).
    """
    _LOG.info("delete_old_articles START")
    session = db.Session()
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
                       DBO.Article.updated < del_date,
                       DBO.Article.starred == 0)
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
        min_oid = session.query(func.min(sel_min_stmt.c.oid)).scalar()
        if min_oid > 0:
            arts = session.query(DBO.Article).\
                    filter(DBO.Article.source_id == src.oid,
                           DBO.Article.oid < min_oid,
                           DBO.Article.starred == 0)
            num_deleted = arts.delete()
            _LOG.debug("delete_old_articles: %d deleted by num for (%r, %r)",
                       num_deleted, src.oid, src.title)

    session.commit()
    _LOG.info("delete_old_articles FINISHED")


def toggle_articles_read(articles_oid):
    """ Toggle given by `articles_oid`  articles read flag.
    Generate changed `Article` object.
    """
    sess = db.Session()
    # get status of first articles
    art1 = db.get_one(DBO.Article, session=sess, oid=articles_oid[0])
    read = art1.read = not art1.read
    yield art1
    for art_oid in articles_oid[1:]:
        art = db.get_one(DBO.Article, session=sess, oid=art_oid)
        if art.read != read:
            art.read = read
            yield art

    sess.commit()


def toggle_articles_starred(articles_oid):
    """ Toggle given by `articles_oid`  articles starred flag.
    Generate changed `Article` object.
    """
    sess = db.Session()
    # get status of first articles
    art1 = db.get_one(DBO.Article, session=sess, oid=articles_oid[0])
    starred = art1.starred = not art1.starred
    yield art1
    for art_oid in articles_oid[1:]:
        art = db.get_one(DBO.Article, session=sess, oid=art_oid)
        if art.starred != starred:
            art.starred = starred
            yield art

    sess.commit()


_LAST_PRESENTER = {'source_id': None, 'presenter': None}


def get_article_content(article_oid, mark_read=True, session=None):
    """ Get article and formated by presenter article.

    Args:
        article_oid (long): id article to load
        mark_read (bool): mark article as read
        session (SqlAlchemy Session): optional session
    Return:
        (article, content as html)
    """
    session = session or db.Session()
    article = session.query(DBO.Article).\
        options(orm.undefer("content"),
                orm.joinedload(DBO.Article.source)).\
        filter_by(oid=article_oid).first()
    if _LAST_PRESENTER['source_id'] == article.source_id:
        presenter = _LAST_PRESENTER['presenter']
    else:
        source_cfg = article.source
        source = plugins.SOURCES.get(source_cfg.name)
        presenter = source.presenter(source)
        _LAST_PRESENTER['source_id'] = article.source_id
        _LAST_PRESENTER['presenter'] = presenter
    content = presenter.to_gui(article)
    if mark_read:
        article.read = 1
        db.save(article, True)
    return article, content
