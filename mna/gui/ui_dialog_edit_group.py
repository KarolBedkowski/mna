# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/dialog_edit_group.ui'
#
# Created: Sun Jan  4 15:23:28 2015
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

class Ui_DialogAddGroup(object):
    def setupUi(self, DialogAddGroup):
        DialogAddGroup.setObjectName(_fromUtf8("DialogAddGroup"))
        DialogAddGroup.resize(382, 76)
        DialogAddGroup.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DialogAddGroup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DialogAddGroup)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.name_edit = QtGui.QLineEdit(DialogAddGroup)
        self.name_edit.setObjectName(_fromUtf8("name_edit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.name_edit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel_btn = QtGui.QPushButton(DialogAddGroup)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.add_btn = QtGui.QPushButton(DialogAddGroup)
        self.add_btn.setDefault(True)
        self.add_btn.setObjectName(_fromUtf8("add_btn"))
        self.horizontalLayout.addWidget(self.add_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogAddGroup)
        QtCore.QMetaObject.connectSlotsByName(DialogAddGroup)

    def retranslateUi(self, DialogAddGroup):
        DialogAddGroup.setWindowTitle(_translate("DialogAddGroup", "Add Group", None))
        self.label.setText(_translate("DialogAddGroup", "Name:", None))
        self.name_edit.setPlaceholderText(_translate("DialogAddGroup", "New group name", None))
        self.cancel_btn.setText(_translate("DialogAddGroup", "Close", None))
        self.add_btn.setText(_translate("DialogAddGroup", "Add", None))

