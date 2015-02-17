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
    """Load article from website"""

    name = "Hacker News"
    conf_panel_class = None
    default_icon = ":icons/hn-icon.svg"

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

        info, page = self._get_top_stories()
        if info['_status'] == 304:  # not modified
            _LOG.info("HNSource.get_items %r - not modified", self.cfg.oid)
            return []

        stories_id = json.loads(page.decode('utf-8'))

        last_sid = self.cfg.meta.get('last_sid')
        _LOG.debug('HNSource.get_items: last_art=%r', last_sid)
        new_last_sid = max(stories_id)
        if last_sid:
            stories_id = [sid for sid in stories_id if sid > last_sid]

        if not stories_id:
            _LOG.info("HNSource.get_items %r - no new stories", self.cfg.oid)
            return []

        articles = self._get_articles(stories_id)

        # filter by timme
        min_date_to_load = self._get_min_date_to_load(max_age_load)
        if min_date_to_load:
            articles = (art for art in articles
                        if art['time_parsed'] >= min_date_to_load)

        articles = [self._create_article(art) for art in articles]

        _LOG.debug("HNSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_log('info', "Not found new articles")
            return []
        self.cfg.add_log('info', "Found %d new articles" % len(articles))
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        self.cfg.meta['last_sid'] = new_last_sid
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
            self.cfg.add_log('error',
                             "Error loading page: " + str(err))
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
                self.cfg.add_log('error', "Error loading page: " + str(err))
            else:
                if page:
                    article = json.loads(page)
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

    def _limit_articles(self, articles, max_load):
        if self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0):
            max_articles_to_load = self.cfg.max_articles_to_load or max_load
            if len(articles) > max_articles_to_load:
                _LOG.debug("HNSource: loaded >max_articles - truncating")
                articles = articles[-max_articles_to_load:]
                self.cfg.add_log('info',
                                 "Loaded only %d articles (limit)." %
                                 len(articles))
        return articles

    def _get_min_date_to_load(self, global_max_age):
        min_date_to_load = self.cfg.last_refreshed
        max_age_to_load = self.cfg.max_age_to_load

        if max_age_to_load == 0:  # use global settings
            max_age_to_load = global_max_age
        elif max_age_to_load == -1:  # no limit; use last refresh
            return min_date_to_load

        if max_age_to_load:  # limit exists
            now = datetime.datetime.now()
            limit = now - datetime.timedelta(days=max_age_to_load)
            if min_date_to_load:
                min_date_to_load = max(limit, min_date_to_load)
            else:
                min_date_to_load = limit

        return min_date_to_load
