# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/dialog_edit_web.ui'
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

class Ui_DialogAddWeb(object):
    def setupUi(self, DialogAddWeb):
        DialogAddWeb.setObjectName(_fromUtf8("DialogAddWeb"))
        DialogAddWeb.resize(410, 359)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogAddWeb.sizePolicy().hasHeightForWidth())
        DialogAddWeb.setSizePolicy(sizePolicy)
        DialogAddWeb.setModal(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DialogAddWeb)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DialogAddWeb)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.e_title = QtGui.QLineEdit(DialogAddWeb)
        self.e_title.setObjectName(_fromUtf8("e_title"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.e_title)
        self.label_2 = QtGui.QLabel(DialogAddWeb)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.e_url = QtGui.QLineEdit(DialogAddWeb)
        self.e_url.setObjectName(_fromUtf8("e_url"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.e_url)
        self.c_group = QtGui.QComboBox(DialogAddWeb)
        self.c_group.setObjectName(_fromUtf8("c_group"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.c_group)
        self.label_3 = QtGui.QLabel(DialogAddWeb)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtGui.QLabel(DialogAddWeb)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_4)
        self.e_xpath = QtGui.QPlainTextEdit(DialogAddWeb)
        self.e_xpath.setObjectName(_fromUtf8("e_xpath"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.e_xpath)
        self.label_5 = QtGui.QLabel(DialogAddWeb)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.e_interval = QtGui.QSpinBox(DialogAddWeb)
        self.e_interval.setMaximum(50000)
        self.e_interval.setSingleStep(5)
        self.e_interval.setObjectName(_fromUtf8("e_interval"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.e_interval)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel_btn = QtGui.QPushButton(DialogAddWeb)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.add_btn = QtGui.QPushButton(DialogAddWeb)
        self.add_btn.setDefault(True)
        self.add_btn.setObjectName(_fromUtf8("add_btn"))
        self.horizontalLayout.addWidget(self.add_btn)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogAddWeb)
        QtCore.QMetaObject.connectSlotsByName(DialogAddWeb)

    def retranslateUi(self, DialogAddWeb):
        DialogAddWeb.setWindowTitle(_translate("DialogAddWeb", "Add Web Page", None))
        self.label.setText(_translate("DialogAddWeb", "Title:", None))
        self.label_2.setText(_translate("DialogAddWeb", "URL:", None))
        self.label_3.setText(_translate("DialogAddWeb", "Group:", None))
        self.label_4.setText(_translate("DialogAddWeb", "XPath", None))
        self.label_5.setText(_translate("DialogAddWeb", "<html><head/><body><p>Update  interval [min]:</p></body></html>", None))
        self.cancel_btn.setText(_translate("DialogAddWeb", "Close", None))
        self.add_btn.setText(_translate("DialogAddWeb", "Add", None))

