# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import gettext
import logging

from PyQt4 import QtGui, uic

from mna.gui import _models
from mna.gui import _resources_rc
from mna.gui import add_group_dialog
from mna.gui import add_rss_dialog
from mna.lib.appconfig import AppConfig
from mna.model import dbobjects as DBO
from mna.logic import groups

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert _resources_rc


class MainWnd(QtGui.QMainWindow):
    """ Main Window class. """

    def __init__(self, _parent=None):
        super(MainWnd, self).__init__()
        self._appconfig = AppConfig()
        uic.loadUi(self._appconfig.get_data_file("gui/main.ui"), self)
        self._bind()
        self._tree_model = _models.TreeModel()
        self._list_model = _models.ListModel()
        self.tree_subscriptions.setModel(self._tree_model)
        self.table_articles.setModel(self._list_model)

    def _bind(self):
        self.action_refresh.triggered.connect(self._on_action_refresh)
        self.tree_subscriptions.clicked.connect(self._on_tree_clicked)
        self.table_articles.clicked.connect(self._on_table_articles_clicked)
        self.add_group_action.triggered.connect(self._on_add_group_action)
        self.add_rss_action.triggered.connect(self._on_add_rss_action)

    def _on_action_refresh(self):
        DBO.Source.force_refresh_all()
        self._tree_model.refresh()

    def _on_tree_clicked(self, index):
        """ Handle group/source selection. """
        node = self._tree_model.node_from_index(index)
        assert node.oid
        articles = []
        if node.kind == _models.TreeNode.KIND_SOURCE:
            source = DBO.Source.get(oid=node.oid)
            articles = source.articles
        self._list_model.set_items(articles)

    def _on_table_articles_clicked(self, index):
        """ Handle article selection -  show article in HtmlView. """
        item = self._list_model.node_from_index(index)
        article = DBO.Article.get(oid=item.oid)
        self.article_view.setHtml(article.content or article.summary
                                  or article.title)

    def _on_add_group_action(self):
        dlg = add_group_dialog.AddGroupDialog(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            if groups.add_group(dlg.get_text()):
                self._refresh_tree()

    def _on_add_rss_action(self):
        dlg = add_rss_dialog.AddRssDialog(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            pass

    def _refresh_tree(self):
        self._tree_model.refresh()
