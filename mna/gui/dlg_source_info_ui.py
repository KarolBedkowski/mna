# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/dlg_source_info.ui'
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

class Ui_DlgSourceInfo(object):
    def setupUi(self, DlgSourceInfo):
        DlgSourceInfo.setObjectName(_fromUtf8("DlgSourceInfo"))
        DlgSourceInfo.resize(570, 442)
        DlgSourceInfo.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.verticalLayout = QtGui.QVBoxLayout(DlgSourceInfo)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(DlgSourceInfo)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lv_info = QtGui.QTreeView(self.tab)
        self.lv_info.setObjectName(_fromUtf8("lv_info"))
        self.horizontalLayout.addWidget(self.lv_info)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lv_logs = QtGui.QTreeView(self.tab_2)
        self.lv_logs.setObjectName(_fromUtf8("lv_logs"))
        self.horizontalLayout_2.addWidget(self.lv_logs)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(DlgSourceInfo)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgSourceInfo)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DlgSourceInfo.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgSourceInfo.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgSourceInfo)

    def retranslateUi(self, DlgSourceInfo):
        DlgSourceInfo.setWindowTitle(_translate("DlgSourceInfo", "Source Info", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("DlgSourceInfo", "Info", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("DlgSourceInfo", "Logs", None))

