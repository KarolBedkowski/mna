#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-03"


from mna.common import objects


class WebSource(objects.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"

    def get_items(self):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return
        return
