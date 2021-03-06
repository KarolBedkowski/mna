# -*- coding: utf-8 -*-
""" Licence and version informations.

Copyright (c) Karol Będkowski, 2014-2015

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-02-01"

import gettext

_ = gettext.gettext

SHORTNAME = "mna"
NAME = _("mna")
VERSION = "0.2.1"
VERSION_INFO = (0, 2, 1, "alpha", 1)
RELEASE = "2015-06-06"
DESCRIPTION = _("""mna""")
DEVELOPERS = u"""Karol Będkowski"""
TRANSLATORS = u"""Karol Będkowski"""
COPYRIGHT = u"Copyright (c) Karol Będkowski, 2014-2015"
LICENSE = _("""\
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
""")


INFO = _("""\
%(name)s version %(version)s (%(release)s)
%(copyright)s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

For details please see COPYING file.
""") % dict(name=NAME, version=VERSION, copyright=COPYRIGHT, release=RELEASE)
