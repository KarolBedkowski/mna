# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui


class DlgInfo(QtGui.QDialog):
    def __init__(self, parent, title, info):
        QtGui.QDialog.__init__(self, parent)  # pylint:disable=no-member
        self.setup_ui()
        self.resize(800, 600)
        self.setWindowTitle(title)
        self._e_info.setText(info)

    def setup_ui(self):
        layout = QtGui.QVBoxLayout(self)
        self._e_info = QtGui.QTextEdit(self)
        layout.addWidget(self._e_info)
        btn_box = QtGui.QDialogButtonBox(self)
        btn_box.setOrientation(QtCore.Qt.Horizontal)
        btn_box.setStandardButtons(QtGui.QDialogButtonBox.Close)
        layout.addWidget(btn_box)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
