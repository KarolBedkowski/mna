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

    def get_items(self, session=None):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []
        _LOG.info("RssSource.get_items from %r", url)
        doc = feedparser.parse(url)
        if not doc or doc.get('status') >= 400:
            self.cfg.add_to_log('error', "Error loading RSS feed: " +
                                doc.get('status'))
            _LOG.error("RssSource: error getting items from %s, %r, %r",
                       url, doc, self.cfg)
            raise objects.GetArticleException("Get rss feed error: %r" %
                                              doc.get('status'))
        initial_score = self.cfg.initial_score
        last_refreshed = self.cfg.last_refreshed
        # if max_age_to_load defined - set limit last_refreshed
        if self.cfg.max_age_to_load:
            last_refreshed = max(last_refreshed,
                    datetime.datetime.now() - datetime.timedelta(
                    days=self.cfg.max_age_to_load))
        articles = []
        for feed in doc.get('entries') or []:
            published = _ts2datetime(feed.get('published_parsed'))
            updated = _ts2datetime(feed.get('updated_parsed'))
            updated = updated or published or datetime.datetime.now()
            if last_refreshed and updated < last_refreshed:
                continue

            internal_id = feed.get('id') or \
                    DBO.Article.compute_id(feed.get('link'),
                                           feed.get('title'),
                                           feed.get('author'),
                                           self.__class__.get_name())
            art = DBO.Article.get(session=session, internal_id=internal_id)
            if art:
                _LOG.debug("Article already in db: %r", internal_id)
                if art.updated > updated:
                    _LOG.debug("Article is not updated, skipping")
                    continue

            art = art or DBO.Article()
            art.internal_id = internal_id
            art.content = feed.get('value')
            art.summary = feed.get('summary')
            art.score = initial_score
            art.title = feed.get('title')
            art.updated = updated
            art.published = published or datetime.datetime.now()
            art.link = feed.get('link')
            articles.append(art)

        _LOG.debug("RssSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_to_log('info', "Not found new articles")
            return []
        # Limit number articles to load
        if (self.cfg.max_articles_to_load and
                len(articles) > self.cfg.max_articles_to_load):
            articles = articles[-self.cfg.max_articles_to_load:]
            self.cfg.add_to_log('info',
                                "Loaded only %d articles because of limit." %
                                len(articles))
        return articles

    @classmethod
    def get_params(cls):
        return {'name': 'Name',
                'url': "RSS URL"}
