#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=W0105

""" SqlAlchemy objects definition.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""
__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-12"


class BaseSource(object):
    """Basic source"""

    name = "dummy"

    def __init__(self):
        super(BaseSource, self).__init__()
        self.oid = None
        self.last_refreshed = None
        self.initial_score = 0
        self.group_id = None
        self.enabled = True

    def get_items(self):
        return []


class BaseFilter(object):
    """Basic Filter object"""

    name = "dummy"

    def __init__(self):
        super(BaseFilter, self).__init__()
        self.enabled = True

    def filter(self, article):
        """ Process article by filter """
        return article