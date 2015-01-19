# -*- coding: utf-8 -*-
""" Filters configuration gui.

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-19"

import logging

from PyQt4 import QtGui

from mna import plugins
from mna.model import dbobjects as DBO
from mna.gui import dlg_filter_type_ui
from mna.gui import dlg_filter_options_ui

_LOG = logging.getLogger(__name__)


class DlgFilterType(QtGui.QDialog):
    def __init__(self, parent=None, value=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = dlg_filter_type_ui.Ui_FilterTypeDialog()
        self._ui.setupUi(self)
        for name, fltr in plugins.FILTERS.iteritems():
            self._ui.cb_filter.addItem(fltr.name, name)
        if value:
            idx = self._ui.cb_filter.findData(value)
            assert idx, 'value %r not found in filters' % value
            self._ui.cb_filter.setCurrentIndex(idx)
        self.value = value

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            self.value = self._ui.cb_filter.itemData(
                self._ui.cb_filter.currentIndex()).toString()
        return QtGui.QDialog.done(self, result)


class DlgFilterOptions(QtGui.QDialog):
    def __init__(self, parent, fltr):
        QtGui.QDialog.__init__(self, parent)
        self.fltr = fltr
        self._ui = dlg_filter_options_ui.Ui_DlgFilterOptions()
        self._ui.setupUi(self)


        self._ui.l_title.setText(self.tr("%s parameters") % fltr.name)

        self._widgets = {}
        lay = self._ui.fl_options
        values = fltr.cfg.conf
        for name, opts in fltr.get_params().iteritems():
            title, ftype, default = opts
            lay.addWidget(QtGui.QLabel(title))
            value = values.get(name) if values else None
            if value is None:
                value = default
            if ftype == int:
                wdg = QtGui.QSpinBox()
                wdg.setMinimum(-999999)
                wdg.setMaximum(999999)
                wdg.setValue(value or 0)
            elif ftype == str:
                wdg = QtGui.QLineEdit()
                wdg.setText(value or '')
            else:
                raise RuntimeError('invalid field type %r - %r', name, opts)
            lay.addWidget(wdg)
            self._widgets[name] = wdg

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            fltr = self.fltr
            for name, opts in fltr.get_params().iteritems():
                _title, ftype, value = opts
                wdg = self._widgets[name]
                if ftype == int:
                    value = wdg.value()
                elif ftype == str:
                    value = wdg.text()
                self.fltr.cfg.conf[name] = value
            print self.fltr.cfg.conf
        return QtGui.QDialog.done(self, result)


def add_filter(parent_wnd, source_id):
    """ Open dialogs for new filter. Save changes to database. """
    dlg = DlgFilterType(parent_wnd)
    if dlg.exec_() != QtGui.QDialog.Accepted:
        return
    fltr_cfg = DBO.Filter()
    fltr_cfg.conf = {}
    fltr_cfg.name = dlg.value
    fltr_cfg.source_id = source_id
    fltr = plugins.FILTERS[dlg.value](fltr_cfg)
    dlg = DlgFilterOptions(parent_wnd, fltr)
    if dlg.exec_() == QtGui.QDialog.Accepted:
        fltr_cfg.save(commit=True)
        return True
    return False


def edit_filter(parent_wnd, fltr_id):
    """ Open filter edit dialog; save changes to database. """
    fltr_cfg = DBO.Filter.get(oid=fltr_id)
    assert fltr_cfg is not None, "Can't find filter with id %r" % fltr_id
    fltr = plugins.FILTERS[fltr_cfg.name](fltr_cfg)
    dlg = DlgFilterOptions(parent_wnd, fltr)
    if dlg.exec_() == QtGui.QDialog.Accepted:
        fltr_cfg.save(commit=True)
        return True
    return False


def delete_filter(parent_wnd, fltr_id):
    """ Delete filter from database. """
    fltr_cfg = DBO.Filter.get(oid=fltr_id)
    fltr = plugins.FILTERS[fltr_cfg.name](fltr_cfg)
    reply = QtGui.QMessageBox.question(
        parent_wnd,
        "Delete filter",
        "Delete filter: " + fltr.get_label(fltr_cfg) + "?",
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
        fltr_cfg.delete(commit=True)
        return True
    return False
