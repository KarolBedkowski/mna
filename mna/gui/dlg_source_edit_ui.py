# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/dlg_source_edit.ui'
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

class Ui_DlgSourceEdit(object):
    def setupUi(self, DlgSourceEdit):
        DlgSourceEdit.setObjectName(_fromUtf8("DlgSourceEdit"))
        DlgSourceEdit.resize(603, 282)
        self.verticalLayout = QtGui.QVBoxLayout(DlgSourceEdit)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(DlgSourceEdit)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.l_main_opt = QtGui.QVBoxLayout()
        self.l_main_opt.setObjectName(_fromUtf8("l_main_opt"))
        self.verticalLayout_2.addLayout(self.l_main_opt)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.l_src_opt = QtGui.QVBoxLayout()
        self.l_src_opt.setObjectName(_fromUtf8("l_src_opt"))
        self.verticalLayout_3.addLayout(self.l_src_opt)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox = QtGui.QGroupBox(self.tab_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.e_interval = QtGui.QSpinBox(self.groupBox)
        self.e_interval.setMaximum(50000)
        self.e_interval.setSingleStep(5)
        self.e_interval.setObjectName(_fromUtf8("e_interval"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.e_interval)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(DlgSourceEdit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgSourceEdit)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DlgSourceEdit.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgSourceEdit.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgSourceEdit)

    def retranslateUi(self, DlgSourceEdit):
        DlgSourceEdit.setWindowTitle(_translate("DlgSourceEdit", "Dialog", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("DlgSourceEdit", "Main", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("DlgSourceEdit", "Source", None))
        self.groupBox.setTitle(_translate("DlgSourceEdit", "Loadin options:", None))
        self.label_2.setText(_translate("DlgSourceEdit", "Update interval [min]:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("DlgSourceEdit", "Additional", None))

