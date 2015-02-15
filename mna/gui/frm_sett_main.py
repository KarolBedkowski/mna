# -*- coding: utf-8 -*-
""" Setting - main settings.

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-10"

import logging

from PyQt4 import QtGui

from mna.gui import frm_sett_main_ui
# from mna.gui import _validators
from mna.model import db
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


class FrmSettMain(QtGui.QFrame):  # pylint: disable=no-member
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)  # pylint: disable=no-member

        self._ui = frm_sett_main_ui.Ui_FrmSettMain()
        self._ui.setupUi(self)
        self._setup()

    def _setup(self):
        for group in db.get_all(DBO.Group):
            self._ui.c_group.addItem(group.name, group.oid)

    def validate(self):  # pylint:disable=no-self-use
        return True

    def from_window(self, source):
        source.title = unicode(self._ui.e_title.text())
        group_idx = self._ui.c_group.currentIndex()
        group_id = self._ui.c_group.itemData(group_idx).toInt()[0]
        source.group_id = group_id
        source.enabled = self._ui.cb_enabled.isChecked()
        return True

    def to_window(self, source):
        self._ui.e_title.setText(source.title or "")
        if source.group_id:
            group_idx = self._ui.c_group.findData(source.group_id)
            self._ui.c_group.setCurrentIndex(group_idx)
        self._ui.cb_enabled.setChecked(source.enabled)
