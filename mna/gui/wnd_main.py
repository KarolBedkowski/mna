# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import os
import sys
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
from mna.gui import dlg_preferences
from mna.gui import wzd_add_src
from mna.lib.appconfig import AppConfig
from mna.model import db
from mna.logic import groups, sources, articles as larts
from mna.common import messenger

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
        self._ui.table_articles.sortByColumn(4, QtCore.Qt.AscendingOrder)
        self._restore_expanded_tree_nodes()

    def _bind(self):
        self._ui.a_update.triggered.connect(self._on_action_refresh)
        self._ui.action_toggle_selected_articles_read.triggered.\
                connect(self._on_toggle_read_action)
        self._ui.a_preferences.triggered.connect(self._on_action_preferences)
        self._ui.tree_subscriptions.selectionModel().selectionChanged.connect(
            self._on_tree_selection_changed)
        self._ui.table_articles.selectionModel().\
                selectionChanged.connect(self._on_article_list_selchng)
        self._ui.table_articles.clicked.\
                connect(self._on_article_list_clicked)
        self._ui.add_group_action.triggered.connect(self._on_add_group_action)
        self._ui.add_src_action.triggered.connect(self._on_add_src_action)
        self._ui.article_view.linkClicked.connect(self._on_article_view_link)
        # handle article list selection changes
        self._ui.a_mark_read.triggered.connect(self._on_mark_all_read_action)
        messenger.MESSENGER.source_updated.connect(self._on_source_updated)
        messenger.MESSENGER.group_updated.connect(self._on_group_updated)
        messenger.MESSENGER.announce.connect(self._on_announce)

        self._ui.a_show_all.triggered.\
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
        sources.force_refresh_all()

    def _on_tree_selection_changed(self, index):
        """ Handle group/source selection."""
        if not index.count():
            return
        index = index.indexes()[0]
        node = self._tree_model.node_from_index(index)
        assert node.oid
        self._show_articles(node)

    def _on_tree_popupmenu(self, position):
        selected = self.selected_tree_item
        if isinstance(selected, _models.SpecialTreeNode):
            # no menu on special nodes
            return
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
        if isinstance(node, _models.SpecialTreeNode):
            # can't edit special nodes
            return
        if isinstance(node, _models.SourceTreeNode):
            dlg = dlg_source_edit.DlgSourceEdit(self, node.oid)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                messenger.MESSENGER.emit_source_updated(
                    dlg.source.oid, dlg.source.group_id)
        elif isinstance(node, _models.GroupTreeNode):
            dlg = dlg_edit_group.DlgEditGroup(self, node.oid)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                messenger.MESSENGER.emit_group_updated(node.oid)
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_tree_menu_delete(self):
        model = self._ui.tree_subscriptions.selectionModel()
        index = model.currentIndex()
        node = self._tree_model.node_from_index(index)
        if node is None:
            return
        if isinstance(node, _models.SpecialTreeNode):
            # can't delete special nodes
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
            if sources.delete_source(node.oid):
                self._refresh_tree()
        elif isinstance(node, _models.GroupTreeNode):
            if groups.delete_group(node.oid):
                self._refresh_tree()
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_tree_menu_info(self):
        model = self._ui.tree_subscriptions.selectionModel()
        index = model.currentIndex()
        node = self._tree_model.node_from_index(index)
        if node is None or not isinstance(node, _models.SourceTreeNode):
            return
        dlg = dlg_source_info.DlgSourceInfo(self, node.oid)
        dlg.exec_()

    def _on_article_list_clicked(self, index):
        """ Handle article click -  star/flag articles. """
        index = self._ui.table_articles.selectionModel().currentIndex()
        item = self._list_model.node_from_index(index)
        _LOG.debug("_on_article_list_clicked %r %r", item.oid, index.column())
        article = None
        if index.column() == 0:  # readed
            article = list(larts.toggle_articles_read([item.oid]))[0]
        elif index.column() == 1:  # starred
            article = list(larts.toggle_articles_starred([item.oid]))[0]
        if article:
            self._list_model.update_item(article)
            self._tree_model.update_source(article.source_id,
                                           article.source.group_id)

    def _on_article_list_selchng(self, index):
        """ Handle article selection -  show article in HtmlView. """
        index = self._ui.table_articles.selectionModel().currentIndex()
        item = self._list_model.node_from_index(index)
        _LOG.debug("_on_article_list_selchng %r %r", item.oid, index.column())
        session = db.Session()
        article, content = larts.get_article_content(item.oid, True,
                                                     session=session)
        self._ui.article_view.setHtml(content)
        self._list_model.update_item(article)
        self._tree_model.update_source(article.source_id,
                                       article.source.group_id)

    def _on_add_group_action(self):
        dlg = dlg_edit_group.DlgEditGroup(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_add_src_action(self):
        dlg = wzd_add_src.WzdAddSrc(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_article_view_link(self, url):
        if sys.platform.startswith('linux'):
            os.popen('xdg-open "%s"' % unicode(url.toString()))
        else:
            webbrowser.open(unicode(url.toString()))

    def _refresh_tree(self):
        self._save_expanded_tree_nodes()
        self._tree_model.refresh()
        self._restore_expanded_tree_nodes()

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

    @QtCore.pyqtSlot(unicode)
    def _on_announce(self, message):
        self.statusBar().showMessage(message, 10000)

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
                    messenger.MESSENGER.emit_source_updated(
                        source_oid, group_oid)
            messenger.MESSENGER.emit_group_updated(sources_to_mark[0][1])
        self._select_next_unread_source()

    def _on_toggle_read_action(self):
        """ Toggle selected articles read. """
        rows = self._ui.table_articles.selectionModel().selectedRows()
        articles = [self._list_model.node_from_index(index).oid
                    for index in rows]
        if not articles:
            return
        toggled = list(larts.toggle_articles_read(articles))
        if not toggled:
            return
        updated_sources = {}
        for article in toggled:
            self._list_model.update_item(article)
            updated_sources[article.source_id] = article.source.group_id
        for source_id, group_id in updated_sources.iteritems():
            self._tree_model.update_source(source_id, group_id)

    def _on_action_preferences(self):
        dlg = dlg_preferences.DlgPreferences(self)
        dlg.exec_()

    def _on_show_unread_action(self):
        node = self.selected_tree_item
        self._show_articles(node)

    def _show_articles(self, node):
        _LOG.debug("WndMain._show_articles(%r(oid=%r))", type(node),
                   node.oid)
        self._ui.table_articles.selectionModel().clearSelection()
        unread_only = not self._ui.a_show_all.isChecked()
        session = db.Session()
        if isinstance(node, _models.SourceTreeNode):
            articles = larts.get_articles_by_source(node.oid, unread_only,
                                                    session=session)
        elif isinstance(node, _models.GroupTreeNode):
            articles = larts.get_articles_by_group(node.oid, unread_only,
                                                   session=session)
        elif isinstance(node, _models.SpecialTreeNode):
            if node.oid == _models.SPECIAL_ALL:
                articles = larts.get_all_articles(unread_only, session=session)
            elif node.oid == _models.SPECIAL_STARRED:
                articles = larts.get_starred_articles(False,
                                                      session=session)
            else:
                raise RuntimeError("invalid special tree item: %r", node)
        else:
            raise RuntimeError("invalid tree item: %r", node)
        self._list_model.set_items(articles)
        self._ui.table_articles.resizeColumnsToContents()

    def _set_window_pos_size(self):
        appcfg = self._appconfig
        width = appcfg.get('wnd_main.width')
        height = appcfg.get('wnd_main.height')
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
        # save expanded tree items
        self._save_expanded_tree_nodes()

    def _save_expanded_tree_nodes(self):
        _LOG.debug('_save_expanded_tree_nodes')
        model = self._tree_model
        expanded = [item.oid
                    for row, item in enumerate(model.root.children)
                    if self._ui.tree_subscriptions.isExpanded(
                        model.index(row, 0, None))]
        self._appconfig['wnd_main.tree.expanded'] = expanded

    def _restore_expanded_tree_nodes(self):
        # expand previous nodes
        for oid in self._appconfig.get('wnd_main.tree.expanded') or []:
            idx = self._tree_model.find_oid_index(oid)
            if idx:
                self._ui.tree_subscriptions.expand(idx[0])

    def _select_next_unread_source(self):
        # current selected
        model = self._ui.tree_subscriptions.selectionModel()
        curr_index = model.currentIndex()
        item = self._tree_model.node_from_index(curr_index)
        if isinstance(item, _models.SourceTreeNode):
            # try to find next unread node in this group
            curr_row = curr_index.row()
            group = item.parent
            for row in (range(curr_row + 1, len(group)) +
                        range(0, curr_row - 1)):
                if group.child_at_row(row).unread:
                    index = self._tree_model.index(row, 0,
                                                   curr_index.parent())
                    model.setCurrentIndex(
                        index, QtGui.QItemSelectionModel.ClearAndSelect)
                    return
            item = group
        # try to go to next group
        curr_row = item.row()
        root = self._tree_model.root
        for row in range(curr_row + 1, len(root)) + range(2, curr_row - 1):
            if root.child_at_row(row).unread:
                index = self._tree_model.index(row, 0, None)
                model.setCurrentIndex(
                    index, QtGui.QItemSelectionModel.ClearAndSelect)
                return
