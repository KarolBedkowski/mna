#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-03"


from mna.common import objects


class WebSource(objects.BaseSource):
    """Load article from website"""

    name = "Web Page Source"

    def __init__(self):
        super(WebSource, self).__init__()
        self.url = None
        self.xpath = None

    def get_items(self):
        return []
