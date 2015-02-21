#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=W0105

""" Global messenger object.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""
__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2014-06-12"

from PyQt4 import QtCore


ST_UPDATE_STARTED = 0
ST_UPDATE_FINISHED = 1
ST_UPDATE_PING = 2


# pylint:disable=no-member
class _Messenger(QtCore.QObject):

    source_updated = QtCore.pyqtSignal(int, int, name="updateSource")
    group_updated = QtCore.pyqtSignal(int, name="updateGroup")
    announce = QtCore.pyqtSignal(unicode, name="announce")
    updating_status = QtCore.pyqtSignal(int, int,
                                        name="updatingStatus")

    def emit_source_updated(self, source_id, group_id):
        """ Send source updated message.

        Args:
            source_id (int): updated source id
            group_id (int): updated source group_id
        """
        self.source_updated.emit(source_id, group_id)

    def emit_group_updated(self, group_id):
        """ Send group of sources updated message.

        Args:
            group_id (int): updated group id
        """
        self.group_updated.emit(group_id)

    def emit_announce(self, message):
        """ Announce some message (in status bar i.e.).

        Args:
            message (unicode): message to display
        """
        self.announce.emit(message)

    def emit_updating_status(self, status, data=0):
        """ Updating status changed.

        Args:
            status: new status
            data: additional data
        """
        self.updating_status.emit(status, data)


MESSENGER = _Messenger()
