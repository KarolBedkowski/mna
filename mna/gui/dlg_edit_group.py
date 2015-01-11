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

from mna.gui import _validators
from mna.gui import resources_rc
from mna.gui import dlg_edit_group_ui
from mna.logic import groups
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)

assert resources_rc


class DlgEditGroup(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, group=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = dlg_edit_group_ui. Ui_DlgEditGroup()
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
        try:
            self._validate()
        except _validators.ValidationError, err:
            QtGui.QMessageBox.information(self, self.tr("Validation error"),
                                          self.tr("Please correct field ") +
                                          str(err))
            return
        self._from_window()
        try:
            groups.save_group(self._group)
        except groups.GroupSaveError, err:
            QtGui.QMessageBox.information(self, self.tr("Validation error"),
                                          self.tr("Error saving group: ") +
                                          unicode(err))
            return
        self.accept()

    def _to_window(self):
        self._ui.name_edit.setText(self._group.name or '')

    def _from_window(self):
        self._group.name = unicode(self._ui.name_edit.text()).strip()

    def _validate(self):
        _validators.validate_empty_string(self._ui.name_edit,
                                          "name")
