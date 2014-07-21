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


class AbstractSource(object):
    """Basic source"""

    name = "dummy"

    def __init__(self, cfg):
        super(AbstractSource, self).__init__()
        # configuration
        self.cfg = cfg

    def get_items(self):
        return []

    def format_item_for_view(self, item):
        return str(item)

    @classmethod
    def get_params(cls):
        return {}


class AbstractFilter(object):
    """Basic Filter object"""

    name = "dummy"

    def __init__(self, cfg):
        super(AbstractFilter, self).__init__()
        # configuration
        self.cfg = cfg

    def filter(self, article):
        """ Process article by filter """
        return article
