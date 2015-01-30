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
from mna.logic import groups, sources, articles

_LOG = logging.getLogger(__name__)


ID_ROLE = QtCore.Qt.UserRole + 1


class TreeNode(object):
    def __init__(self, parent, caption=None, oid=None, unread=None):
        self.clear()
        self.parent = parent
        self.caption = caption
        self.oid = oid
        self.unread = unread

    def __len__(self):
        return len(self.children)

    def __str__(self):
        if self.unread:
            return self.caption + " (" + str(self.unread) + ")"
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

    def get_font(self):
        if self.unread:
            font = QtGui.QFont()
            font.setBold(True)
            return font
        return QtCore.QVariant()

    def get_first_unread(self, start=0, wrap=True, skip=0):
        """ Find first child with unread articles.

        Args:
            start (int): start searching from given row
            wrap (bool): if start > 0 also search in previous rows
            skip (int): optional, skips first `skip` rows

        Return:
            (row number, node)
        """
        assert start < len(self.children), 'Invalid start pos: %d' % start
        for row, child in enumerate(self.children[start:], start):
            if child.unread:
                return row, child
        if wrap:
            for row, child in enumerate(self.children[skip:start], skip):
                if child.unread:
                    return row, child
        return None, None


class GroupTreeNode(TreeNode):
    """ Group node """
    def __init__(self, parent, group_oid, group_name):
        super(GroupTreeNode, self).__init__(parent, group_name, group_oid)

    def update(self, session=None, recursive=False):
        """ Update node or find children and update when found.

        :param oid: id object to update
        """
        if recursive:
            self.caption, self.unread = groups.get_group_info(
                session, self.oid)
        else:
            self.unread = sum(cld.unread for cld in self.children)


class SourceTreeNode(TreeNode):
    """ Group node """
    def __init__(self, parent, title, oid, unread):
        super(SourceTreeNode, self).__init__(parent, title, oid, unread)

    def update(self, session=None, _recursive=False):
        self.caption, self.unread = sources.get_source_info(session, self.oid)


SPECIAL_STARRED = -1
SPECIAL_ALL = -2
SPECIAL_SEARCH = -3


class SpecialTreeNode(TreeNode):
    """Special node (all nodes, stared, etc). """
    def __init__(self, parent, title, sid):
        super(SpecialTreeNode, self).__init__(parent, title, sid)

    def update(self, session, _recursive=False):
        if self.oid == SPECIAL_STARRED:
            self.unread = articles.get_starred_count(session)

    def get_font(self):
        return QtCore.QVariant()


class TreeModel(QtCore.QAbstractItemModel):
    """ Groups & sources tree model.
    """
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = TreeNode(None, 'root', -1, -1)
        self._starred = None
        self.refresh()
        # special group position
        self.specials = {
            SPECIAL_ALL: 0,
            SPECIAL_STARRED: 1,
            SPECIAL_SEARCH: 2,
        }

    def refresh(self):
        """ Refresh whole tree model from database. """
        self.layoutAboutToBeChanged.emit()
        self.root.clear()
        session = db.Session()
        self.root.children.append(SpecialTreeNode(
            self.root, "All", SPECIAL_ALL))
        self._starred = SpecialTreeNode(self.root, "Starred", SPECIAL_STARRED)
        self._starred.update(session)
        self.root.children.append(self._starred)
        self.root.children.append(SpecialTreeNode(
            self.root, "Search", SPECIAL_SEARCH))
        for (group_oid, group_name), group \
                in groups.get_group_sources_tree(session):
            obj = GroupTreeNode(self.root, group_oid, group_name)
            obj.children = [SourceTreeNode(obj, s_title, s_oid, s_unread)
                            for s_oid, s_title, s_unread in group]
            obj.unread = sum(cld.unread for cld in obj.children)
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
        assert source is not None, 'cant find source %r in tree model' % \
            source_id
        source.update(session, False)
        group.update(session, False)
        self._starred.update(session)
        self.layoutChanged.emit()

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred
           to by the index."""
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(str(self.node_from_index(index)))
        elif role == QtCore.Qt.FontRole:
            return self.node_from_index(index).get_font()
        elif role == ID_ROLE:
            return self.node_from_index(index).oid
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        """Sets the role data for the item at index to value."""
        return False

    def headerData(self, section, orientation, role):
        """Returns the data for the given role and section in the header
           with the specified orientation."""
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('Title')
        return QtCore.QVariant()

    def flags(self, index):
        """Returns the item flags for the given index. """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def columnCount(self, parent):
        """The number of columns for the children of the given index."""
        return 1

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
        assert parent is None or isinstance(parent, QtCore.QModelIndex), \
            "Invalid parent argument: %r" % parent
        branch = self.root if not parent else self.node_from_index(parent)
        return self.createIndex(row, column, branch.child_at_row(row))

    def node_from_index(self, index):
        """Retrieves the tree node with a given index."""
        assert isinstance(index, QtCore.QModelIndex), \
            "Invalid index argument: %r" % index
        if index and index.isValid():
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
