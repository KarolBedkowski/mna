#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Groups logick """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"

import logging

from sqlalchemy import orm

from mna.model import db
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


class GroupSaveError(RuntimeError):
    pass


def save_group(group):
    """ Save new or updated `group`.
    Checking uniques of group name.
    """
    assert isinstance(group, DBO.Group), "Invalid function argument %r" % group
    _LOG.info("save_group %r", group)
    # check for dupilcate name
    session = db.Session()
    if group.oid:
        # find groups with this same name
        tmp_group = db.get_one(DBO.Group, session=session, name=group.name)
        if tmp_group and tmp_group.oid != group.oid:
            _LOG.info("save_group: group with name %r already exists, oid: %d",
                      group.name, tmp_group.oid)
            raise GroupSaveError("duplicated name")
    db.save(group, commit=True, session=session)
    _LOG.info("save_group done")


def delete_group(group_oid):
    """ Delete `group`. """
    _LOG.info("delete_group %r", group_oid)
    group = db.get_one(DBO.Group, oid=group_oid)
    db.delete(group, True)
    _LOG.info("delete_group done")
    return True


def get_group_sources_tree(session):
    res = session.query(DBO.Group).join(DBO.Source).order_by(DBO.Group.name)
    return res
