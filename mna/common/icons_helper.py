# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
""" Icons helper - retrieving and caching.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-02-15"


import os.path
import logging

from PyQt4 import QtGui

from mna.lib import appconfig

_LOG = logging.getLogger(__name__)
_ICON_CACHE = {}


def load_icon(icon_name):
    icon = None
    if icon_name:
        if icon_name in _ICON_CACHE:
            return _ICON_CACHE[icon_name]
        if icon_name[0] == ':':  # resources
            icon = QtGui.QIcon(icon_name)  # pylint:disable=no-member
        elif os.path.isabs(icon_name):
            icon = QtGui.QIcon(icon_name)  # pylint:disable=no-member
        else:
            fname = appconfig.AppConfig().get_cache_file(icon_name)
            if fname:
                icon = QtGui.QIcon(fname)  # pylint:disable=no-member
        if icon:
            _ICON_CACHE[icon_name] = icon
    # pylint:disable=no-member
    return icon or QtGui.QIcon(":icons/unknown-icon.svg")
