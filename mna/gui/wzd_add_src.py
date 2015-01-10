# -*- coding: utf-8 -*-
""" Add source wizard.

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
from mna.gui import ui_wzd_add_src
from mna import plugins
from mna.gui import ui_frm_sett_main
from mna.gui import _validators
from mna.model import dbobjects as DBO
from mna.logic import sources

_LOG = logging.getLogger(__name__)

assert resources_rc


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


class WzdAddSrc(QtGui.QWizard):
    """ Add new source wizard. """

    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self._ui = ui_wzd_add_src.Ui_WizardAddSource()
        self._ui.setupUi(self)
        self._setup()
        self._bind()

    def _setup(self):
        self._curr_src_frame = None
        self._curr_src = None

        for name, source_cls in plugins.SOURCES.iteritems():
            self._ui.cb_source_type.addItem(source_cls.name, name)

        self._frm_edit_main = FrmSettMain(self)
        self._ui.l_main_opt.addWidget(self._frm_edit_main)

    def _bind(self):
        pass

    def initializePage(self, page):
        if page == 1:  # source specific settings
            sel_source_type = self._ui.cb_source_type.currentIndex()
            src = unicode(self._ui.cb_source_type.itemData(sel_source_type).
                          toPyObject())
            if self._curr_src == src:
                return
            self._curr_src = src
            # remove current frame
            while not self._ui.l_src_opt.isEmpty():
                itm = self._ui.l_src_opt.itemAt(0)
                self._ui.l_src_opt.removeItem(itm)
                wdg = itm.widget()
                wdg.hide()
                wdg.destroy()
            # create new frame
            src_opt_frame = None
            src_cls = plugins.SOURCES[src]
            if hasattr(src_cls, 'conf_panel_class'):
                src_opt_frame = src_cls.conf_panel_class(self)
            else:
                src_opt_frame = QtGui.QLabel("No options", self)
            self._ui.l_src_opt.addWidget(src_opt_frame)
            self._curr_src_frame = src_opt_frame

    def validateCurrentPage(self):
        if not self.currentPage().validatePage():
            return False
        page = self.currentId()
        if page == 0:  # main
            return self._frm_edit_main.validate()
        elif page == 1:  # source settings
            assert self._curr_src_frame is not None, "Missing curr src frame"
            if hasattr(self._curr_src_frame, 'validate'):
                return self._curr_src_frame.validate()
        elif page == 2:  # additional
            if self._ui.e_interval.value() < 1:
                return False
        return True

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            self._create_source()
        return QtGui.QWizard.done(self, result)

    def _create_source(self):
        source = DBO.Source()
        source.name = self._curr_src
        source.conf = {}
        # get params from main frame
        self._frm_edit_main.from_window(source)
        # source specific
        if hasattr(self._curr_src_frame, 'from_window'):
            self._curr_src_frame.from_window(source)
        # additional
        source.interval = self._ui.e_interval.value() * 60
        sources.save_source(source)
