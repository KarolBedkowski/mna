# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
""" Qt models - subscriptions and groups models

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-31"


import logging
import weakref

from PyQt4 import QtCore, QtGui

from mna.model import db
from mna.logic import groups, sources, articles

_LOG = logging.getLogger(__name__)


ID_ROLE = QtCore.Qt.UserRole + 1  # pylint:disable=no-member


class _TreeNode(object):
    def __init__(self, parent, caption=None, oid=None, unread=None):
        self.clear()
        self.parent = weakref.proxy(parent) if parent else None
        self.caption = caption
        self.oid = oid
        self.unread = unread

    def __str__(self):
        if self.unread:
            return self.caption + "  (" + str(self.unread) + ")"
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

    def find_child_by_oid(self, oid):
        for child in self.children:
            if child.oid == oid:
                return child
        _LOG.error("_TreeNode.find_child_by_oid(oid=%r) not found in %r",
                   oid, self)
        return None

    def row(self):
        """The position of this node in the parent's list of children."""
        return self.parent.children.index(self) if self.parent else 0

    def get_font(self):
        if self.unread:
            font = QtGui.QFont()  # pylint:disable=no-member
            font.setBold(True)
            return font
        return QtCore.QVariant()  # pylint:disable=no-member

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


class GroupTreeNode(_TreeNode):
    """ Group node """
    def __init__(self, parent, group_oid, group_name):
        super(GroupTreeNode, self).__init__(parent, group_name, group_oid)

    def update(self, session=None):
        """ Update group caption and unread counter from database. """
        self.caption, self.unread = groups.get_group_info(session, self.oid)

    def update_unread(self):
        """ Update unread items count from children. """
        self.unread = sum(cld.unread for cld in self.children)


class SourceTreeNode(_TreeNode):
    """ Group node """
    def __init__(self, parent, title, oid, unread):
        super(SourceTreeNode, self).__init__(
            parent, (title or u"Source %d" % oid), oid, unread)

    def update(self, session=None):
        """ Update source caption and unread counter from database. """
        caption, self.unread = sources.get_source_info(session, self.oid)
        self.caption = caption or u"Source %d" % self.oid


SPECIAL_STARRED = -1
SPECIAL_ALL = -2
SPECIAL_SEARCH = -3


class SpecialTreeNode(_TreeNode):
    """Special node (all nodes, stared, etc). """
    def __init__(self, parent, title, sid):
        super(SpecialTreeNode, self).__init__(parent, title, sid)

    def update(self, session):
        if self.oid == SPECIAL_STARRED:
            self.unread = articles.get_starred_count(session)

    def get_font(self):
        return QtCore.QVariant()  # pylint:disable=no-member


# pylint:disable=no-member
_DEFAULT_FLAGS = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class TreeModel(QtCore.QAbstractItemModel):  # pylint:disable=no-member
    """ Groups & sources tree model.
    """
    def __init__(self, parent=None):
        # pylint:disable=no-member
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.root = _TreeNode(None, 'root', -1, -1)
        self._starred = None
        self._specials_pos = {}
        self._specials = {}
        self.refresh()

    def _create_specials(self, root):
        """ Create special groups """

        def append_special(caption, oid):
            node = SpecialTreeNode(root, caption, oid)
            root.children.append(node)
            self._specials[oid] = node
            self._specials_pos[oid] = len(root.children) - 1

        append_special("All", SPECIAL_ALL)
        append_special("Starred", SPECIAL_STARRED)
        append_special("Search", SPECIAL_SEARCH)

    def refresh(self, session=None):
        """ Refresh whole tree model from database. """
        self.layoutAboutToBeChanged.emit()  # pylint:disable=no-member
        self.root.clear()
        session = session or db.Session()
        self._create_specials(self.root)
        for (group_oid, group_name), group \
                in groups.get_group_sources_tree(session):
            obj = GroupTreeNode(self.root, group_oid, group_name)
            obj.children = [SourceTreeNode(obj, s_title, s_oid, s_unread)
                            for s_oid, s_title, s_unread in group]
            obj.update_unread()
            self.root.children.append(obj)
        self.update_specials(session)
        self.layoutChanged.emit()  # pylint:disable=no-member

    def update_group(self, group_id, session=None):
        self.layoutAboutToBeChanged.emit()  # pylint:disable=no-member
        child = self.root.find_child_by_oid(group_id)
        if child is not None:
            child.update(session)
        self.layoutChanged.emit()  # pylint:disable=no-member

    def update_source(self, source_id, group_id, session=None):
        self.layoutAboutToBeChanged.emit()  # pylint:disable=no-member
        group = self.root.find_child_by_oid(group_id)
        assert group is not None
        source = group.find_child_by_oid(source_id)
        assert source is not None, 'cant find source %r in tree model' % \
            source_id
        source.update(session)
        group.update_unread()
        self.update_specials(session)
        self.layoutChanged.emit()  # pylint:disable=no-member

    def update_specials(self, session):
        for spec in self._specials.itervalues():
            spec.update(session)

    def get_index_of_special(self, special_id):
        row = self._specials_pos[special_id]
        return self.index(row, 0, None)

    # pylint:disable=no-member
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

    # pylint:disable=no-member,no-self-use
    def setData(self, _index, _value, _role=None):
        """Sets the role data for the item at index to value."""
        return False

    def headerData(self, _section, orientation, role):
        """Returns the data for the given role and section in the header
           with the specified orientation."""
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('Title')
        return QtCore.QVariant()

    def flags(self, _index):
        """Returns the item flags for the given index. """
        return _DEFAULT_FLAGS

    def columnCount(self, _parent):
        """The number of columns for the children of the given index."""
        return 1

    def rowCount(self, parent):
        """The number of rows of the given index."""
        return len(self.node_from_index(parent).children)

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
        return self.createIndex(row, column, branch.children[row])

    def node_from_index(self, index):
        """Retrieves the tree node with a given index."""
        assert isinstance(index, QtCore.QModelIndex), \
            "Invalid index argument: %r" % index
        if index and index.isValid():
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

    def find_oid_index(self, oid):
        root = self.createIndex(0, 0, 0)
        return self.match(root, ID_ROLE, oid, -1)
