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

try:
    import simplejson as json
except ImportError:
    import json

from PyQt4 import QtGui, QtCore

from mna.common import dlg_info
from mna.gui import resources_rc
from mna.gui import dlg_source_edit_ui
from mna.gui import frm_sett_main
from mna.gui import filter_conf
from mna.logic import sources
from mna import plugins
from mna.model import db
from mna.model import dbobjects as DBO
from mna.lib import appconfig

_LOG = logging.getLogger(__name__)

assert resources_rc


# pylint:disable=no-member,too-few-public-methods
class DlgSourceEdit(QtGui.QDialog):
    """ Main Window class. """

    def __init__(self, parent=None, source_oid=None):
        _LOG.info("DlgSourceEdit.init: %r", source_oid)
        QtGui.QDialog.__init__(self, parent)  # pylint:disable=no-member
        self._ui = dlg_source_edit_ui.Ui_DlgSourceEdit()
        self._ui.setupUi(self)
        self._bind()
        source = db.get_one(DBO.Source, oid=source_oid)
        self.source = source
        self._setup(source)
        self.setWindowTitle(source.title)  # pylint:disable=no-member
        self._to_window(source)

    def _bind(self):
        self._ui.b_add_filter.clicked.connect(self._on_add_filter)
        self._ui.b_remove_filter.clicked.connect(self._on_remove_filter)
        self._ui.lv_filters.itemActivated.connect(self._on_filters_act)
        if appconfig.AppConfig().debug:
            self._ui.b_dev_save.clicked.connect(self._on_dev_save)
            self._ui.b_dev_load.clicked.connect(self._on_dev_load)
            self._ui.b_dev_show.clicked.connect(self._on_dev_show)

    def _setup(self, source):
        self._frm_sett_main = frm_sett_main.FrmSettMain(self)
        self._ui.l_main_opt.addWidget(self._frm_sett_main)
        src = plugins.SOURCES[source.name]
        if hasattr(src, 'conf_panel_class') and src.conf_panel_class:
            src_opt_frame = src.conf_panel_class(self)
        else:
            # pylint:disable=no-member
            src_opt_frame = QtGui.QLabel("No options", self)
        self._ui.l_src_opt.addWidget(src_opt_frame)
        self._curr_src_frame = src_opt_frame
        if not appconfig.AppConfig().debug:
            self._ui.tab_widget.removeTab(4)

    def done(self, result):
        if result != QtGui.QDialog.Accepted:  # pylint:disable=no-member
            return QtGui.QDialog.done(self, result)  # pylint:disable=no-member
        if not self._validate():
            return
        if self._from_window():
            sources.save_source(self.source)
            return QtGui.QDialog.done(self, result)  # pylint:disable=no-member

    def _to_window(self, source):
        self._frm_sett_main.to_window(source)
        if self._curr_src_frame and hasattr(self._curr_src_frame, 'to_window'):
            self._curr_src_frame.to_window(source)
        self_ui = self._ui
        self_ui.e_interval.setValue((source.interval or 3600) / 60)
        self_ui.sb_art_keep_num.setValue(source.num_articles_to_keep or 0)
        self_ui.sb_art_keep_age.setValue(source.age_articles_to_keep or 0)
        self_ui.gb_delete_art.setChecked(bool(source.delete_old_articles))
        self_ui.sb_max_art_load.setValue(source.max_articles_to_load or 0)
        self_ui.sb_max_age_load.setValue(source.max_age_to_load or 0)
        self_ui.gb_filter_articles.setChecked(
            source.conf.get('filter.enabled', True))
        self_ui.cb_filter_score.setChecked(
            source.conf.get('filter.score', True))
        self_ui.cb_filter_score_default.setChecked(
            source.conf.get('filter.use_default_score', True))
        self_ui.sp_minial_score.setValue(
            source.conf.get('filter.min_score', 0))
        self_ui.cb_global_filters.setChecked(
            source.conf.get('filter.apply_global', True))
        self._fill_filters()

    def _from_window(self):
        source = self.source
        if not self._frm_sett_main.from_window(source):
            return False
        if hasattr(self._curr_src_frame, 'from_window'):
            if not self._curr_src_frame.from_window(source):
                return False
        self_ui = self._ui
        source.interval = self._ui.e_interval.value() * 60
        source.num_articles_to_keep = self_ui.sb_art_keep_num.value()
        source.age_articles_to_keep = self_ui.sb_art_keep_age.value()
        source.delete_old_articles = self_ui.gb_delete_art.isChecked()
        source.max_articles_to_load = self_ui.sb_max_art_load.value()
        source.max_age_to_load = self_ui.sb_max_age_load.value()
        source.conf['filter.enabled'] = self_ui.gb_filter_articles.isChecked()
        source.conf['filter.score'] = self_ui.cb_filter_score.isChecked()
        source.conf['filter.use_default_score'] = \
            self_ui.cb_filter_score_default.isChecked()
        source.conf['filter.min_score'] = self_ui.sp_minial_score.value()
        source.conf['filter.apply_global'] = \
            self_ui.cb_global_filters.isChecked()
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

    def _fill_filters(self):
        lv_filters = self._ui.lv_filters
        lv_filters.clear()
        for fltr in db.get_all(DBO.Filter, source_id=self.source.oid):
            fltr_class = plugins.FILTERS[fltr.name]
            # pylint:disable=no-member
            itm = QtGui.QListWidgetItem(fltr_class.get_label(fltr))
            # pylint:disable=no-member
            itm.setData(QtCore.Qt.UserRole, fltr.oid)
            lv_filters.addItem(itm)

    def _on_add_filter(self):
        if filter_conf.add_filter(self, self.source.oid):
            self._fill_filters()

    def _on_remove_filter(self):
        item = self._ui.lv_filters.currentItem()
        if not item:
            return
        fltr_id = item.data(QtCore.Qt.UserRole)  # pylint:disable=no-member
        assert fltr_id, "Missing user data in item %r" % item
        fltr_id, conv_ok = fltr_id.toInt()
        assert conv_ok, "Invalid id in item: %r" % fltr_id
        if filter_conf.delete_filter(self, fltr_id):
            self._fill_filters()

    def _on_filters_act(self, item):
        fltr_id = item.data(QtCore.Qt.UserRole)  # pylint:disable=no-member
        assert fltr_id, "Missing user data in item %r" % item
        fltr_id, conv_ok = fltr_id.toInt()
        assert conv_ok, "Invalid id in item: %r" % fltr_id
        if filter_conf.edit_filter(self, fltr_id):
            self._fill_filters()

    def _on_dev_load(self):
        source = self.source
        self._ui.e_dev_conf.setPlainText(json.dumps(source.conf or {},
                                                    indent='  '))
        self._ui.e_dev_meta.setPlainText(json.dumps(source.meta or {},
                                                    indent='  '))
        self._ui.dte_dev_last_refresh.setDateTime(source.last_refreshed)

    def _on_dev_save(self):
        source = self.source
        conf = self._ui.e_dev_conf.toPlainText()
        if conf:
            source.conf = json.loads(conf)
        meta = self._ui.e_dev_meta.toPlainText()
        if meta:
            source.meta = json.loads(meta)
        last_refresh = self._ui.dte_dev_last_refresh.dateTime()
        source.last_refreshed = last_refresh.toPyDateTime()

    def _on_dev_show(self):
        info = "\n".join(key + " = " + repr(val)
                         for key, val in self.source.obj_info())
        dlg = dlg_info.DlgInfo(self, "Source " + self.source.title, info)
        dlg.exec_()
