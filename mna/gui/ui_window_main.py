# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/window_main.ui'
#
# Created: Sun Jan  4 22:51:29 2015
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

class Ui_WindowMain(object):
    def setupUi(self, WindowMain):
        WindowMain.setObjectName(_fromUtf8("WindowMain"))
        WindowMain.resize(910, 674)
        self.centralwidget = QtGui.QWidget(WindowMain)
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
        WindowMain.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(WindowMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 910, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_file = QtGui.QMenu(self.menubar)
        self.menu_file.setObjectName(_fromUtf8("menu_file"))
        self.menu_add = QtGui.QMenu(self.menubar)
        self.menu_add.setObjectName(_fromUtf8("menu_add"))
        self.menuArticles = QtGui.QMenu(self.menubar)
        self.menuArticles.setObjectName(_fromUtf8("menuArticles"))
        WindowMain.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(WindowMain)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        WindowMain.setStatusBar(self.statusbar)
        self.tool_bar = QtGui.QToolBar(WindowMain)
        self.tool_bar.setObjectName(_fromUtf8("tool_bar"))
        WindowMain.addToolBar(QtCore.Qt.TopToolBarArea, self.tool_bar)
        self.action_refresh = QtGui.QAction(WindowMain)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/main/reload.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_refresh.setIcon(icon)
        self.action_refresh.setObjectName(_fromUtf8("action_refresh"))
        self.action_exit = QtGui.QAction(WindowMain)
        self.action_exit.setObjectName(_fromUtf8("action_exit"))
        self.add_group_action = QtGui.QAction(WindowMain)
        self.add_group_action.setObjectName(_fromUtf8("add_group_action"))
        self.add_rss_action = QtGui.QAction(WindowMain)
        self.add_rss_action.setObjectName(_fromUtf8("add_rss_action"))
        self.add_web_action = QtGui.QAction(WindowMain)
        self.add_web_action.setObjectName(_fromUtf8("add_web_action"))
        self.mark_all_read_action = QtGui.QAction(WindowMain)
        self.mark_all_read_action.setObjectName(_fromUtf8("mark_all_read_action"))
        self.show_unread_action = QtGui.QAction(WindowMain)
        self.show_unread_action.setCheckable(True)
        self.show_unread_action.setChecked(True)
        self.show_unread_action.setObjectName(_fromUtf8("show_unread_action"))
        self.menu_file.addAction(self.action_exit)
        self.menu_add.addAction(self.add_group_action)
        self.menu_add.addSeparator()
        self.menu_add.addAction(self.add_rss_action)
        self.menu_add.addAction(self.add_web_action)
        self.menuArticles.addAction(self.mark_all_read_action)
        self.menuArticles.addAction(self.show_unread_action)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_add.menuAction())
        self.menubar.addAction(self.menuArticles.menuAction())
        self.tool_bar.addAction(self.action_refresh)

        self.retranslateUi(WindowMain)
        QtCore.QMetaObject.connectSlotsByName(WindowMain)

    def retranslateUi(self, WindowMain):
        WindowMain.setWindowTitle(_translate("WindowMain", "MainWindow", None))
        self.menu_file.setTitle(_translate("WindowMain", "File", None))
        self.menu_add.setTitle(_translate("WindowMain", "Add", None))
        self.menuArticles.setTitle(_translate("WindowMain", "Articles", None))
        self.tool_bar.setWindowTitle(_translate("WindowMain", "toolBar", None))
        self.action_refresh.setText(_translate("WindowMain", "Refresh", None))
        self.action_refresh.setToolTip(_translate("WindowMain", "Refresh all subscriptions", None))
        self.action_exit.setText(_translate("WindowMain", "Exit", None))
        self.action_exit.setShortcut(_translate("WindowMain", "Ctrl+Q", None))
        self.add_group_action.setText(_translate("WindowMain", "Add group", None))
        self.add_rss_action.setText(_translate("WindowMain", "Add RSS", None))
        self.add_web_action.setText(_translate("WindowMain", "Add Web", None))
        self.mark_all_read_action.setText(_translate("WindowMain", "Mark &all read", None))
        self.mark_all_read_action.setShortcut(_translate("WindowMain", "Alt+A", None))
        self.show_unread_action.setText(_translate("WindowMain", "Show unread only", None))

from PyQt4 import QtWebKit
import resources_rc
