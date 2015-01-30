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
from mna.gui import wzd_add_src_ui
from mna import plugins
from mna.gui import frm_sett_main
from mna.model import dbobjects as DBO
from mna.logic import sources
from mna.lib import appconfig

_LOG = logging.getLogger(__name__)

assert resources_rc


class WzdAddSrc(QtGui.QWizard):
    """ Add new source wizard. """

    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self._ui = wzd_add_src_ui.Ui_WizardAddSource()
        self._ui.setupUi(self)
        self._setup()

    def _setup(self):
        self._curr_src_frame = None
        self._curr_src = None

        for name, source_cls in plugins.SOURCES.iteritems():
            self._ui.cb_source_type.addItem(source_cls.name, name)

        self._frm_edit_main = frm_sett_main.FrmSettMain(self)
        self._ui.l_main_opt.addWidget(self._frm_edit_main)
        aconf = appconfig.AppConfig()
        self._ui.e_interval.setValue(
            aconf.get('articles.update_interval', 60))

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
        source = DBO.Source(name=self._curr_src, conf={})
        # get params from main frame
        self._frm_edit_main.from_window(source)
        # source specific
        if hasattr(self._curr_src_frame, 'from_window'):
            self._curr_src_frame.from_window(source)
        # additional
        source.interval = self._ui.e_interval.value() * 60
        sources.save_source(source)
