#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RSS/Atom source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"

import logging
import time
import datetime

import feedparser

from mna.common import objects
from mna.model import dbobjects as DBO

_LOG = logging.getLogger(__name__)


def _ts2datetime(tstruct):
    """ Convert time stucture to datetime.datetime """
    if tstruct:
        return datetime.datetime.fromtimestamp(time.mktime(tstruct))
    return None


class RssSource(objects.AbstractSource):
    """Rss/Atom source class. """

    name = "RSS/Atom Source"

    def get_items(self):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return
        _LOG.info("RssSource.get_items from %r", url)
        doc = feedparser.parse(url)
        if not doc or doc.get('status') >= 400:
            _LOG.error("RssSource: error getting items from %s, %r, %r",
                       url, doc, self.cfg)
            return
        initial_score = self.cfg.initial_score
        last_refreshed = self.cfg.last_refreshed
        cntr = 0
        for feed in doc.get('entries') or []:
            published = _ts2datetime(feed.get('published_parsed'))
            updated = _ts2datetime(feed.get('updated_parsed'))
            updated = updated or published or datetime.datetime.now()
            if last_refreshed and updated < last_refreshed:
                continue

            # TODO: dodać sprawdzanie po id
            art = DBO.Article()
            art.internal_id = feed.get('id')
            art.content = feed.get('value')
            art.summary = feed.get('summary')
            art.score = initial_score
            art.title = feed.get('title')
            art.updated = updated
            art.published = published or datetime.datetime.now()
            art.link = feed.get('link')
            yield art
            cntr += 1
        _LOG.debug("RssSource: loaded %d articles", cntr)

    @classmethod
    def get_params(cls):
        return {'name': 'Name',
                'url': "RSS URL"}
