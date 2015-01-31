# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
""" Main application window.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-30"

import os
import sys
import logging
import webbrowser
import urllib2

from PyQt4 import QtGui, QtWebKit, QtCore

from mna.gui._models import arts_model, subs_model
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

_LOG = logging.getLogger(__name__)

assert resources_rc


# pylint: disable=too-few-public-methods
class WndMain(QtGui.QMainWindow):  # pylint: disable=no-member
    """ Main Window class. """

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)  # pylint: disable=no-member
        self._appconfig = AppConfig()
        self._current_article = None
        self._ui = wnd_main_ui.Ui_WndMain()
        self._ui.setupUi(self)
        self._setup()
        self._bind()
        self._set_window_pos_size()
        self._restore_expanded_tree_nodes()

    # pylint: disable=no-member
    def _setup(self):
        # models
        # group & sources tree
        self._subs_model = subs_model.TreeModel()
        self._ui.tv_subs.setModel(self._subs_model)
        # articles list with sorting proxy
        self._arts_list_model = arts_model.ListModel()
        self._list_model_proxy = QtGui.QSortFilterProxyModel(self)
        self._list_model_proxy.setSourceModel(self._arts_list_model)
        self._ui.tv_articles.setModel(self._list_model_proxy)
        self._ui.tv_articles.setSortingEnabled(True)
        self._ui.tv_articles.sortByColumn(4, QtCore.Qt.AscendingOrder)
        # popup menu
        self._ui.tv_subs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # handle links
        self._ui.article_view.page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)
        # add search field to toolbar
        self._t_search = QtGui.QLineEdit(self)
        self._t_search.setPlaceholderText(self.tr("Search"))
        self._t_search.setMaximumWidth(200)
        self._ui.toolbar.addWidget(self._t_search)

    def _bind(self):
        # actions
        self._ui.a_update.triggered.connect(self._on_action_update)
        self._ui.a_toggle_sel_articles_read.triggered.connect(
            self._on_action_toggle_read)
        self._ui.a_preferences.triggered.connect(self._on_action_preferences)
        self._ui.a_mark_read.triggered.connect(self._on_action_mark_all_read)
        self._ui.a_add_group.triggered.connect(self._on_action_add_group)
        self._ui.a_add_source.triggered.connect(self._on_action_add_source)
        self._ui.a_show_all.triggered.connect(self._on_action_show_all)
        # groups & sources tree
        self._ui.tv_subs.selectionModel().selectionChanged.connect(
            self._on_subs_sel_changed)
        self._ui.tv_subs.customContextMenuRequested.connect(
            self._on_subs_contextmenu)
        # article list
        self._ui.tv_articles.selectionModel().selectionChanged.connect(
            self._on_art_sel_changed)
        self._ui.tv_articles.clicked.connect(self._on_art_clicked)
        # article view - webkit
        self._ui.article_view.linkClicked.connect(self._on_art_link_clicked)
        # otker
        self._t_search.returnPressed.connect(self._on_search_return)
        # global events
        messenger.MESSENGER.source_updated.connect(self._on_source_updated)
        messenger.MESSENGER.group_updated.connect(self._on_group_updated)
        messenger.MESSENGER.announce.connect(self._on_announce)

    @property
    def _selected_subscription(self):
        """ Get current selected item in subscriptions tree. """
        model = self._ui.tv_subs.selectionModel()
        index = model.currentIndex()
        return self._subs_model.node_from_index(index)

    @property
    def _selected_article(self):
        """ Get current selected article """
        index = self._ui.tv_articles.selectionModel().currentIndex()
        if index:
            return self._arts_list_model.node_from_index(index)

    def closeEvent(self, event):
        self._save_window_pos_size()
        event.accept()

    def _on_subs_sel_changed(self, index):
        """ Handle group/source selection."""
        if not index.count():
            return
        index = index.indexes()[0]
        node = self._subs_model.node_from_index(index)
        assert node.oid
        self._show_articles(node)

    def _on_subs_contextmenu(self, position):
        """ Show context menu for subscriptions tree """
        selected = self._selected_subscription
        if isinstance(selected, subs_model.SpecialTreeNode):
            # no menu on special nodes
            return
        menu = QtGui.QMenu()
        menu.addAction(self.tr("Edit")).triggered.\
                connect(self._on_subs_cmenu_edit)
        menu.addAction(self.tr("Delete")).triggered.\
                connect(self._on_subs_cmenu_del)
        if isinstance(selected, subs_model.SourceTreeNode):
            menu.addAction(self.tr("Info")).triggered.\
                    connect(self._on_subs_cmenu_info)
        menu.exec_(self._ui.tv_subs.viewport(). mapToGlobal(position))

    def _on_subs_cmenu_edit(self):
        node = self._selected_subscription
        assert node and not isinstance(node, subs_model.SpecialTreeNode), \
            'Invalid node'
        if isinstance(node, subs_model.SourceTreeNode):
            dlg = dlg_source_edit.DlgSourceEdit(self, node.oid)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                messenger.MESSENGER.emit_source_updated(
                    dlg.source.oid, dlg.source.group_id)
        elif isinstance(node, subs_model.GroupTreeNode):
            dlg = dlg_edit_group.DlgEditGroup(self, node.oid)
            if dlg.exec_() == QtGui.QDialog.Accepted:
                messenger.MESSENGER.emit_group_updated(node.oid)
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_subs_cmenu_del(self):
        node = self._selected_subscription
        assert node and not isinstance(node, subs_model.SpecialTreeNode), \
            'Invalid node'
        if QtGui.QMessageBox.question(
                self, self.tr("Delete"),
                self.tr("Delete selected item?"),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) \
                == QtGui.QMessageBox.No:
            return

        model = self._ui.tv_subs.selectionModel()
        model.clearSelection()

        if isinstance(node, subs_model.SourceTreeNode):
            if sources.delete_source(node.oid):
                self._refresh_tree()
        elif isinstance(node, subs_model.GroupTreeNode):
            if groups.delete_group(node.oid):
                self._refresh_tree()
        else:
            raise RuntimeError("invalid object type %r", node)

    def _on_subs_cmenu_info(self):
        node = self._selected_subscription
        if node is None or not isinstance(node, subs_model.SourceTreeNode):
            return
        dlg = dlg_source_info.DlgSourceInfo(self, node.oid)
        dlg.exec_()

    def _on_art_clicked(self, index):
        """ Handle article click -  star/flag articles. """
        index = self._ui.tv_articles.selectionModel().currentIndex()
        item = self._arts_list_model.node_from_index(index)
        _LOG.debug("_on_art_clicked %r %r", item.oid, index.column())
        article = None
        if index.column() == 0:  # readed
            article = list(larts.toggle_articles_read([item.oid]))[0]
        elif index.column() == 1:  # starred
            article = list(larts.toggle_articles_starred([item.oid]))[0]
        if article:
            self._arts_list_model.update_item(article)
            self._subs_model.update_source(
                article.source_id, article.source.group_id)

    def _on_art_sel_changed(self, _index):
        """ Handle article selection -  show article in HtmlView. """
        item = self._selected_article
        _LOG.debug("_on_art_sel_changed %r", item.oid)
        session = db.Session()
        article, content = larts.get_article_content(
            item.oid, True, session=session)
        self._current_article = article
        self._ui.article_view.setHtml(content)
        self._arts_list_model.update_item(article)
        self._subs_model.update_source(
            article.source_id, article.source.group_id)

    def _on_action_update(self):  # pylint: disable=no-self-use
        sources.force_refresh_all()

    def _on_action_add_group(self):
        dlg = dlg_edit_group.DlgEditGroup(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_action_add_source(self):
        dlg = wzd_add_src.WzdAddSrc(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._refresh_tree()

    def _on_action_mark_all_read(self):
        """ Mark all articles in current group or source read. """
        sources_to_mark = []
        node = self._selected_subscription
        if node is None:
            return
        if isinstance(node, subs_model.SourceTreeNode):
            sources_to_mark = [(node.oid, node.parent.oid)]
        elif isinstance(node, subs_model.GroupTreeNode):
            sources_to_mark = [(child.oid, node.oid)
                               for child in node.children]
        else:
            self._select_next_unread_source()
            return
        updated, src_updated = sources.mark_source_read(
            [src[0] for src in sources_to_mark])
        # when updated - emit signals for refresh tree/list
        if updated > 0:
            for source_oid, group_oid in sources_to_mark:
                # send signals only for real updated sources
                if src_updated[source_oid] > 0:
                    messenger.MESSENGER.emit_source_updated(
                        source_oid, group_oid)
            messenger.MESSENGER.emit_group_updated(sources_to_mark[0][1])
        self._select_next_unread_source()

    def _on_action_toggle_read(self):
        """ Toggle selected articles read. """
        rows = self._ui.tv_articles.selectionModel().selectedRows()
        if not rows:
            return
        articles = [self._arts_list_model.node_from_index(index).oid
                    for index in rows]
        toggled = list(larts.toggle_articles_read(articles))
        if not toggled:
            return
        updated_sources = {}
        for article in toggled:
            self._arts_list_model.update_item(article)
            updated_sources[article.source_id] = article.source.group_id
        for source_id, group_id in updated_sources.iteritems():
            self._subs_model.update_source(source_id, group_id)

    def _on_action_preferences(self):
        dlg = dlg_preferences.DlgPreferences(self)
        dlg.exec_()

    def _on_action_show_all(self):
        unread_only = not self._ui.a_show_all.isChecked()
        model = self._arts_list_model
        model.set_data_source(unread_only=unread_only)
        model.refresh()

    def _on_search_return(self):
        # switch to search item
        index = self._subs_model.get_index_of_special(
            subs_model.SPECIAL_SEARCH)
        model = self._ui.tv_subs.selectionModel()
        if model.currentIndex() == index:
            text = self._t_search.text()
            amodel = self._arts_list_model
            amodel.set_data_source(arts_model.DS_SEARCH, text)
            session = db.Session()
            amodel.refresh(session)
        else:
            model.setCurrentIndex(
                index, QtGui.QItemSelectionModel.ClearAndSelect)

    def _on_art_link_clicked(self, url):
        url = unicode(url.toString())
        art_url = self._current_article.link
        if art_url:
            url = urllib2.urlparse.urljoin(art_url, url)
        if sys.platform.startswith('linux'):
            os.popen('xdg-open "%s"' % url)
        else:
            webbrowser.open(url)

    @QtCore.pyqtSlot(int, int)
    def _on_source_updated(self, source_id, group_id):
        """ Handle  source update event. """
        _LOG.debug("Source updated %r, %r", source_id, group_id)
        if not source_id or not group_id:
            return
        self._subs_model.update_source(source_id, group_id)
        # refresh article list when updated source is displayed
        model = self._arts_list_model
        if model.ds_kind == arts_model.DS_SOURCE and model.ds_oid == source_id:
            self._arts_list_model.refresh()
        elif model.ds_kind == arts_model.DS_GROUP and model.ds_oid == group_id:
            self._arts_list_model.refresh()

    @QtCore.pyqtSlot(unicode)
    def _on_announce(self, message):
        self.statusBar().showMessage(message, 10000)

    @QtCore.pyqtSlot(int)
    def _on_group_updated(self, group_id):
        """ Handle group update event. """
        _LOG.debug("Group updated %r", group_id)
        self._subs_model.update_group(group_id)
        node = self._selected_subscription
        if node is None:
            return
        if isinstance(node, subs_model.GroupTreeNode) and group_id == node.oid:
            self._arts_list_model.refresh()

    def _refresh_tree(self):
        """ Refresh tree; keep expanded nodes """
        self._save_expanded_tree_nodes()
        self._subs_model.refresh()
        self._restore_expanded_tree_nodes()

    def _show_articles(self, node):
        _LOG.debug("WndMain._show_articles(%r(oid=%r))", type(node), node.oid)
        self._ui.tv_articles.selectionModel().clearSelection()
        unread_only = not self._ui.a_show_all.isChecked()
        model = self._arts_list_model
        if isinstance(node, subs_model.SourceTreeNode):
            model.set_data_source(arts_model.DS_SOURCE, node.oid, unread_only)
        elif isinstance(node, subs_model.GroupTreeNode):
            model.set_data_source(arts_model.DS_GROUP, node.oid, unread_only)
        elif isinstance(node, subs_model.SpecialTreeNode):
            if node.oid == subs_model.SPECIAL_ALL:
                model.set_data_source(arts_model.DS_ALL, None, unread_only)
            elif node.oid == subs_model.SPECIAL_STARRED:
                model.set_data_source(arts_model.DS_STARRED)
            elif node.oid == subs_model.SPECIAL_SEARCH:
                text = self._t_search.text()
                model.set_data_source(arts_model.DS_SEARCH, text)
            else:
                raise RuntimeError("invalid special tree item: %r", node)
        else:
            raise RuntimeError("invalid tree item: %r", node)
        session = db.Session()
        model.refresh(session)
        self._ui.tv_articles.resizeColumnsToContents()

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
        model = self._subs_model
        expanded = [
            item.oid
            for row, item in enumerate(model.root.children)
            if self._ui.tv_subs.isExpanded(model.index(row, 0, None))]
        self._appconfig['wnd_main.tree.expanded'] = expanded

    def _restore_expanded_tree_nodes(self):
        # expand previous nodes
        for oid in self._appconfig.get('wnd_main.tree.expanded') or []:
            idx = self._subs_model.find_oid_index(oid)
            if idx:
                self._ui.tv_subs.expand(idx[0])

    def _select_next_unread_source(self):
        # current selected
        model = self._ui.tv_subs.selectionModel()
        curr_index = model.currentIndex()
        item = self._subs_model.node_from_index(curr_index)
        if isinstance(item, subs_model.SourceTreeNode):
            # try to find next unread node in this group
            curr_row = curr_index.row()
            group = item.parent
            row, node = group.get_first_unread(curr_row)
            if row is not None:
                index = self._subs_model.index(row, 0, curr_index.parent())
                model.setCurrentIndex(
                    index, QtGui.QItemSelectionModel.ClearAndSelect)
                return
            # select first unread source in next group
            sel_group = group.row()
            row, group = self._subs_model.root.get_first_unread(
                sel_group, True, 3)
            if row is not None:
                # found group with unread articles, select first unread source
                row, node = group.get_first_unread()
                assert row is not None, 'found unread group but no sources'
                index = self._subs_model.createIndex(row, 0, node)
                model.setCurrentIndex(
                    index, QtGui.QItemSelectionModel.ClearAndSelect)
            return
        # try to go to next group
        curr_row = item.row()
        row, _ = self._subs_model.root.get_first_unread(curr_row, True, 3)
        if row is not None:
            index = self._subs_model.index(row, 0, None)
            model.setCurrentIndex(
                index, QtGui.QItemSelectionModel.ClearAndSelect)
