# -*- coding: utf-8 -*-
""" Qt modela

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"


import logging

from PyQt4 import QtCore

from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


class TreeNode(object):
    KIND_GROUP = 0
    KIND_SOURCE = 1

    def __init__(self, parent, caption=None, kind=0, oid=None):
        self.clear()
        self.parent = parent
        self.caption = caption
        self.kind = kind
        self.oid = oid

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return "<TreeNode %s; %r, %r>" % (self.caption, self.kind, self.oid) + \
            "\n".join(" - " + repr(child) for child in self.children) + "</>"

    def clear(self):
        self.children = []

    def child_at_row(self, row):
        """The row-th child of this node."""
        return self.children[row]

    def row(self):
        """The position of this node in the parent's list of children."""
        return self.parent.children.index(self) if self.parent else 0


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = TreeNode(None, 'root', -1, -1)
        self.refresh()

    def refresh(self):
        self.root.clear()
        session = DBO.Session()
        for group in list(DBO.Group.all(session=session)):
            obj = TreeNode(None, group.name, TreeNode.KIND_GROUP, group.oid)
            for source in group.sources:
                src = TreeNode(obj, source.title, TreeNode.KIND_SOURCE,
                               source.oid)
                obj.children.append(src)
            self.root.children.append(obj)

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred
           to by the index."""
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            node = self._node_from_index(index)
            return QtCore.QVariant(str(node))
        else:
            return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        """Sets the role data for the item at index to value."""
        return False

    def headerData(self, section, orientation, role):
        """Returns the data for the given role and section in the header
           with the specified orientation."""
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('Tree')
        return QtCore.QVariant()

    def flags(self, index):
        """Returns the item flags for the given index. """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def columnCount(self, parent):
        """The number of columns for the children of the given index."""
        return 1

    def rowCount(self, parent):
        """The number of rows of the given index."""
        return len(self._node_from_index(parent))

    def hasChildren(self, index):
        """Finds out if a node has children."""
        if not index.isValid():
            return True
        return len(self._node_from_index(index).children) > 0

    def index(self, row, column, parent):
        """Creates an index in the model for a given node and returns it."""
        branch = self._node_from_index(parent)
        return self.createIndex(row, column, branch.child_at_row(row))

    def _node_from_index(self, index):
        """Retrieves the tree node with a given index."""
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root

    def parent(self, child):
        """The parent index of a given index."""
        node = self._node_from_index(child)
        if node is None:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent is None or parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)
