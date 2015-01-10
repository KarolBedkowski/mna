# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/gui/wzd_add_src.ui'
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

class Ui_WizardAddSource(object):
    def setupUi(self, WizardAddSource):
        WizardAddSource.setObjectName(_fromUtf8("WizardAddSource"))
        WizardAddSource.resize(481, 375)
        WizardAddSource.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        WizardAddSource.setWizardStyle(QtGui.QWizard.ClassicStyle)
        self.wiz_page1 = QtGui.QWizardPage()
        self.wiz_page1.setSubTitle(_fromUtf8(""))
        self.wiz_page1.setObjectName(_fromUtf8("wiz_page1"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.wiz_page1)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.frame_2 = QtGui.QFrame(self.wiz_page1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.frame_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.cb_source_type = QtGui.QComboBox(self.frame_2)
        self.cb_source_type.setObjectName(_fromUtf8("cb_source_type"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cb_source_type)
        self.verticalLayout_4.addLayout(self.formLayout)
        self.groupBox_2 = QtGui.QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.l_main_opt = QtGui.QVBoxLayout()
        self.l_main_opt.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.l_main_opt.setObjectName(_fromUtf8("l_main_opt"))
        self.verticalLayout_5.addLayout(self.l_main_opt)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        self.verticalLayout_4.setStretch(1, 1)
        self.verticalLayout_3.addWidget(self.frame_2)
        WizardAddSource.addPage(self.wiz_page1)
        self.wiz_page2 = QtGui.QWizardPage()
        self.wiz_page2.setObjectName(_fromUtf8("wiz_page2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.wiz_page2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.l_src_opt = QtGui.QVBoxLayout()
        self.l_src_opt.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.l_src_opt.setObjectName(_fromUtf8("l_src_opt"))
        self.verticalLayout_2.addLayout(self.l_src_opt)
        WizardAddSource.addPage(self.wiz_page2)
        self.wiz_page3 = QtGui.QWizardPage()
        self.wiz_page3.setSubTitle(_fromUtf8(""))
        self.wiz_page3.setObjectName(_fromUtf8("wiz_page3"))
        self.verticalLayout = QtGui.QVBoxLayout(self.wiz_page3)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.wiz_page3)
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
        self.e_interval.setMinimum(1)
        self.e_interval.setMaximum(50000)
        self.e_interval.setSingleStep(5)
        self.e_interval.setObjectName(_fromUtf8("e_interval"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.e_interval)
        self.verticalLayout.addWidget(self.groupBox)
        WizardAddSource.addPage(self.wiz_page3)

        self.retranslateUi(WizardAddSource)
        QtCore.QMetaObject.connectSlotsByName(WizardAddSource)

    def retranslateUi(self, WizardAddSource):
        WizardAddSource.setWindowTitle(_translate("WizardAddSource", "Add Source", None))
        self.wiz_page1.setTitle(_translate("WizardAddSource", "Source", None))
        self.label.setText(_translate("WizardAddSource", "Source type:", None))
        self.groupBox_2.setTitle(_translate("WizardAddSource", "Main parameters", None))
        self.wiz_page2.setTitle(_translate("WizardAddSource", "Source options", None))
        self.wiz_page3.setTitle(_translate("WizardAddSource", "Additional options", None))
        self.groupBox.setTitle(_translate("WizardAddSource", "Loadin options:", None))
        self.label_2.setText(_translate("WizardAddSource", "Update interval [min]:", None))

