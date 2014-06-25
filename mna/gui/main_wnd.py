# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import gettext
import logging

from PyQt4 import QtGui, uic

from mna.gui import _models
from mna.gui import _resources_rc
from mna.lib.appconfig import AppConfig
from mna.model import dbobjects as DBO

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert _resources_rc


class MainWnd(QtGui.QMainWindow):
    """ Main Window class. """

    def __init__(self, _parent=None):
        super(MainWnd, self).__init__()
        self._appconfig = AppConfig()
        uic.loadUi(self._appconfig.get_data_file("gui/main.ui"), self)
        self._bind()
        self._tree_model = _models.TreeModel()
        self.treeSubscriptions.setModel(self._tree_model)

    def _bind(self):
        self.actionRefresh.triggered.connect(self._on_action_refresh)

    def _on_action_refresh(self):
        DBO.Source.force_refresh_all()

    def _refresh_tree(self):
        pass
