#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Database  objects definition.

Copyright (c) Karol Będkowski, 2014

This file is part of  mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-12"

import logging

_LOG = logging.getLogger(__name__)

SCHEMA_DEF = [[
    "PRAGMA foreign_keys=ON",
    "PRAGMA auto_vacuum=INCREMENTAL"
]]


def add_icon_id(engine):
    """ Add icon_id to Source """
    res = engine.execute("select sql from sqlite_master where name='sources'")
    rows = res.fetchall()
    if not rows:
        return
    if 'icon_id' in rows[0][0]:
        return
    engine.execute('alter table sources add column icon_id varchar(64)')


def add_source_conf_updated(engine):
    """ Add conf_updated to Source """
    res = engine.execute("select sql from sqlite_master where name='sources'")
    row = res.fetchone()
    if not row or 'conf_updated' in row[0]:
        return
    engine.execute('alter table sources add column conf_updated datetime')


def _schema_update_2(engine):
    engine.execute('alter table sources add column deleted datetime')
    engine.execute('alter table sources add column failure_counter integer '
                   'default 0')


_SCHEMA_UPDATES = {
    2: _schema_update_2,
}


def update_schema(engine, current_schema_ver):
    res = engine.execute(
        "select value from app_meta where key='schema_version'")
    row = res.fetchone()
    if not row:
        return
    schema_version = int(row[0])
    if schema_version == current_schema_ver:
        return
    if schema_version > current_schema_ver:
        _LOG.warn("update_schema db schema (%d) > app schema (%d)",
                  schema_version, current_schema_ver)
        return
    _LOG.debug("update_schema %d -> %d", schema_version, current_schema_ver)
    for sver in xrange(schema_version + 1, current_schema_ver + 1):
        func = _SCHEMA_UPDATES.get(sver)
        if func:
            _LOG.debug("update_schema %d", sver)
            func(engine)
    engine.execute("update app_meta set value=? where key='schema_version'",
                   (current_schema_ver, ))
