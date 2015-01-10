# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mna/plugins/frm_sett_rss.ui'
#
# Created: Sat Jan 10 22:12:56 2015
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

class Ui_FrmSettRss(object):
    def setupUi(self, FrmSettRss):
        FrmSettRss.setObjectName(_fromUtf8("FrmSettRss"))
        FrmSettRss.resize(404, 81)
        FrmSettRss.setFrameShape(QtGui.QFrame.Panel)
        FrmSettRss.setFrameShadow(QtGui.QFrame.Raised)
        FrmSettRss.setLineWidth(0)
        self.verticalLayout = QtGui.QVBoxLayout(FrmSettRss)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(FrmSettRss)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setChecked(False)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_8 = QtGui.QLabel(self.groupBox_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_8)
        self.e_url = QtGui.QLineEdit(self.groupBox_2)
        self.e_url.setObjectName(_fromUtf8("e_url"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.e_url)
        self.horizontalLayout_2.addLayout(self.formLayout_2)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(FrmSettRss)
        QtCore.QMetaObject.connectSlotsByName(FrmSettRss)

    def retranslateUi(self, FrmSettRss):
        FrmSettRss.setWindowTitle(_translate("FrmSettRss", "Frame", None))
        self.groupBox_2.setTitle(_translate("FrmSettRss", "Main", None))
        self.label_8.setText(_translate("FrmSettRss", "URL:", None))

