# -*- coding: utf-8 -*-
""" Add/edit monitored website.

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-04"

import gettext
import logging

from PyQt4 import QtGui

from mna.gui import resources_rc
from mna.gui import ui_dialog_edit_web
from mna.model import dbobjects as DBO
from mna.logic import sources

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert resources_rc


class DialogEditWeb(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, source=None):
        _LOG.info("DialogEditWeb.init: %r", source)
        QtGui.QDialog.__init__(self, parent)
        self._ui = ui_dialog_edit_web.Ui_DialogAddWeb()
        self._ui.setupUi(self)
        self._setup()
        self._bind()
        if source:
            self.setWindowTitle("Edit %s Source" % source.title)
        else:
            self.setWindowTitle("New Group")
            source = DBO.Source()
            source.name = "mna.plugins.web.WebSource"
            source.conf = {}
        self._source = source
        self._to_window(source)

    def _setup(self):
        for group in DBO.Group.all():
            self._ui.c_group.addItem(group.name, group.oid)

    def _bind(self):
        self._ui.cancel_btn.clicked.connect(self._on_btn_cancel)
        self._ui.add_btn.clicked.connect(self._on_btn_add)

    def _on_btn_cancel(self):
        self.close()

    def _on_btn_add(self):
        if self._from_window():
            sources.save_source(self._source)
            self.accept()

    def _to_window(self, source):
        if not source:
            return
        self._ui.e_title.setText(source.title or "")
        self._ui.e_url.setText(source.conf.get("url") or "")
        self._ui.e_xpath.setPlainText(source.conf.get("xpath") or "")
        if source.group_id:
            group_idx = self._ui.c_group.findData(source.group_id)
            self._ui.c_group.setCurrentIndex(group_idx)
        self._ui.e_interval.setValue(source.interval or 3600)

    def _from_window(self):
        source = self._source
        source.title = unicode(self._ui.e_title.text())
        source.conf["url"] = unicode(self._ui.e_url.text())
        source.conf["xpath"] = unicode(self._ui.e_xpath.toPlainText())
        group_idx = self._ui.c_group.currentIndex()
        group_id = self._ui.c_group.itemData(group_idx).toInt()[0]
        source.group_id = group_id
        source.interval = self._ui.e_interval.value()
        return True
