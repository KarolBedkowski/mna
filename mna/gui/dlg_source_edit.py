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
from mna.gui import dlg_source_edit_ui
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
        self._ui = dlg_source_edit_ui.Ui_DlgSourceEdit()
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
            return
        if self._from_window():
            sources.save_source(self._source)
            return QtGui.QDialog.done(self, result)

    def _to_window(self, source):
        self._frm_sett_main.to_window(source)
        if hasattr(self._curr_src_frame, 'to_window'):
            self._curr_src_frame.to_window(source)
        self._ui.e_interval.setValue((source.interval or 3600) / 60)
        self._ui.sb_art_keep_num.setValue(source.num_articles_to_keep or 0)
        self._ui.sb_art_keep_age.setValue(source.age_articles_to_keep or 0)
        self._ui.gb_delete_art.setChecked(bool(source.delete_old_articles))
        self._ui.sb_max_art_load.setValue(source.max_articles_to_load or 0)
        self._ui.sb_max_age_load.setValue(source.max_age_to_load or 0)

    def _from_window(self):
        source = self._source
        if not self._frm_sett_main.from_window(source):
            return False
        if hasattr(self._curr_src_frame, 'from_window'):
            if not self._curr_src_frame.from_window(source):
                return False
        source.interval = self._ui.e_interval.value() * 60
        source.num_articles_to_keep = self._ui.sb_art_keep_num.value()
        source.age_articles_to_keep = self._ui.sb_art_keep_age.value()
        source.delete_old_articles = self._ui.gb_delete_art.isChecked()
        source.max_articles_to_load = self._ui.sb_max_art_load.value()
        source.max_age_to_load = self._ui.sb_max_age_load.value()
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
