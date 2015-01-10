# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/dlg_edit_group.ui'
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

class Ui_DlgEditGroup(object):
    def setupUi(self, DlgEditGroup):
        DlgEditGroup.setObjectName(_fromUtf8("DlgEditGroup"))
        DlgEditGroup.resize(382, 76)
        DlgEditGroup.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DlgEditGroup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DlgEditGroup)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.name_edit = QtGui.QLineEdit(DlgEditGroup)
        self.name_edit.setObjectName(_fromUtf8("name_edit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.name_edit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel_btn = QtGui.QPushButton(DlgEditGroup)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.add_btn = QtGui.QPushButton(DlgEditGroup)
        self.add_btn.setDefault(True)
        self.add_btn.setObjectName(_fromUtf8("add_btn"))
        self.horizontalLayout.addWidget(self.add_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(DlgEditGroup)
        QtCore.QMetaObject.connectSlotsByName(DlgEditGroup)

    def retranslateUi(self, DlgEditGroup):
        DlgEditGroup.setWindowTitle(_translate("DlgEditGroup", "Add Group", None))
        self.label.setText(_translate("DlgEditGroup", "Name:", None))
        self.name_edit.setPlaceholderText(_translate("DlgEditGroup", "New group name", None))
        self.cancel_btn.setText(_translate("DlgEditGroup", "Close", None))
        self.add_btn.setText(_translate("DlgEditGroup", "Add", None))

