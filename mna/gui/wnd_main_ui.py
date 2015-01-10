# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/wnd_main.ui'
#
# Created: Sat Jan 10 22:20:31 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_WndMain(object):
    def setupUi(self, WndMain):
        WndMain.setObjectName(_fromUtf8("WndMain"))
        WndMain.resize(910, 674)
        self.centralwidget = QtGui.QWidget(WndMain)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.tree_subscriptions = QtGui.QTreeView(self.splitter_2)
        self.tree_subscriptions.setObjectName(_fromUtf8("tree_subscriptions"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.table_articles = QtGui.QTableView(self.splitter)
        self.table_articles.setAlternatingRowColors(True)
        self.table_articles.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table_articles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_articles.setShowGrid(False)
        self.table_articles.setSortingEnabled(True)
        self.table_articles.setObjectName(_fromUtf8("table_articles"))
        self.table_articles.horizontalHeader().setVisible(True)
        self.table_articles.horizontalHeader().setCascadingSectionResizes(True)
        self.table_articles.horizontalHeader().setMinimumSectionSize(27)
        self.table_articles.verticalHeader().setVisible(False)
        self.table_articles.verticalHeader().setCascadingSectionResizes(True)
        self.table_articles.verticalHeader().setDefaultSectionSize(20)
        self.table_articles.verticalHeader().setMinimumSectionSize(10)
        self.article_view = QtWebKit.QWebView(self.splitter)
        self.article_view.setObjectName(_fromUtf8("article_view"))
        self.verticalLayout.addWidget(self.splitter_2)
        WndMain.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(WndMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 910, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_file = QtGui.QMenu(self.menubar)
        self.menu_file.setObjectName(_fromUtf8("menu_file"))
        self.menu_add = QtGui.QMenu(self.menubar)
        self.menu_add.setObjectName(_fromUtf8("menu_add"))
        self.menuArticles = QtGui.QMenu(self.menubar)
        self.menuArticles.setObjectName(_fromUtf8("menuArticles"))
        WndMain.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(WndMain)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        WndMain.setStatusBar(self.statusbar)
        self.tool_bar = QtGui.QToolBar(WndMain)
        self.tool_bar.setObjectName(_fromUtf8("tool_bar"))
        WndMain.addToolBar(QtCore.Qt.TopToolBarArea, self.tool_bar)
        self.action_refresh = QtGui.QAction(WndMain)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/main/reload.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_refresh.setIcon(icon)
        self.action_refresh.setObjectName(_fromUtf8("action_refresh"))
        self.action_exit = QtGui.QAction(WndMain)
        self.action_exit.setObjectName(_fromUtf8("action_exit"))
        self.add_group_action = QtGui.QAction(WndMain)
        self.add_group_action.setObjectName(_fromUtf8("add_group_action"))
        self.add_rss_action = QtGui.QAction(WndMain)
        self.add_rss_action.setObjectName(_fromUtf8("add_rss_action"))
        self.add_src_action = QtGui.QAction(WndMain)
        self.add_src_action.setObjectName(_fromUtf8("add_src_action"))
        self.mark_all_read_action = QtGui.QAction(WndMain)
        self.mark_all_read_action.setObjectName(_fromUtf8("mark_all_read_action"))
        self.show_unread_action = QtGui.QAction(WndMain)
        self.show_unread_action.setCheckable(True)
        self.show_unread_action.setChecked(True)
        self.show_unread_action.setObjectName(_fromUtf8("show_unread_action"))
        self.menu_file.addAction(self.action_exit)
        self.menu_add.addAction(self.add_group_action)
        self.menu_add.addSeparator()
        self.menu_add.addAction(self.add_src_action)
        self.menuArticles.addAction(self.mark_all_read_action)
        self.menuArticles.addAction(self.show_unread_action)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menuArticles.menuAction())
        self.menubar.addAction(self.menu_add.menuAction())
        self.tool_bar.addAction(self.action_refresh)

        self.retranslateUi(WndMain)
        QtCore.QMetaObject.connectSlotsByName(WndMain)

    def retranslateUi(self, WndMain):
        WndMain.setWindowTitle(_translate("WndMain", "MainWindow", None))
        self.menu_file.setTitle(_translate("WndMain", "File", None))
        self.menu_add.setTitle(_translate("WndMain", "Add", None))
        self.menuArticles.setTitle(_translate("WndMain", "Articles", None))
        self.tool_bar.setWindowTitle(_translate("WndMain", "toolBar", None))
        self.action_refresh.setText(_translate("WndMain", "Refresh", None))
        self.action_refresh.setToolTip(_translate("WndMain", "Refresh all subscriptions", None))
        self.action_exit.setText(_translate("WndMain", "Exit", None))
        self.action_exit.setShortcut(_translate("WndMain", "Ctrl+Q", None))
        self.add_group_action.setText(_translate("WndMain", "Add group", None))
        self.add_rss_action.setText(_translate("WndMain", "Add RSS", None))
        self.add_src_action.setText(_translate("WndMain", "Add Source", None))
        self.mark_all_read_action.setText(_translate("WndMain", "Mark &all read", None))
        self.mark_all_read_action.setShortcut(_translate("WndMain", "Alt+A", None))
        self.show_unread_action.setText(_translate("WndMain", "Show unread only", None))

from PyQt4 import QtWebKit
import resources_rc
