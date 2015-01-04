# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import logging

from PyQt4 import QtGui

from mna.gui import resources_rc
from mna.gui import ui_dialog_edit_group
from mna.logic import groups
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)

assert resources_rc


class DialogEditGroup(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, group=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = ui_dialog_edit_group. Ui_DialogAddGroup()
        self._ui.setupUi(self)
        self._bind()
        if group:
            self.setWindowTitle("Edit %s Group" % group.name)
        else:
            self.setWindowTitle("New Group")
            group = DBO.Group()
        self._group = group
        self._to_window()

    def _bind(self):
        self._ui.cancel_btn.clicked.connect(self._on_btn_cancel)
        self._ui.add_btn.clicked.connect(self._on_btn_add)

    def _on_btn_cancel(self):
        self.close()

    def _on_btn_add(self):
        self._from_window()
        if self._group.is_valid():
            groups.save_group(self._group)
            self.accept()

    def _to_window(self):
        self._ui.name_edit.setText(self._group.name or '')

    def _from_window(self):
        self._group.name = unicode(self._ui.name_edit.text()).strip()
