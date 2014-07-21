#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Groups logick """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


from mna.model import dbobjects as DBO


def add_group(name):
    """ Add new group with `name`.

    :return: DBO.Group object if success."""
    # TODO check name uniques
    group = DBO.Group()
    group.name = name
    group.save(True)
    return group
