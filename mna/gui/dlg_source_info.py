# -*- coding: utf-8 -*-
""" Dialog - information about source.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"

import logging

from PyQt4 import QtGui, QtCore

from mna.gui import resources_rc
from mna.gui import dlg_source_info_ui
from mna.model import db
from mna.model import dbobjects as DBO
from mna import plugins

_LOG = logging.getLogger(__name__)

assert resources_rc


class DlgSourceInfo(QtGui.QDialog):  # pylint:disable=too-few-public-methods,no-member
    """ Main Window class. """

    def __init__(self, parent, source_oid):
        _LOG.info("DlgSourceInfo.init: %r", source_oid)
        QtGui.QDialog.__init__(self, parent)  # pylint:disable=no-member
        self._ui = dlg_source_info_ui.Ui_DlgSourceInfo()
        self._ui.setupUi(self)
        self._setup(source_oid)

    def _setup(self, source_oid):
        session = db.Session()
        source = db.get_one(DBO.Source, session=session, oid=source_oid)

        src_class = plugins.SOURCES.get(source.name)
        assert src_class is not None, source.name

        self._create_info_model(source, session, src_class)
        self._create_logs_model(source)
        self.setWindowTitle("Source %s info" % source.title)  # pylint:disable=no-member

    def _create_info_model(self, source, session, src_class):
        articles_cnt = db.count(DBO.Article, source_id=source.oid)
        info = [('Name', source.name),
                ('Title', source.title),
                ('Last refreshed', unicode(source.last_refreshed)),
                ('Next refresh', unicode(source.next_refresh)),
                ('Last error date', unicode(source.last_error_date)),
                ('Last error', unicode(source.last_error)),
                ('Articles', unicode(articles_cnt))]
        info.extend(src_class.get_info(source, session) or [])

        model = QtGui.QStandardItemModel(0, 2, self._ui.lv_info)  # pylint:disable=no-member
        model.setHeaderData(0, QtCore.Qt.Horizontal, self.tr("Key"))  # pylint:disable=no-member
        model.setHeaderData(1, QtCore.Qt.Horizontal, self.tr("Value"))  # pylint:disable=no-member
        for key, val in info:
            model.appendRow([QtGui.QStandardItem(key),  # pylint:disable=no-member
                             QtGui.QStandardItem(val)])  # pylint:disable=no-member
        self._ui.lv_info.setModel(model)
        self._ui.lv_info.resizeColumnToContents(0)
        self._ui.lv_info.resizeColumnToContents(1)

    def _create_logs_model(self, source):
        logs = source.source_log
        model = QtGui.QStandardItemModel(0, 3, self._ui.lv_logs)  # pylint:disable=no-member
        model.setHeaderData(0, QtCore.Qt.Horizontal, self.tr("Date"))  # pylint:disable=no-member
        model.setHeaderData(1, QtCore.Qt.Horizontal, self.tr("Category"))  # pylint:disable=no-member
        model.setHeaderData(2, QtCore.Qt.Horizontal, self.tr("Message"))  # pylint:disable=no-member
        for log in logs:
            model.appendRow([QtGui.QStandardItem(unicode(log.date)),  # pylint:disable=no-member
                             QtGui.QStandardItem(log.category or ''),  # pylint:disable=no-member
                             QtGui.QStandardItem(log.message or '')])  # pylint:disable=no-member
        self._ui.lv_logs.setModel(model)
        self._ui.lv_logs.resizeColumnToContents(0)
        self._ui.lv_logs.resizeColumnToContents(1)
        self._ui.lv_logs.resizeColumnToContents(2)
