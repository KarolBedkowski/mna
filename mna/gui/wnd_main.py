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

from PyQt4 import QtGui, QtWebKit, QtCore

from mna.gui import _models
from mna.gui import resources_rc
from mna.gui import wnd_main_ui
from mna.gui import dlg_edit_group
from mna.gui import dlg_source_edit
from mna.gui import dlg_source_info
from mna.lib.appconfig import AppConfig
from mna.model import dbobjects as DBO
from mna.logic import groups, sources
from mna.common import objects
from mna import plugins

_ = gettext.gettext
_LOG = logging.getLogger(__name__)

assert resources_rc


class WndMain(QtGui.QMainWindow):
    """ Main Window class. """

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self._appconfig = AppConfig()
        self._ui = wnd_main_ui.Ui_WndMain()
        self._ui.setupUi(self)
        # setup
        self._tree_model = _models.TreeModel()
        self._list_model = _models.ListModel()
        self._list_model_proxy = QtGui.QSortFilterProxyModel(self)
        self._list_model_proxy.setDynamicSortFilter(True)
        self._list_model_proxy.setSourceModel(self._list_model)
        self._ui.tree_subscriptions.setModel(self._tree_model)
        self._ui.table_articles.setModel(self._list_model_proxy)
        self._ui.table_articles.setSortingEnabled(True)
        self._ui.tree_subscriptions.\
                setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui.tree_subscriptions.customContextMenuRequested.\
                connect(self._on_tree_popupmenu)

        self._last_presenter = (None, None)

        # handle links
        self._ui.article_view.page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)
        self._bind()
        self._set_window_pos_size()

    def _bind(self):
        self._ui.action_refresh.triggered.connect(self._on_action_refresh)
        self._ui.tree_subscriptions.clicked.connect(self._on_tree_clicked)
        self._ui.table_articles.selectionModel().\
                selectionChanged.connect(self._on_table_articles_clicked)
        self._ui.add_group_action.triggered.connect(self._on_add_group_action)
        self._ui.add_src_action.triggered.connect(self._on_add_src_action)
        self._ui.article_view.linkClicked.connect(self._on_article_view_link)
        # handle article list selection changes
        self._ui.mark_all_read_action.triggered.\
                connect(self._on_mark_all_read_action)
        objects.MESSENGER.source_updated.connect(self._on_source_updated)
        objects.MESSENGER.group_updated.connect(self._on_group_updated)

        self._ui.show_unread_action.triggered.\
                connect(self._on_show_unread_action)

    def closeEvent(self, event):
        self._save_window_pos_size()
        event.accept()

    @property
    def selected_tree_item(self):
        model = self._ui.tree_subscriptions.selectionModel()
        index = model.currentIndex()
        item = self._tree_model.node_from_index(index)
        return item

    def _on_action_refresh(self):
        DBO.Source.force_refresh_all()

    def _on_tree_clicked(self, index):
        """ Handle group/source selection."""
        node = self._tree_model.node_from_index(index)
        assert node.oid
        self._show_articles(node)

    def _on_tree_popupmenu(self, position):
        selected = self.selected_tree_item
        menu = QtGui.QMenu()
        menu.addAction(self.tr("Edit")).triggered.\
                connect(self._on_tree_menu_edit)
        menu.addAction(self.tr("Delete")).triggered.\
                connect(self._on_tree_menu_delete)
        if isinstance(selected, _models.SourceTreeNode):
            menu.addAction(self.tr("Info")).triggered.\
                    connect(self._on_tree_menu_info)

        menu.exec_(self._ui.tree_subscriptions.viewport().
                   mapToGlobal(position))

    def _on_tree_menu_edit(self):
        node = self.selected_tree_item
        if node is None:
            return
        if isinstance(node, _models.SourceTreeNode):
            source = DBO.Source.get(oid=node.oid)
            dlg = dlg_source_edit.DlgSourceEdit(self, source)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                objects.MESSENGER.emit_source_updated(source.oid,
                                                      source.group_id)
        elif isinstance(node, _models.GroupTreeNode):
            group = DBO.Group.get(oid=node.oid)
            dlg = dlg_edit_group.DlgEditGroup(self, group)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                objects.MESSENGER.emit_group_updated(group.oid)
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_tree_menu_delete(self):
        model = self._ui.tree_subscriptions.selectionModel()
        index = model.currentIndex()
        node = self._tree_model.node_from_index(index)
        if node is None:
            return
        if QtGui.QMessageBox.question(self, self.tr("Delete"),
                                      self.tr("Delete selected item?"),
                                      QtGui.QMessageBox.Yes,
                                      QtGui.QMessageBox.No) \
                == QtGui.QMessageBox.No:
            return

        model.clearSelection()
#        parent = index.parent()
#        if parent and parent.isValid():
#            model.select(parent)

        if isinstance(node, _models.SourceTreeNode):
            source = DBO.Source.get(oid=node.oid)
            if sources.delete_source(source):
                self._refresh_tree()
        elif isinstance(node, _models.GroupTreeNode):
            group = DBO.Group.get(oid=node.oid)
            if groups.delete_group(group):
                self._refresh_tree()
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_tree_menu_info(self):
        model = self._ui.tree_subscriptions.selectionModel()
        index = model.currentIndex()
        node = self._tree_model.node_from_index(index)
        if node is None or not isinstance(node, _models.SourceTreeNode):
            return
        source = DBO.Source.get(oid=node.oid)
        dlg = dlg_source_info.DlgSourceInfo(self, source)
        dlg.exec_()

    def _on_table_articles_clicked(self, index):
        """ Handle article selection -  show article in HtmlView. """
        index = self._ui.table_articles.selectionModel().currentIndex()
        item = self._list_model.node_from_index(index)
        _LOG.debug("_on_table_articles_clicked %r", item.oid)
        article = DBO.Article.get(oid=item.oid)
        if self._last_presenter[0] == article.source_id:
            presenter = self._last_presenter[1]
        else:
            source_cfg = DBO.Source.get(oid=article.source_id)
            source = plugins.SOURCES.get(source_cfg.name)
            presenter = source.presenter(source)
            self._last_presenter = (article.source_id, presenter)
        content = presenter.to_gui(article)
        #print repr(article.content)
        self._ui.article_view.setHtml(content)
        article.read = 1
        article.save(True)
        self._list_model.update_item(article)
        self._tree_model.update_source(article.source_id,
                                       article.source.group_id)

    def _on_add_group_action(self):
        dlg = dlg_edit_group.DlgEditGroup(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_add_src_action(self):
        from mna.gui import wzd_add_src
        dlg = wzd_add_src.WzdAddSrc(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_article_view_link(self, url):
        webbrowser.open(unicode(url.toString()))

    def _refresh_tree(self):
        self._tree_model.refresh()

    @QtCore.pyqtSlot(int, int)
    def _on_source_updated(self, source_id, group_id):
        """ Handle  source update event. """
        _LOG.debug("Source updated %r, %r", source_id, group_id)
        if not source_id or not group_id:
            return

        self._tree_model.update_source(source_id, group_id)

        # refresh article list when updated source is showed
        node = self.selected_tree_item
        if node is None:
            return
        if isinstance(node, _models.SourceTreeNode) and source_id == node.oid:
            self._show_articles(node)
        elif isinstance(node, _models.GroupTreeNode) and group_id == node.oid:
            self._show_articles(node)

    @QtCore.pyqtSlot(int)
    def _on_group_updated(self, group_id):
        """ Handle group update event. """
        _LOG.debug("Group updated %r", group_id)
        self._tree_model.update_group(group_id)
        node = self.selected_tree_item
        if node is None:
            return
        if isinstance(node, _models.GroupTreeNode) and \
                group_id == node.oid:
            self._show_articles(node)

    def _on_mark_all_read_action(self):
        """ Mark all articles in current group or source read. """
        sources_to_mark = []
        node = self.selected_tree_item
        if node is None:
            return
        if isinstance(node, _models.SourceTreeNode):
            sources_to_mark = [(node.oid, node.parent.oid)]
        elif isinstance(node, _models.GroupTreeNode):
            sources_to_mark = [(child.oid, node.oid)
                               for child
                               in node.children]
        else:
            raise RuntimeError("invalid object type %r", node)
        updated, src_updated = sources.mark_source_read([src[0]
                                                         for src
                                                         in sources_to_mark])
        # when updated - emit signals for refresh tree/list
        if updated > 0:
            for source_oid, group_oid in sources_to_mark:
                # send signals only for real updated sources
                if src_updated[source_oid] > 0:
                    objects.MESSENGER.emit_source_updated(source_oid,
                                                          group_oid)
            objects.MESSENGER.emit_group_updated(sources_to_mark[0][1])

    def _on_show_unread_action(self):
        node = self.selected_tree_item
        self._show_articles(node)

    def _show_articles(self, node):
        _LOG.debug("WndMain._show_articles(%r(oid=%r))", type(node),
                   node.oid)
        unread_only = self._ui.show_unread_action.isChecked()
        if isinstance(node, _models.SourceTreeNode):
            source = DBO.Source.get(oid=node.oid)
        elif isinstance(node, _models.GroupTreeNode):
            source = DBO.Group.get(oid=node.oid)
        else:
            raise RuntimeError("invalid tree item: %r", node)
        articles = source.get_articles(unread_only)
        self._list_model.set_items(articles)
        self._ui.table_articles.resizeColumnsToContents()

    def _set_window_pos_size(self):
        appcfg = self._appconfig
        width = appcfg.get('wnd_main.width')
        height = appcfg.get('wnd_main.hright')
        if width and height:
            self.resize(width, height)
        sp1 = appcfg.get('wnd_main.splitter1')
        if sp1:
            self._ui.splitter.setSizes(sp1)
        sp2 = appcfg.get('wnd_main.splitter2')
        if sp2:
            self._ui.splitter_2.setSizes(sp2)

    def _save_window_pos_size(self):
        appcfg = self._appconfig
        appcfg['wnd_main.width'] = self.width()
        appcfg['wnd_main.height'] = self.height()
        appcfg['wnd_main.splitter1'] = self._ui.splitter.sizes()
        appcfg['wnd_main.splitter2'] = self._ui.splitter_2.sizes()
