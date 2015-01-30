# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"

import logging

from PyQt4 import QtGui

from mna.gui import _validators
from mna.gui import resources_rc
from mna.gui import dlg_edit_group_ui
from mna.logic import groups
from mna.model import dbobjects as DBO
from mna.model import db

_LOG = logging.getLogger(__name__)

assert resources_rc


class DlgEditGroup(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, group_oid=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = dlg_edit_group_ui. Ui_DlgEditGroup()
        self._ui.setupUi(self)
        if group_oid:
            group = db.get_one(DBO.Group, oid=group_oid)
            self.setWindowTitle("Edit %s Group" % group.name)
        else:
            group = DBO.Group()
            self.setWindowTitle("New Group")
        self._group = group
        self._to_window()

    def done(self, result):
        if result != QtGui.QDialog.Accepted:
            return QtGui.QDialog.done(self, result)

        try:
            self._validate()
        except _validators.ValidationError, err:
            QtGui.QMessageBox.information(
                self, self.tr("Validation error"),
                self.tr("Please correct field ") + unicode(err))
            return
        self._from_window()
        try:
            groups.save_group(self._group)
        except groups.GroupSaveError, err:
            QtGui.QMessageBox.information(
                self, self.tr("Validation error"),
                self.tr("Error saving group: ") + unicode(err))
            return
        return QtGui.QDialog.done(self, result)

    def _to_window(self):
        self._ui.name_edit.setText(self._group.name or '')

    def _from_window(self):
        self._group.name = unicode(self._ui.name_edit.text()).strip()

    def _validate(self):
        _validators.validate_empty_string(self._ui.name_edit, "name")
