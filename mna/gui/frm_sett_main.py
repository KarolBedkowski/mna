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

from mna.gui import ui_frm_sett_main
from mna.gui import _validators
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


class FrmSettMain(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.ui = ui_frm_sett_main.Ui_FrmSettMain()
        self.ui.setupUi(self)
        self._setup()

    def _setup(self):
        for group in DBO.Group.all():
            self.ui.c_group.addItem(group.name, group.oid)

    def validate(self):
        try:
            _validators.validate_empty_string(self.ui.e_title, 'Title')
        except _validators.ValidationError:
            return False
        return True

    def from_window(self, source):
        source.title = unicode(self.ui.e_title.text())
        group_idx = self.ui.c_group.currentIndex()
        group_id = self.ui.c_group.itemData(group_idx).toInt()[0]
        source.group_id = group_id
