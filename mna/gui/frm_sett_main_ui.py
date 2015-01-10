# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/frm_sett_main.ui'
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

class Ui_FrmSettMain(object):
    def setupUi(self, FrmSettMain):
        FrmSettMain.setObjectName(_fromUtf8("FrmSettMain"))
        FrmSettMain.resize(477, 85)
        FrmSettMain.setFrameShape(QtGui.QFrame.Panel)
        FrmSettMain.setFrameShadow(QtGui.QFrame.Plain)
        FrmSettMain.setLineWidth(0)
        self.formLayout = QtGui.QFormLayout(FrmSettMain)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_7 = QtGui.QLabel(FrmSettMain)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self.e_title = QtGui.QLineEdit(FrmSettMain)
        self.e_title.setObjectName(_fromUtf8("e_title"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.e_title)
        self.label_10 = QtGui.QLabel(FrmSettMain)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_10)
        self.c_group = QtGui.QComboBox(FrmSettMain)
        self.c_group.setObjectName(_fromUtf8("c_group"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.c_group)

        self.retranslateUi(FrmSettMain)
        QtCore.QMetaObject.connectSlotsByName(FrmSettMain)

    def retranslateUi(self, FrmSettMain):
        FrmSettMain.setWindowTitle(_translate("FrmSettMain", "Frame", None))
        self.label_7.setText(_translate("FrmSettMain", "Title:", None))
        self.label_10.setText(_translate("FrmSettMain", "Group:", None))

