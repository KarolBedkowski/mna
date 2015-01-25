# -*- coding: utf-8 -*-

""" Database functions.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-12"


import os
import time
import sqlite3
import logging
import datetime

import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy import orm, or_
# from sqlalchemy.pool import SingletonThreadPool

from mna.model import sqls
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)
Session = orm.sessionmaker()  # pylint: disable=C0103


def text_factory(text):
    return unicode(text, 'utf-8', errors='replace')


@sqlalchemy.event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    dbapi_connection.text_factory = text_factory
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA auto_vacuum=INCREMENTAL")
    cursor.close()


def connect(filename, debug=False, *args, **kwargs):
    """ Create connection  to database  & initiate it.

    Args:
        filename: path to sqlite database file
        debug: (bool) turn on  debugging
        args, kwargs: other arguments for sqlalachemy engine

    Return:
        Sqlalchemy Session class
    """
    _LOG.info('connect %r', (filename, args, kwargs))
    args = {'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            'check_same_thread': False}

    engine = sqlalchemy.create_engine("sqlite:///" + filename,
                                      echo=False,
                                      connect_args=args,
                                      native_datetime=True,
                                      isolation_level='SERIALIZABLE')
    for schema in sqls.SCHEMA_DEF:
        for sql in schema:
            engine.execute(sql)
    Session.configure(bind=engine)  # pylint: disable=E1120

    if debug:
        @sqlalchemy.event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(_conn, _cursor,  # pylint: disable=W0612
                                  _stmt, _params, context, _executemany):
            context.app_query_start = time.time()

        @sqlalchemy.event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(_conn, _cursor,  # pylint: disable=W0612
                                 _stmt, _params, context, _executemany):
            _LOG.debug("Query time: %.02fms",
                       (time.time() - context.app_query_start) * 1000)

    _LOG.info('Database create_all START')
    DBO.Base.metadata.create_all(engine)
    _LOG.info('Database create_all COMPLETED')
    # bootstrap
    _LOG.info('Database bootstrap START')
    session = Session()
    _bootstrap_data(session)
    session.commit()
    _LOG.info('Database bootstrap COMPLETED')
    _LOG.info('Database cleanup START')
    # remove processing tag
    session.query(DBO.Source).filter(DBO.Source.processing == 1).\
            update({"processing": False})
    # delete old logs
    log_del_date = datetime.datetime.now() - datetime.timedelta(days=90)
    session.query(DBO.SourceLog).filter(DBO.SourceLog.date < log_del_date).\
            delete()
    session.commit()

    freelist_count = session.execute("PRAGMA freelist_count").fetchone()[0]
    page_count = session.execute("PRAGMA page_count").fetchone()[0]
    if freelist_count > 0.20 * page_count:
        _LOG.debug('Database vacuum')
        session.execute('PRAGMA incremental_vacuum(%d)' % (freelist_count / 2))
    _LOG.info('Database cleanup COMPLETED')
    return Session


def find_db_file(config):
    """ Find existing database file. """

    def _try_path(path):
        """ Check if in given path exists mna.db file. """
        file_path = os.path.join(path, 'mna.db')
        if os.path.isfile(file_path):
            return file_path
        return None

    db_filename = _try_path(config.main_dir)
    if not db_filename:
        db_filename = _try_path(os.path.join(config.main_dir, 'db'))
    if not db_filename:
        db_dir = os.path.join(config.main_dir, 'db')
        if os.path.isdir(db_dir):
            db_filename = os.path.join(db_dir, 'mna.db')
    if not db_filename:
        db_filename = os.path.join(config.user_share_dir, 'mna.db')
    #  create dir for database if not exist
    db_dirname = os.path.dirname(db_filename)
    if not os.path.isdir(db_dirname):
        os.mkdir(db_dirname)
    return db_filename


def _bootstrap_data(session):
    if count(DBO.Group) == 0:
        # create default group
        group = DBO.Group()
        group.name = "Default Group"
        session.add(group)
        group = DBO.Group()
        group.name = "OSS"
        session.add(group)
    if count(DBO.Source) == 0:
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "Filmweb"
        source.conf = {"url": r'http://www.filmweb.pl/rss/news'}
        source.group_id = 1
        session.add(source)
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "Lifehacker"
        source.conf = {"url": r'http://lifehacker.com/index.xml'}
        source.group_id = 1
        session.add(source)
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "New Scientist"
        source.conf = {"url": r'http://feeds.newscientist.com/science-news'}
        source.group_id = 1
        session.add(source)
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "Make"
        source.conf = {"url": r'http://feeds.feedburner.com/makezineonline'}
        source.group_id = 1
        session.add(source)
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "Cnet"
        source.conf = {"url": r'http://www.cnet.com/rss/all/'}
        source.group_id = 1
        session.add(source)
        source = DBO.Source()
        source.name = "mna.plugins.rss.RssSource"
        source.title = "LinuxToday"
        source.conf = {"url": r'http://linuxtoday.com/backend/biglt.rss'}
        source.group_id = 2
        session.add(source)


def get_one(clazz, session=None, **kwargs):
    """ Get one object with given attributes.

    Args:
        session: optional sqlalchemy session
        kwargs: query filters.

    Return:
        One object.
    """
    return (session or Session()).query(clazz).filter_by(**kwargs).first()


def get_all(clazz, order_by=None, session=None):
    """ Return all objects this class.

    Args:
        order_by: optional order_by query argument
    """
    session = session or Session()
    query = session.query(clazz)
    if hasattr(clazz, 'deleted'):
        query = query.filter(clazz.deleted.is_(None))
    if order_by:
        query = query.order_by(order_by)
    return query  # pylint: disable=E1101


def count(clazz, session=None, **kwargs):
    """ Count objects with given attributes.

    Args:
        session: optional sqlalchemy session
        kwargs: query filters.

    Return:
        One object.
    """
    return (session or Session()).query(clazz).filter_by(**kwargs).count()


def save(obj, commit=False, session=None):
    """ Save object into database. """
    if session:
        session.merge(obj)
    else:
        session = Session.object_session(obj) or Session()
        session.add(obj)
    if commit:
        session.commit()
    return session


def delete(obj, commit=False, session=None):
    """ Delete object from database. """
    if session:
        session.merge(obj)
    else:
        session = Session.object_session(obj) or Session()
        session.delete(obj)
    if commit:
        session.commit()


def add_to_log(source, category, message, commit=False):
    session = Session.object_session(source)
    log = DBO.SourceLog()
    log.source_id = source.oid
    log.category = category
    log.message = message
    session.add(log)
    if commit:
        session.commit()


def get_source_logs(source):
    """  Find logs for source """
    session = Session.object_session(source) or Session()
    article = session.query(DBO.SourceLog).\
        filter(DBO.SourceLog.source_id == source.oid).\
        order_by(DBO.SourceLog.date.desc()).all()
    return article


def get_filters(source):
    """  Find all (globals/locals) filters for source """
    session = Session.object_session(source) or Session()
    fltrs = session.query(DBO.Filter)
    if source.conf.get('filter.apply_global', True):
        fltrs = fltrs.filter(or_(DBO.Filter.source_id == source.oid,
                                 DBO.Filter.source_id == None))
    else:
        fltrs = fltrs.filter(DBO.Filter.source_id == source.oid)
    return fltrs
