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

from mna.gui import _resources_rc
from mna.lib.appconfig import AppConfig

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert _resources_rc


class AddRssDialog(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None):
        super(AddRssDialog, self).__init__(parent)
        self._appconfig = AppConfig()
        uic.loadUi(self._appconfig.get_data_file("gui/dialog_add_rss.ui"),
                   self)
        self._bind()

    def get_text(self):
        return unicode(self.name_edit.text()).strip()

    def _bind(self):
        self.cancel_btn.clicked.connect(self._on_btn_cancel)
        self.add_btn.clicked.connect(self._on_btn_add)

    def _on_btn_cancel(self):
        self.close()

    def _on_btn_add(self):
        if self.get_text():
            self.accept()
