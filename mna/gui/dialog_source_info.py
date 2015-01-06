# -*- coding: utf-8 -*-
""" Dialog - information about source.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import logging

from PyQt4 import QtGui, QtCore

from mna.gui import resources_rc
from mna.gui import ui_dialog_source_info

_LOG = logging.getLogger(__name__)

assert resources_rc


class DialogSourceInfo(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent, source):
        _LOG.info("DialogSourceInfo.init: %r", source)
        QtGui.QDialog.__init__(self, parent)
        self._ui = ui_dialog_source_info.Ui_DialogSourceInfo()
        self._ui.setupUi(self)
        self._setup(source)
        self._bind()
        self.setWindowTitle("Source %s info" % source.title)

    def _setup(self, source):
        self._create_info_model(source)
        self._create_logs_model(source)

    def _create_info_model(self, source):
        info = [('Name', source.name),
                ('Title', source.title),
                ('Last refreshed', unicode(source.last_refreshed)),
                ('Next refresh', unicode(source.next_refresh)),
                ('Last error date', unicode(source.last_error_date)),
                ('Last error', unicode(source.last_error))]

        model = QtGui.QStandardItemModel(0, 2, self._ui.lv_info)
        model.setHeaderData(0, QtCore.Qt.Horizontal, self.tr("Key"))
        model.setHeaderData(1, QtCore.Qt.Horizontal, self.tr("Value"))
        for key, val in info:
            model.appendRow([QtGui.QStandardItem(key), QtGui.QStandardItem(val)])
        self._ui.lv_info.setModel(model)
        self._ui.lv_info.resizeColumnToContents(0)
        self._ui.lv_info.resizeColumnToContents(1)

    def _create_logs_model(self, source):
        logs = source.get_logs()
        model = QtGui.QStandardItemModel(0, 3, self._ui.lv_logs)
        model.setHeaderData(0, QtCore.Qt.Horizontal, self.tr("Date"))
        model.setHeaderData(1, QtCore.Qt.Horizontal, self.tr("Category"))
        model.setHeaderData(2, QtCore.Qt.Horizontal, self.tr("Message"))
        for log in logs:
            model.appendRow([QtGui.QStandardItem(unicode(log.date)),
                             QtGui.QStandardItem(log.category or ''),
                             QtGui.QStandardItem(log.message or '')])
        self._ui.lv_logs.setModel(model)
        self._ui.lv_logs.resizeColumnToContents(0)
        self._ui.lv_logs.resizeColumnToContents(1)
        self._ui.lv_logs.resizeColumnToContents(2)


    def _bind(self):
        pass
