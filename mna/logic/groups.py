#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Groups logick """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"

import logging

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
    session = DBO.Session()
    if group.oid:
        # find groups with this same name
        tmp_group = DBO.Group.get(session=session, name=group.name)
        if tmp_group and tmp_group.oid != group.oid:
            _LOG.info("save_group: group with name %r already exists, oid: %d",
                      group.name, tmp_group.oid)
            raise GroupSaveError("duplicated name")
    group.save(commit=True, session=session)
    _LOG.info("save_group done")


def delete_group(group):
    """ Delete `group`. """
    assert isinstance(group, DBO.Group), "Invalid function argument %r" % group
    _LOG.info("delete_group %r", group)
    group.delete(True)
    _LOG.info("delete_group done")
    return True
