# -*- coding: utf-8 -*-
""" Qt models

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"


import logging

from PyQt4 import QtCore

from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


class TreeNode(object):
    KIND_GROUP = 0
    KIND_SOURCE = 1

    def __init__(self, parent, caption=None, kind=0, oid=None, unread=0):
        self.clear()
        self.parent = parent
        self.caption = caption
        self.kind = kind
        self.oid = oid
        self.unread = unread

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return "<TreeNode %s; %r, %r>" % (self.caption, self.kind, self.oid) + \
            "\n".join(" - " + repr(child) for child in self.children) + "</>"

    def clear(self):
        self.children = []

    def _update_self(self, session):
        """ Update me. """
        if self.kind == TreeNode.KIND_GROUP:
            item = DBO.Group.get(session=session, oid=self.oid)
            self.caption = item.name
        else:
            item = DBO.Source.get(session=session, oid=self.oid)
            self.caption = item.title

    def update(self, oid, session):
        """ Update node or find children and update when found.

        :param oid: id object to update
        """
        if self.oid == oid:
            self._update_self(session)
            return True
        for node in self.children:
            if node.update(oid, session):
                self._update_self(session)
                return True
        return False

    def child_at_row(self, row):
        """The row-th child of this node."""
        return self.children[row]

    def row(self):
        """The position of this node in the parent's list of children."""
        return self.parent.children.index(self) if self.parent else 0


class TreeModel(QtCore.QAbstractItemModel):
    """ Groups & sources tree model.
    """
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = TreeNode(None, 'root', -1, -1)
        self.refresh()

    def refresh(self):
        """ Refresh whole tree model from database. """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.root.clear()
        session = DBO.Session()
        for group in list(DBO.Group.all(session=session)):
            obj = TreeNode(None, group.name, TreeNode.KIND_GROUP, group.oid)
            for source in group.sources:
                src = TreeNode(obj, source.title, TreeNode.KIND_SOURCE,
                               source.oid)
                obj.children.append(src)
            self.root.children.append(obj)
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def update(self, oid):
        """ Update group by `oid` and its subtree

        Arguments:
            oid: id group to update
        """
        session = DBO.Session()
        self.root.update(oid, session)
        session.close()

    def update_source(self, group_oid, source_oid):
        pass

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred
           to by the index."""
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            node = self.node_from_index(index)
            if index.column() == 1:
                return QtCore.QVariant(str(1))
            return QtCore.QVariant(str(node))
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        """Sets the role data for the item at index to value."""
        return False

    def headerData(self, section, orientation, role):
        """Returns the data for the given role and section in the header
           with the specified orientation."""
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            if section == 1:
                return QtCore.QVariant('Unread')
            return QtCore.QVariant('Title')
        return QtCore.QVariant()

    def flags(self, index):
        """Returns the item flags for the given index. """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def columnCount(self, parent):
        """The number of columns for the children of the given index."""
        return 2

    def rowCount(self, parent):
        """The number of rows of the given index."""
        return len(self.node_from_index(parent))

    def hasChildren(self, index):
        """Finds out if a node has children."""
        if not index.isValid():
            return True
        return len(self.node_from_index(index).children) > 0

    def index(self, row, column, parent):
        """Creates an index in the model for a given node and returns it."""
        branch = self.node_from_index(parent)
        return self.createIndex(row, column, branch.child_at_row(row))

    def node_from_index(self, index):
        """Retrieves the tree node with a given index."""
        if index.isValid():
            return index.internalPointer()
        return self.root

    def parent(self, child):
        """The parent index of a given index."""
        node = self.node_from_index(child)
        if node is None:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent is None or parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)


class ListItem(object):
    def __init__(self, title=None, oid=None, readed=None, updated=None):
        self.title = title
        self.oid = oid
        self.readed = readed
        self.updated = updated

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<ListItem %r; %r, %r, %r>" % (self.title, self.oid,
                                              self.readed, self.updated)


class ListModel(QtCore.QAbstractTableModel):

    _HEADERS = ("Readed", "Title", "Date")

    def __init__(self, parent=None):
        super(ListModel, self).__init__(parent)
        self.items = []

    def set_items(self, items):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.items = [ListItem(item.title, item.oid, item.readed, item.updated)
                      for item in items]
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent):
        return 3

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._HEADERS[col])
        return QtCore.QVariant()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            row = self.items[index.row()]
            col = index.column()
            if col == 0:
                return QtCore.QVariant(row.readed)
            elif col == 1:
                return QtCore.QVariant(row.title)
            elif col == 2:
                return QtCore.QVariant(row.updated)
        return QtCore.QVariant()

    def node_from_index(self, index):
        return self.items[index.row()]
