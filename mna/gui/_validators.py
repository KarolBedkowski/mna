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


class EmptyStringValidator(QtGui.QValidator):  # pylint:disable=no-member,no-init,too-few-public-methods
    """ Validate fields for empty values """

    def validate(self, text, pos):  # pylint:disable=no-self-use
        if unicode(text).strip():
            return QtGui.QValidator.Acceptable, pos  # pylint:disable=no-member
        return QtGui.QValidator.Invalid, pos  # pylint:disable=no-member


class ValidationError(RuntimeError):
    pass


def validate_empty_string(widget, title):
    """ Check widget for empty string. """
    if hasattr(widget, "text"):
        value = widget.text()
    elif hasattr(widget, "toPlainText"):
        value = widget.toPlainText()
    else:
        raise RuntimeError("Invalid widget %r, %r" % (widget, title))
    if not unicode(value).strip():
        widget.setFocus()
        raise ValidationError(title)
    return True
