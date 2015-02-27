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
