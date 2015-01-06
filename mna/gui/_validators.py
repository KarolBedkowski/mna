# -*- coding: utf-8 -*-
""" Qt validators

Copyright (c) Karol Będkowski, 2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-06"

from PyQt4 import QtGui


class EmptyStringValidator(QtGui.QValidator):
    """ Validate fields for empty values """

    def validate(self, text, pos):
        if unicode(text).strip():
            return QtGui.QValidator.Acceptable, pos
        return QtGui.QValidator.Invalid, pos


class ValidationError(RuntimeError):
    pass


def validate_empty_string(widget, title):
    """ Check widget for empty string. """
    assert hasattr(widget, "text"), "Invalid widget %r, %r" % (widget, title)
    if not unicode(widget.text()).strip():
        widget.setFocus()
        raise ValidationError(title)
    return True
