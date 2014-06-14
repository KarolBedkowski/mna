#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RSS/Atom source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"


import feedparser

from mna.common import objects
from mna.model import dbobjects as DBO


class RssSource(objects.BaseSource):
    """Rss/Atom source class. """

    name = "RSS/Atom Source"

    def __init__(self):
        super(RssSource, self).__init__()
        self.url = None

    def get_items(self):
        if not self.url:
            return
        doc = feedparser.parse(self.url)
        if not doc or doc.get('status') != 200:
            print "error", doc
            return
        for feed in doc.get('feed') or []:
            art = DBO.Article()
            art.content = feed.get('value')
            art.source_id = self.__class__.__name__
            art.score = self.initial_score
            art.title = feed.get('title')
            art.updated = feed.get('updated_parsed')
            yield art
