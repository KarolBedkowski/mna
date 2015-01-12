# -*- coding: utf-8 -*-
""" Application preferences dialog.

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-12"

import logging

from PyQt4 import QtGui

from mna.gui import _validators
from mna.gui import resources_rc
from mna.gui import dlg_preferences_ui
from mna.lib import appconfig

_LOG = logging.getLogger(__name__)

assert resources_rc


class DlgPreferences(QtGui.QDialog):
    """ Preferences dialog class. """

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = dlg_preferences_ui.Ui_DlgPreferences()
        self._ui.setupUi(self)
        self._appconf = appconfig.AppConfig()
        self._bind()
        self._to_window()

    def _bind(self):
        pass

    def done(self, result):
        if result != QtGui.QDialog.Accepted:
            return QtGui.QDialog.done(self, result)
        try:
            self._validate()
        except _validators.ValidationError:
            return
        if self._from_window():
            return QtGui.QDialog.done(self, result)

    def _to_window(self):
        aconf = self._appconf
        self_ui = self._ui
        self_ui.sb_max_art_load.setValue(aconf.get('articles.max_num_load', 0))
        self_ui.sb_max_age_load.setValue(aconf.get('articles.max_age_load', 0))
        self_ui.sb_art_keep_age.setValue(aconf.get('articles.keep_older', 0))
        self_ui.sb_art_keep_num.setValue(aconf.get('articles.keep_num', 0))

    def _from_window(self):
        aconf = self._appconf
        self_ui = self._ui
        aconf['articles.max_num_load'] = self_ui.sb_max_art_load.value()
        aconf['articles.max_age_load'] = self_ui.sb_max_age_load.value()
        aconf['articles.keep_older'] = self_ui.sb_art_keep_age.value()
        aconf['articles.keep_num'] = self_ui.sb_art_keep_num.value()
        return True

    def _validate(self):
        pass
