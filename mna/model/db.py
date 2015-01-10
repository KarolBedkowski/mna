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
from sqlalchemy.pool import SingletonThreadPool

from mna.model import sqls
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


@sqlalchemy.event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
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
                                      isolation_level='SERIALIZABLE',
                                      # poolclass=SingletonThreadPool
                                      )
    for schema in sqls.SCHEMA_DEF:
        for sql in schema:
            engine.execute(sql)
    DBO.Session.configure(bind=engine)  # pylint: disable=E1120

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
    session = DBO.Session()
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
    print freelist_count, page_count
    if freelist_count > 0.20 * page_count:
        _LOG.debug('Database vacuum')
        session.execute('PRAGMA incremental_vacuum(%d)' % (freelist_count / 2))
    _LOG.info('Database cleanup COMPLETED')
    return DBO.Session


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
    if DBO.Group.count() == 0:
        # create default group
        group = DBO.Group()
        group.name = "Default Group"
        session.add(group)
        group = DBO.Group()
        group.name = "OSS"
        session.add(group)
    if DBO.Actions.count() == 0:
        # create empty action
        action = DBO.Actions()
        action.name = "No actions"
        session.add(action)
    if DBO.Source.count() == 0:
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
