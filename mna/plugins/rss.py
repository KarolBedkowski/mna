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
from PyQt4 import QtGui

from mna.common import objects
from mna.model import dbobjects as DBO
from mna.plugins import frm_sett_rss_ui
from mna.gui import _validators

_LOG = logging.getLogger(__name__)


def _ts2datetime(tstruct):
    """ Convert time stucture to datetime.datetime """
    if tstruct:
        return datetime.datetime.fromtimestamp(time.mktime(tstruct))
    return None


class FrmSettRss(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.ui = frm_sett_rss_ui.Ui_FrmSettRss()
        self.ui.setupUi(self)

    def validate(self):
        try:
            _validators.validate_empty_string(self.ui.e_url, 'URL')
        except _validators.ValidationError:
            return False
        return True

    def from_window(self, source):
        source.conf["url"] = unicode(self.ui.e_url.text())
        return True

    def to_window(self, source):
        self.ui.e_url.setText(source.conf.get("url") or "")


class RssSource(objects.AbstractSource):
    """Rss/Atom source class. """

    name = "RSS/Atom Source"
    conf_panel_class = FrmSettRss

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
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

        last_refreshed = self.cfg.last_refreshed
        if last_refreshed and (self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0)):
            max_age_to_load = self.cfg.max_age_to_load or max_age_load
            # if max_age_to_load defined - set limit last_refreshed
            last_refreshed = \
                    max(last_refreshed,
                        datetime.datetime.now() -
                        datetime.timedelta(days=max_age_to_load))

        articles = filter(None,
                          (self._create_article(feed, session, last_refreshed)
                           for feed in doc.get('entries') or []))

        _LOG.debug("RssSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_to_log('info', "Not found new articles")
            return []

        # Limit number articles to load
        if self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0):
            max_articles_to_load = self.cfg.max_articles_to_load or max_load
            if len(articles) > max_articles_to_load:
                _LOG.debug("WebSource: loaded >max_articles - truncating")
                articles = articles[-max_articles_to_load:]
                self.cfg.add_to_log('info',
                                    "Loaded only %d articles (limit)." %
                                    len(articles))
        return articles

    def _create_article(self, feed, session, last_refreshed):
        published = _ts2datetime(feed.get('published_parsed'))
        updated = _ts2datetime(feed.get('updated_parsed'))
        updated = updated or published or datetime.datetime.now()
        if last_refreshed and updated < last_refreshed:
            return None

        internal_id = feed.get('id') or \
                DBO.Article.compute_id(feed.get('link'),
                                       feed.get('title'),
                                       feed.get('author'),
                                       self.__class__.get_name())
        art = DBO.Article.get(session=session, source_id=self.cfg.oid,
                              internal_id=internal_id)
        if art:
            _LOG.debug("Article already in db: %r", internal_id)
            if art.updated > updated:
                _LOG.debug("Article is not updated, skipping")
                return None

        art = art or DBO.Article()
        art.internal_id = internal_id
        art.content = feed.get('value')
        art.summary = feed.get('summary')
        art.score = self.cfg.initial_score
        art.title = feed.get('title')
        art.updated = updated
        art.published = published or datetime.datetime.now()
        art.link = feed.get('link')
        return art

    @classmethod
    def get_params(cls):
        return {'name': 'Name',
                'url': "RSS URL"}
