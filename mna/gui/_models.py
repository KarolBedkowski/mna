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

from PyQt4 import QtCore, QtGui

from mna.model import db
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


ID_ROLE = QtCore.Qt.UserRole + 1


class TreeNode(object):
    def __init__(self, parent, caption=None, oid=None, unread=0):
        self.clear()
        self.parent = parent
        self.caption = caption
        self.oid = oid
        self.unread = unread

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return "<%s %s; %r>" % (self.__class__.__name__,
                                self.caption, self.oid) + \
            "\n".join(" - " + repr(child) for child in self.children) + "</>"

    def clear(self):
        self.children = []

    def get_unread_count(self):
        """ Get count of unread articles in subtree. """
        return self.unread

    def update(self, session=None, recursive=False):
        pass

    def get_child(self, oid):
        for child in self.children:
            if child.oid == oid:
                return child
        _LOG.error("TreeNode.get_child(oid=%r) not found in %r",
                   oid, self)
        return None

    def child_at_row(self, row):
        """The row-th child of this node."""
        return self.children[row]

    def row(self):
        """The position of this node in the parent's list of children."""
        return self.parent.children.index(self) if self.parent else 0


class GroupTreeNode(TreeNode):
    """ Group node """
    def __init__(self, parent, group):
        super(GroupTreeNode, self).__init__(parent, group.name, group.oid)

    def update(self, session=None, recursive=False):
        """ Update node or find children and update when found.

        :param oid: id object to update
        """
        group = db.get_one(DBO.Group, session=session, oid=self.oid)
        self.caption = group.name
        if recursive:
            for child in self.children:
                child.update(session, recursive)
        self.unread = sum(child.get_unread_count()
                          for child in self.children)


class SourceTreeNode(TreeNode):
    """ Group node """
    def __init__(self, parent, source):
        super(SourceTreeNode, self).__init__(parent, source.title, source.oid,
                                             source.unread)

    def update(self, session=None, _recursive=False):
        item = db.get_one(DBO.Source, session=session, oid=self.oid)
        self.caption = item.title
        self.unread = item.unread


class TreeModel(QtCore.QAbstractItemModel):
    """ Groups & sources tree model.
    """
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = TreeNode(None, 'root', -1, -1)
        self.refresh()

    def refresh(self):
        """ Refresh whole tree model from database. """
        self.layoutAboutToBeChanged.emit()
        self.root.clear()
        session = db.Session()
        for group in list(db.get_all(DBO.Group, session=session)):
            obj = GroupTreeNode(None, group)
            obj.children.extend(SourceTreeNode(obj, source)
                                for source in group.sources)
            obj.update(session)
            self.root.children.append(obj)
        self.layoutChanged.emit()

    def update_group(self, group_id, session=None):
        self.layoutAboutToBeChanged.emit()
        child = self.root.get_child(group_id)
        if child is not None:
            child.update(session, True)
        self.layoutChanged.emit()

    def update_source(self, source_id, group_id, session=None):
        self.layoutAboutToBeChanged.emit()
        group = self.root.get_child(group_id)
        assert group is not None
        source = group.get_child(source_id)
        assert source is not None
        source.update(session, False)
        group.update(session, False)
        self.layoutChanged.emit()

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred
           to by the index."""
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            node = self.node_from_index(index)
            if index.column() == 1:
                return QtCore.QVariant(str(node.unread))
            return QtCore.QVariant(str(node))
        elif role == QtCore.Qt.FontRole:
            node = self.node_from_index(index)
            if node.unread:
                font = QtGui.QFont()
                font.setBold(True)
                return font
        elif role == ID_ROLE:
            node = self.node_from_index(index)
            return node.oid
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
        if not child.isValid():
            return QtCore.QModelIndex()
        node = self.node_from_index(child)
        if node is None:
            return QtCore.QModelIndex()
        parent = node.parent
        if parent is None or parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def find_oid_index(self, oid):
        root = self.createIndex(0, 0, 0)
        return self.match(root, ID_ROLE, oid, -1)


class ListItem(object):
    def __init__(self, title=None, oid=None, read=None, updated=None,
                 source=None, starred=None, score=None):
        self.title = title
        self.oid = oid
        self.read = read
        self.updated = updated
        self.source = source
        self.starred = starred
        self.score = score

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<ListItem %r; %r, %r, %r>" % (self.title, self.oid,
                                              self.read, self.updated)


class ListModel(QtCore.QAbstractTableModel):

    _HEADERS = ("R.", "S.", "Source", "Title", "Date", "Score")

    def __init__(self, parent=None):
        super(ListModel, self).__init__(parent)
        self.items = []

    def set_items(self, items):
        _LOG.debug("ListModel.set_items(len=%d)", len(items))
        self.layoutAboutToBeChanged.emit()
        self.items = [ListItem(item.title, item.oid, item.read,
                               item.updated, item.source.title, item.starred,
                               item.score)
                      for item in items]
        self.layoutChanged.emit()

    def update_item(self, item):
        for row, itm in enumerate(self.items):
            if itm.oid == item.oid:
                itm.title = item.title
                itm.read = item.read
                itm.updated = item.updated
                itm.starred = item.starred
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
            row = self.items[index.row()]
            col = index.column()
            if col == 0:
                return QtCore.QVariant(u"✔" if row.read else "")
            elif col == 1:
                return QtCore.QVariant(u"★" if row.starred else "")
            elif col == 2:
                return QtCore.QVariant(row.source)
            elif col == 3:
                return QtCore.QVariant(row.title)
            elif col == 4:
                return QtCore.QDateTime(row.updated)
            elif col == 5:
                return QtCore.QVariant(row.score)
        elif role == QtCore.Qt.FontRole:
            row = self.items[index.row()]
            if not row.read:
                font = QtGui.QFont()
                font.setBold(True)
                return font
        elif role == QtCore.Qt.TextColorRole:
            row = self.items[index.row()]
            if row.score > 9:
                return QtGui.QColor(0, 0, 200)
            elif row.score > 25:
                return QtGui.QColor(0, 200, 0)
            elif row.score > 75:
                return QtGui.QColor(200, 0, 0)
            elif row.score < -10:
                return QtGui.QColor(50, 50, 50)
        return QtCore.QVariant()

    def node_from_index(self, index):
        return self.items[index.row()]
