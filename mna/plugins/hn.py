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


# pylint: disable=too-few-public-methods
class _HNPresenter(base.SimplePresenter):
    """ Presenter dedicated to HNSource articles. """
    name = "HN presenter"

    def _format_content(self, article):  # pylint: disable=no-self-use
        yield "<article>"
        if article.content:
            yield "<p>" + article.content + r"</p>"
        else:
            if article.link:
                yield '<p><a href="%s">%s</a></p>' % (article.link,
                                                      article.link)
            yield '<p><a href="https://news.ycombinator.com/item?id=%s">'\
                'Comments</a></p>' % article.internal_id
            yield '<p><small><b>Score:</b> %s&nbsp;&nbsp;&nbsp;' \
                % article.meta.get('score')
            yield '<b>Type:</b> %s</small></p>' % article.meta.get('type')
        yield "</article>"


class HNSource(base.AbstractSource):
    """Load article from HackerNews"""

    name = "Hacker News"
    conf_panel_class = None
    default_icon = ":plugins-hn/hn-icon.png"
    presenter = _HNPresenter

    def __init__(self, cfg):
        super(HNSource, self).__init__(cfg)
        self._icon = None
        if not self.cfg.title:
            self.cfg.title = 'Hacker News'
            self.mark_conf_updated()
        if not self.cfg.icon_id:
            self.cfg.icon_id = self.default_icon
            self.mark_conf_updated()

    @classmethod
    def get_name(cls):
        return 'mna.plugins.hn'

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        _LOG.info("HNSource.get_items src=%r", self.cfg.oid)

        stories_id = self._get_top_stories()
        if not stories_id:
            return None

        last_sid = self.cfg.meta.get('last_sid')
        if last_sid:
            stories_id = [sid for sid in stories_id if sid > last_sid]
            if not stories_id:
                # no new stories
                self._log_debug("no stories with id > %d", last_sid)
                return None
            self._log_debug("%d new stories with id > %d", len(stories_id),
                            last_sid)

        self.cfg.meta['last_sid'] = max(stories_id)
        stories_id = self._limit_articles(stories_id, max_load)
        stories = (self._get_story(sid) for sid in stories_id)
        # filter broken stories
        stories = (story for story in stories if story is not None)

        # filter by time
        min_date_to_load = self._get_min_date_to_load(max_age_load)
        if min_date_to_load:
            stories = (story for story in stories
                       if story['time_parsed'] >= min_date_to_load)

        articles = (self._create_article(art) for art in stories)
        articles = (art for art in articles if art is not None)
        return articles

    def _get_top_stories(self):
        """ Load top stories from api.

        Returns:
            List of stories id
        """
        try:
            info, page = websupport.download_page(
                _TOP_STORIES_URL, self.cfg.meta.get('etag'),
                self.cfg.meta.get('last-modified'))
        except websupport.LoadPageError, err:
            self._log_error("Error loading top stories page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        self.cfg.meta['last-modified'] = info['_modified']
        self.cfg.meta['etag'] = info.get('etag')
        return json.loads(page.decode('utf-8')) if page else None

    def _get_story(self, story_id):
        """ Load one article by `story_id` """
        try:
            _LOG.debug('_get_story: sid=%r', story_id)
            info, page = websupport.download_page(_GET_STORY_URL % story_id)
        except websupport.LoadPageError, err:
            _LOG.error('_get_story %d error %r; %r', story_id, err, info)
            self._log_error("Error loading story %d: %s" % (story_id, err))
            return None
        if not page:
            return None
        story = json.loads(page)
        if story.get('deleted'):  # pylint: disable=maybe-no-member
            return None
        story['time_parsed'] = datetime.datetime.fromtimestamp(story['time'])
        return story

    def _create_article(self, story):
        """ Create article from `story`. """
        art = DBO.Article()
        art.internal_id = story['id']
        art.score = self.cfg.initial_score
        art.title = story['title']
        art.updated = story['time_parsed']
        art.published = art.updated
        art.link = story.get('url')
        art.author = story['by']
        art.meta = {key: story.get(key) for key in ('score', 'type')}
        return art
