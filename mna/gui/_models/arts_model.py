# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
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

from mna.logic import articles

_LOG = logging.getLogger(__name__)


class ListItem(object):
    __slots__ = ('oid', '_cols', 'font', 'color')

    def __init__(self, src):
        self.oid = src.oid
        self._cols = []
        self.font = QtCore.QVariant()  # pylint: disable=no-member
        self.color = QtCore.QVariant()  # pylint: disable=no-member
        self.update(src)

    # pylint: disable=no-member
    def update(self, src):
        if src.read:
            self.font = QtCore.QVariant()  # pylint: disable=no-member
        else:
            self.font = QtGui.QFont()  # pylint: disable=no-member
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


DS_SOURCE = 1
DS_GROUP = 2
DS_STARRED = 3
DS_ALL = 4
DS_SEARCH = 4


class ListModel(QtCore.QAbstractTableModel):  # pylint: disable=no-member

    _HEADERS = ("R.", "S.", "Source", "Title", "Date", "Score")

    def __init__(self, parent=None):
        # pylint: disable=no-member
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.clear()

    def clear(self):
        self.ds_kind = None
        self.ds_oid = None
        self.ds_unread_only = False

    def set_data_source(self, kind=None, oid=None, unread_only=None):
        _LOG.info("set_data_source: %r, %r, %r", kind, oid, unread_only)
        if kind is not None:
            self.ds_kind = kind
        if oid is not None:
            self.ds_oid = oid
        if unread_only is not None:
            self.ds_unread_only = unread_only

    def refresh(self, session=None):
        """ Refresh all items according to data sources. """
        _LOG.info("refresh: %r, %r, %r", self.ds_kind, self.ds_oid,
                  self.ds_unread_only)
        self.layoutAboutToBeChanged.emit()  # pylint: disable=no-member
        arts = []
        if self.ds_kind == DS_SOURCE:
            arts = articles.get_articles_by_source(
                self.ds_oid, self.ds_unread_only, session=session)
        elif self.ds_kind == DS_GROUP:
            arts = articles.get_articles_by_group(
                self.ds_oid, self.ds_unread_only, session=session)
        elif self.ds_kind == DS_ALL:
            arts = articles.get_all_articles(self.ds_unread_only,
                                             session=session)
        elif self.ds_kind == DS_STARRED:
            arts = articles.get_starred_articles(False, session=session)
        elif self.ds_kind == DS_SEARCH:
            arts = articles.search_text(self.ds_oid, session=session)
        else:
            raise RuntimeError("invalid ds_kind=%r" % self.ds_kind)
        self.items = [ListItem(item) for item in arts]
        self.layoutChanged.emit()  # pylint: disable=no-member

    def update_item(self, item):
        for row, itm in enumerate(self.items):
            if itm.oid == item.oid:
                itm.update(item)
                # pylint: disable=no-member
                self.dataChanged.emit(self.index(row, 0), self.index(row, 3))
                return True
        return False

    def rowCount(self, _parent=None):
        return len(self.items)

    def columnCount(self, _parent):  # pylint: disable=no-self-use
        return 6

    # pylint: disable=no-member
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._HEADERS[col])
        return QtCore.QVariant()

    # pylint: disable=no-member
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


# pylint: disable=no-member
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
