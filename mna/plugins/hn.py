#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Hacker News source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-02-17"

import datetime
import logging

try:
    import simplejson as json
except ImportError:
    import json

from mna.model import base
from mna.model import dbobjects as DBO
from mna.lib import websupport

_LOG = logging.getLogger(__name__)

_TOP_STORIES_URL = r'https://hacker-news.firebaseio.com/v0/topstories.json'
_GET_STORY_URL = r'https://hacker-news.firebaseio.com/v0/item/%d.json'


class HNSource(base.AbstractSource):
    """Load article from HackerNews"""

    name = "Hacker News"
    conf_panel_class = None
    default_icon = ":plugins-hn/hn-icon.png"

    def __init__(self, cfg):
        super(HNSource, self).__init__(cfg)
        self._icon = None
        if not self.cfg.meta:
            self.cfg.meta = {}

    @classmethod
    def get_name(cls):
        return 'mna.plugins.hn'

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        _LOG.info("HNSource.get_items src=%r", self.cfg.oid)

        if not self.cfg.title:
            self.cfg.title = 'Hacker News'
        if not self.cfg.icon_id:
            self.cfg.icon_id = self.default_icon

        info, page = self._get_top_stories()
        if not page or info['_status'] == 304:  # not modified
            return []

        stories_id = json.loads(page.decode('utf-8'))
        last_sid = self.cfg.meta.get('last_sid')
        if last_sid:
            stories_id = [sid for sid in stories_id if sid > last_sid]

        if not stories_id:
            return []

        self.cfg.meta['last_sid'] = max(stories_id)
        articles = self._get_articles(stories_id)

        # filter by time
        min_date_to_load = self._get_min_date_to_load(max_age_load)
        if min_date_to_load:
            articles = (art for art in articles
                        if art['time_parsed'] >= min_date_to_load)

        articles = (self._create_article(art) for art in articles)
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        return articles

    @classmethod
    def get_info(cls, source_conf, _session=None):
        return []

    def _get_top_stories(self):
        try:
            info, page = websupport.download_page(
                _TOP_STORIES_URL, self.cfg.meta.get('etag'),
                self.cfg.meta.get('last-modified'))
        except websupport.LoadPageError, err:
            self._log_error("Error loading page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        self.cfg.meta['last-modified'] = info['_modified']
        self.cfg.meta['etag'] = info.get('etag')
        return info, page

    def _get_articles(self, stories_id):
        for sid in stories_id:
            try:
                _LOG.debug('_get_articles: sid=%r', sid)
                _info, page = websupport.download_page(_GET_STORY_URL % sid)
            except websupport.LoadPageError, err:
                self._log_error("Error loading page: " + str(err))
                continue
            if not page:
                continue
            article = json.loads(page)
            if article.get('deleted'):  # pylint: disable=maybe-no-member
                continue
            if not article.get('url'):  # pylint: disable=maybe-no-member
                _LOG.debug("_get_articles without url: %r", article)
                continue
            article['time_parsed'] = datetime.datetime.fromtimestamp(
                article['time'])
            yield article

    def _create_article(self, article):
        art = DBO.Article()
        art.internal_id = article['id']
        art.content = '<a href="%s">%s</a>' % (article['url'],
                                               article['title'])
        art.summary = None
        art.score = self.cfg.initial_score
        art.title = article['title']
        art.updated = article['time_parsed']
        art.published = art.updated
        art.link = article['url']
        art.author = article['by']
        art.meta = {}
        return art


