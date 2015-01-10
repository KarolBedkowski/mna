# -*- coding: utf-8 -*-
""" Add/edit monitored website.

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-04"

import logging

from PyQt4 import QtGui

from mna.gui import resources_rc
from mna.gui import ui_dlg_source_edit
from mna.gui import frm_sett_main
from mna.logic import sources
from mna import plugins

_LOG = logging.getLogger(__name__)

assert resources_rc


class DlgSourceEdit(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, source=None):
        _LOG.info("DlgSourceEdit.init: %r", source)
        QtGui.QDialog.__init__(self, parent)
        self._ui = ui_dlg_source_edit.Ui_DlgSourceEdit()
        self._ui.setupUi(self)
        self._source = source
        self._setup(source)
        self.setWindowTitle(source.title)
        self._to_window(source)

    def _setup(self, source):
        self._frm_sett_main = frm_sett_main.FrmSettMain(self)
        self._ui.l_main_opt.addWidget(self._frm_sett_main)
        src = plugins.SOURCES[source.name]
        if hasattr(src, 'conf_panel_class'):
            src_opt_frame = src.conf_panel_class(self)
        else:
            src_opt_frame = QtGui.QLabel("No options", self)
        self._ui.l_src_opt.addWidget(src_opt_frame)
        self._curr_src_frame = src_opt_frame

    def done(self, result):
        if result != QtGui.QDialog.Accepted:
            return QtGui.QDialog.done(self, result)
        if not self._validate():
            print 'n-valid'
            return
        if self._from_window():
            sources.save_source(self._source)
            return QtGui.QDialog.done(self, result)

    def _to_window(self, source):
        self._frm_sett_main.to_window(source)
        if hasattr(self._curr_src_frame, 'to_window'):
            self._curr_src_frame.to_window(source)
        self._ui.e_interval.setValue((source.interval or 3600) / 60)

    def _from_window(self):
        source = self._source
        if not self._frm_sett_main.from_window(source):
            return False
        if hasattr(self._curr_src_frame, 'from_window'):
            if not self._curr_src_frame.from_window(source):
                return False
        source.interval = self._ui.e_interval.value() * 60
        return True

    def _validate(self):
        if not self._frm_sett_main.validate():
            return False
        if hasattr(self._curr_src_frame, 'validate'):
            if not self._curr_src_frame.validate():
                return False
        if self._ui.e_interval.value() < 1:
            return False
        return True
