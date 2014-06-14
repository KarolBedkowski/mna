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

import sqlalchemy
from sqlalchemy.engine import Engine

from mna.model import sqls
from mna.model import dbobjects

_LOG = logging.getLogger(__name__)


@sqlalchemy.event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
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
    args = {'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES}
    engine = sqlalchemy.create_engine("sqlite:///" + filename, echo=debug,
                                      connect_args=args, native_datetime=True)
    for schema in sqls.SCHEMA_DEF:
        for sql in schema:
            engine.execute(sql)
    dbobjects.Session.configure(bind=engine)  # pylint: disable=E1120

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
    dbobjects.Base.metadata.create_all(engine)
    _LOG.info('Database create_all COMPLETED')
    # bootstrap
    _LOG.info('Database bootstrap START')
    # session = dbobjects.Session()
    _LOG.info('Database bootstrap COMPLETED')
    return dbobjects.Session


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
