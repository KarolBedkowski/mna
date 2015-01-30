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

from mna.model import base
from mna.model import db
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
        self._ui = frm_sett_rss_ui.Ui_FrmSettRss()
        self._ui.setupUi(self)

    def validate(self):
        try:
            _validators.validate_empty_string(self._ui.e_url, 'URL')
        except _validators.ValidationError:
            return False
        return True

    def from_window(self, source):
        source.conf["url"] = self._ui.e_url.text()
        return True

    def to_window(self, source):
        self._ui.e_url.setText(source.conf.get("url") or "")


class RssSource(base.AbstractSource):
    """Rss/Atom source class. """

    name = "RSS/Atom Source"
    conf_panel_class = FrmSettRss

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        _LOG.info("RssSource: src=%d get_items from %r", self.cfg.oid, url)
        doc = feedparser.parse(url)
        if not doc or doc.get('status') >= 400:
            self.cfg.add_log('error', "Error loading RSS feed: " +
                             doc.get('status'))
            _LOG.error("RssSource: src=%d error getting items from %s, %r, %r",
                       self.cfg.oid, url, doc, self.cfg)
            raise base.GetArticleException("Get rss feed error: %r" %
                                           doc.get('status'))

        min_date_to_load = self._get_min_date_to_load(max_age_load)
        _LOG.debug("RssSource: src=%d min_date_to_load=%s", self.cfg.oid,
                   min_date_to_load)
        articles = filter(None,
                          (self._create_article(feed, session,
                                                min_date_to_load)
                           for feed in doc.get('entries') or []))

        _LOG.debug("RssSource: src=%d loaded %d articles",
                   self.cfg.oid, len(articles))
        if not articles:
            self.cfg.add_log('info', "Not found new articles")
            return []

        # Limit number articles to load
        if self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0):
            max_articles_to_load = self.cfg.max_articles_to_load or max_load
            if len(articles) > max_articles_to_load:
                _LOG.debug("RssSource: src=%d loaded >max_articles - "
                           "truncating", self.cfg.oid)
                articles = articles[-max_articles_to_load:]
                self.cfg.add_log('info',
                                 "Loaded only %d articles (limit)." %
                                 len(articles))
        return articles

    def _create_article(self, feed, session, min_date_to_load):
        published = _ts2datetime(feed.get('published_parsed'))
        updated = _ts2datetime(feed.get('updated_parsed'))
        updated = updated or published or datetime.datetime.now()
        if min_date_to_load and updated < min_date_to_load:
            _LOG.debug("RssSource: src=%d updated=%s < min_date_to_load=%s",
                       self.cfg.oid, updated, min_date_to_load)
            # return None

        internal_id = feed.get('id') or \
                DBO.Article.compute_id(feed.get('link'),
                                       feed.get('title'),
                                       feed.get('author'),
                                       self.__class__.get_name())
        art = db.get_one(DBO.Article, session=session,
                         source_id=self.cfg.oid,
                         internal_id=internal_id)
        if art:
            _LOG.debug("RssSource: src=%d Article already in db: %r",
                       self.cfg.oid, internal_id)
            if art.updated > updated:
                _LOG.debug("RssSource: src=%d Article is not updated, "
                           "skipping", self.cfg.oid)
                return None

        art = art or DBO.Article()
        art.internal_id = internal_id
        if 'content' in feed:
            art.content = feed.content[0].value
        else:
            art.content = feed.get('value')
        art.summary = feed.get('summary')
        art.score = self.cfg.initial_score
        art.title = feed.get('title')
        art.updated = updated
        art.published = published or datetime.datetime.now()
        art.link = feed.get('link')
        return art

    def _get_min_date_to_load(self, global_max_age):
        min_date_to_load = self.cfg.last_refreshed
        max_age_to_load = self.cfg.max_age_to_load

        if max_age_to_load == 0:  # use global settings
            max_age_to_load = global_max_age
        elif max_age_to_load == -1:  # no limit; use last refresh
            return min_date_to_load

        if max_age_to_load:  # limit exists
            limit = datetime.datetime.now() - datetime.timedelta(
                days=max_age_to_load)
            if min_date_to_load:
                min_date_to_load = max(limit, min_date_to_load)
            else:
                min_date_to_load = limit

        return min_date_to_load
