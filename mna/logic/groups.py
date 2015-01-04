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


def add_group(name):
    """ Add new group with `name`.

    :return: DBO.Group object if success."""
    # TODO check name uniques
    group = DBO.Group()
    group.name = name
    group.save(True)
    return group


def save_group(group):
    """ Save new or updated `group`. """
    _LOG.info("save_group %r", group)
    # check for dupilcate name
    session = DBO.Session()
    tmp_group = DBO.Group.get(session=session, name=group.name)
    print repr(tmp_group)
    if tmp_group and tmp_group.oid != group.oid:
        raise GroupSaveError("duplicated name")
    group.save(commit=True, session=session)
    _LOG.info("save_group done")
