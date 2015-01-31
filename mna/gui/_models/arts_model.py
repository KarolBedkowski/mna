# -*- coding: utf-8 -*-
""" Qt models - article list

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-31"


import logging

from PyQt4 import QtCore, QtGui

_LOG = logging.getLogger(__name__)


class ListItem(object):
    __slots__ = ('oid', '_cols', 'font', 'color')

    def __init__(self, src):
        self.oid = src.oid
        self.font = QtCore.QVariant()
        self.color = QtCore.QVariant()
        self.update(src)

    def update(self, src):
        if src.read:
            self.font = QtCore.QVariant()
        else:
            self.font = QtGui.QFont()
            self.font.setBold(True)
        self.color = _score_to_color(src.score)
        self._cols = [
            QtCore.QVariant(u"✔" if src.read else ""),  # read
            QtCore.QVariant(u"★" if src.starred else ""),  # starred
            QtCore.QVariant(src.source.title),  # source
            QtCore.QVariant(src.title),  # title
            QtCore.QDateTime(src.updated),  # updated
            QtCore.QVariant(src.score)  # score
        ]

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<ListItem %r; %r, %r, %r>" % (self.title, self.oid,
                                              self.read, self.updated)

    def get_value(self, col):
        return self._cols[col]


class ListModel(QtCore.QAbstractTableModel):

    _HEADERS = ("R.", "S.", "Source", "Title", "Date", "Score")

    def __init__(self, parent=None):
        super(ListModel, self).__init__(parent)
        self.items = []

    def set_items(self, items):
        _LOG.debug("ListModel.set_items(len=%d)", len(items))
        self.layoutAboutToBeChanged.emit()
        self.items = [ListItem(item) for item in items]
        self.layoutChanged.emit()

    def update_item(self, item):
        for row, itm in enumerate(self.items):
            if itm.oid == item.oid:
                itm.update(item)
                self.dataChanged.emit(self.index(row, 0), self.index(row, 3))
                return True
        return False

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent):
        return 6

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._HEADERS[col])
        return QtCore.QVariant()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()].get_value(index.column())
        elif role == QtCore.Qt.FontRole:
            return self.items[index.row()].font
        elif role == QtCore.Qt.TextColorRole:
            return self.items[index.row()].color
        return QtCore.QVariant()

    def node_from_index(self, index):
        return self.items[index.row()]


def _score_to_color(score):
    if score > 9:
        return QtGui.QColor(0, 0, 200)
    elif score > 25:
        return QtGui.QColor(0, 200, 0)
    elif score > 75:
        return QtGui.QColor(200, 0, 0)
    elif score < -10:
        return QtGui.QColor(50, 50, 50)
    return QtCore.QVariant()
