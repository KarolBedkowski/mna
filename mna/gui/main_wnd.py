# -*- coding: utf-8 -*-
""" Main application window.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2013-04-28"

import gettext
import logging

from PyQt4 import QtGui, uic, QtCore

from mna.lib.appconfig import AppConfig
from mna.model import dbobjects as DBO

_ = gettext.gettext
_LOG = logging.getLogger(__name__)


class MainWnd(QtGui.QMainWindow):
    """ Main Window class. """

    def __init__(self, _parent=None):
        super(MainWnd, self).__init__()
        self._appconfig = AppConfig()
        uic.loadUi(self._appconfig.get_data_file("gui/main.ui"), self)
        self._bind()
        self._tree_model = TreeModel()
        self.treeSubscriptions.setModel(self._tree_model)

    def _bind(self):
        self.actionRefresh.triggered.connect(self._on_action_refresh)

    def _on_action_refresh(self):
        DBO.Source.force_refresh_all()

    def _refresh_tree(self):
        pass


class TreeNode(object):
    KIND_GROUP = 0
    KIND_SOURCE = 1

    def __init__(self, parent, name=None, kind=0, oid=None):
        self.children = []
        self.parent = parent
        self.name = name
        self.kind = kind
        self.oid = oid

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return "<TreeNode %s; %r, %r>" % (self.name, self.kind, self.oid) + \
            "\n".join(" - " + str(child) for child in self.children) + "</>"

    def childAtRow(self, row):
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
            node = self._nodeFromIndex(index)
            return QtCore.QVariant(node.name)
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
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()
        return len(parent_node)

    def hasChildren(self, index):
        """Finds out if a node has children."""
        if not index.isValid():
            return True
        return len(self._nodeFromIndex(index).children) > 0

    def index(self, row, column, parent):
        """Creates an index in the model for a given node and returns it."""
        branch = self._nodeFromIndex(parent)
        return self.createIndex(row, column, branch.childAtRow(row))

    def _nodeFromIndex(self, index):
        """Retrieves the tree node with a given index."""
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root

    def parent(self, child):
        """The parent index of a given index."""
        node = self._nodeFromIndex(child)
        if node is None:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent is None or parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)
