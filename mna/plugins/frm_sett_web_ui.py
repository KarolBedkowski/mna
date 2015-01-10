# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mna/plugins/frm_sett_web.ui'
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

class Ui_FrmSettWeb(object):
    def setupUi(self, FrmSettWeb):
        FrmSettWeb.setObjectName(_fromUtf8("FrmSettWeb"))
        FrmSettWeb.resize(404, 295)
        FrmSettWeb.setFrameShape(QtGui.QFrame.StyledPanel)
        FrmSettWeb.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout = QtGui.QVBoxLayout(FrmSettWeb)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(FrmSettWeb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
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
        self.groupBox = QtGui.QGroupBox(FrmSettWeb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.rb_scan_page = QtGui.QRadioButton(self.groupBox)
        self.rb_scan_page.setChecked(True)
        self.rb_scan_page.setObjectName(_fromUtf8("rb_scan_page"))
        self.verticalLayout_4.addWidget(self.rb_scan_page)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(24, -1, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_3.addWidget(self.label_6)
        self.sb_similarity_ratio = QtGui.QDoubleSpinBox(self.groupBox)
        self.sb_similarity_ratio.setMaximum(100.0)
        self.sb_similarity_ratio.setObjectName(_fromUtf8("sb_similarity_ratio"))
        self.horizontalLayout_3.addWidget(self.sb_similarity_ratio)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.verticalLayout_4.addLayout(self.verticalLayout_5)
        self.rb_scan_parts = QtGui.QRadioButton(self.groupBox)
        self.rb_scan_parts.setObjectName(_fromUtf8("rb_scan_parts"))
        self.verticalLayout_4.addWidget(self.rb_scan_parts)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(24, -1, -1, -1)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.e_xpath = QtGui.QPlainTextEdit(self.groupBox)
        self.e_xpath.setObjectName(_fromUtf8("e_xpath"))
        self.horizontalLayout_4.addWidget(self.e_xpath)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(FrmSettWeb)
        QtCore.QMetaObject.connectSlotsByName(FrmSettWeb)

    def retranslateUi(self, FrmSettWeb):
        FrmSettWeb.setWindowTitle(_translate("FrmSettWeb", "Frame", None))
        self.groupBox_2.setTitle(_translate("FrmSettWeb", "Main", None))
        self.label_8.setText(_translate("FrmSettWeb", "URL:", None))
        self.groupBox.setTitle(_translate("FrmSettWeb", "Options", None))
        self.rb_scan_page.setText(_translate("FrmSettWeb", "Scan whole page", None))
        self.label_6.setText(_translate("FrmSettWeb", "Minimal changes ratio:", None))
        self.sb_similarity_ratio.setToolTip(_translate("FrmSettWeb", "<html><head/><body><p>Minimal changes to treat page as changed - 0 = any changes, 100 = all page must be changed</p></body></html>", None))
        self.sb_similarity_ratio.setSuffix(_translate("FrmSettWeb", "%", None))
        self.rb_scan_parts.setText(_translate("FrmSettWeb", "Find page parts", None))
        self.label_4.setText(_translate("FrmSettWeb", "XPath:", None))

