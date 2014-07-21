#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


from mna.model import dbobjects as DBO


def add_source(clazz, params):
    """ Add new source.

    :param clazz: source class to add
    :param params: dictionary of params.
    :return: DBO.Group object if success."""
    # TODO check name uniques
    group = DBO.Group()
    group.name = n
    group.save(True)
    return group
