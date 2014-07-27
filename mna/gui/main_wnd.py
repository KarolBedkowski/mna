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
import webbrowser

from PyQt4 import QtGui, uic, QtWebKit

from mna.gui import _models
from mna.gui import _resources_rc
from mna.gui import add_group_dialog
from mna.gui import add_rss_dialog
from mna.lib.appconfig import AppConfig
from mna.model import dbobjects as DBO
from mna.logic import groups
from mna import plugins

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert _resources_rc


class MainWnd(QtGui.QMainWindow):
    """ Main Window class. """

    def __init__(self, _parent=None):
        super(MainWnd, self).__init__()
        self._appconfig = AppConfig()
        uic.loadUi(self._appconfig.get_data_file("gui/main.ui"), self)
        self._tree_model = _models.TreeModel()
        self._list_model = _models.ListModel()
        self.tree_subscriptions.setModel(self._tree_model)
        self.table_articles.setModel(self._list_model)
        self._current_source = None
        self._current_source_obj = None
        # handle links
        self.article_view.page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)
        self._bind()

    def _bind(self):
        self.action_refresh.triggered.connect(self._on_action_refresh)
        self.tree_subscriptions.clicked.connect(self._on_tree_clicked)
        self.table_articles.selectionModel().selectionChanged.connect(
                self._on_table_articles_clicked)
        self.add_group_action.triggered.connect(self._on_add_group_action)
        self.add_rss_action.triggered.connect(self._on_add_rss_action)
        self.article_view.linkClicked.connect(self._on_article_view_link)
        # handle article list selection changes
        sel_model = self.table_articles.selectionModel()
        sel_model.currentChanged.connect(self._on_table_articles_clicked)
        sel_model.selectionChanged.connect(self._on_table_articles_clicked)

    def _on_action_refresh(self):
        DBO.Source.force_refresh_all()
        self._tree_model.refresh()

    def _on_tree_clicked(self, index):
        """ Handle group/source selection. """
        node = self._tree_model.node_from_index(index)
        assert node.oid
        articles = []
        self._current_source = None
        if node.kind == _models.TreeNode.KIND_SOURCE:
            source = DBO.Source.get(oid=node.oid)
            articles = source.articles
            self._current_source = source
        self._list_model.set_items(articles)
        self.table_articles.resizeColumnsToContents()

    def _on_table_articles_clicked(self, index):
        """ Handle article selection -  show article in HtmlView. """
        index = self.table_articles.selectionModel().currentIndex()
        item = self._list_model.node_from_index(index)
        article = DBO.Article.get(oid=item.oid)
        if (self._current_source_obj is None or
                self._current_source.oid != article.oid):
            source = DBO.Source.get(oid=article.source_id)
            self._current_source = source
            self._current_source_obj = plugins.SOURCES.get(source.name)
        presenter = self._current_source_obj.presenter(self._current_source_obj)
        content = presenter.to_gui(article)
        self.article_view.setHtml(content)
        article.readed = 1
        article.save(True)

    def _on_add_group_action(self):
        dlg = add_group_dialog.AddGroupDialog(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            if groups.add_group(dlg.get_text()):
                self._refresh_tree()

    def _on_add_rss_action(self):
        dlg = add_rss_dialog.AddRssDialog(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            pass

    def _on_article_view_link(self, url):
        webbrowser.open(unicode(url.toString()))

    def _refresh_tree(self):
        self._tree_model.refresh()
