#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=W0105

""" Files repository.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""
__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-02-11"


import os
import logging

from mna.lib import singleton

_LOG = logging.getLogger(__name__)


class Reporitory(singleton.Singleton):
    def _init(self):
        self._path = None

    def setup(self, path):
        self._path = path

    def get_file(self, fid):
        with open(os.path.join(self._path, fid), 'rb') as fle:
            return fle.read()

    def store_file(self, fid, content):
        with open(os.path.join(self._path, fid), 'wb') as fle:
            fle.write(content)
