#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Standard paths.

Copyright (c) Karol Będkowski, 2004-2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-14"


from mna import version

LINUX_LOCALES_DIR = 'share/locale'
LINUX_INSTALL_DIR = 'share/%s' % version.SHORTNAME
LINUX_DOC_DIR = 'share/doc/%s' % version.SHORTNAME
LINUX_DATA_DIR = 'share/%s/data' % version.SHORTNAME


LOCALES_DIR = './locale'
DATA_DIR = './data'
