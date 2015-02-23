#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RSS/Atom source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"

import os
import logging
import datetime
import calendar

import feedparser
from sqlalchemy import orm
from PyQt4 import QtGui

from mna.model import base
from mna.model import db
from mna.model import dbobjects as DBO
from mna.gui import _validators
from mna.lib import websupport
from . import opml
from . import frm_sett_rss_ui

_LOG = logging.getLogger(__name__)

feedparser.PARSE_MICROFORMATS = 0
feedparser.USER_AGENT = ("Mozilla/5.0 (X11; Linux i686; rv:36.0) "
                         "Gecko/20100101 Firefox/36.0")


def _ts2datetime(tstruct, default=None):
    """ Convert time stucture to datetime.datetime """
    if tstruct:
        return datetime.datetime.fromtimestamp(calendar.timegm(tstruct))
    return default


def _entry_hash(entry):
    """ Compute simple checksum for "content" of feed entry """
    content = entry.content[0].value if 'content' in entry \
        else entry.get('value')
    title = entry.get('title') or ''
    author = entry.get('author') or ''
    summary = entry.get('summary') or ''
    return "".join(map(str, map(hash, (content, title, author, summary))))


class FrmSettRss(QtGui.QFrame):  # pylint: disable=no-member
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)  # pylint: disable=no-member
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
    default_icon = ":icons/feed-icon.svg"

    def __init__(self, cfg):
        super(RssSource, self).__init__(cfg)

    @classmethod
    def get_name(cls):
        return 'mna.plugins.rss.RssSource'

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        _LOG.info("RssSource: src=%d get_items", self.cfg.oid)
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        now = datetime.datetime.now()
        doc = self._get_document(url)
        if not doc:
            return []
        self._update_source_cfg(doc)

        min_date_to_load = self._get_min_date_to_load(max_age_load, now)
        feed_update = _ts2datetime(doc.get('updated_parsed'), now)
        _LOG.debug("RssSource: src=%d min_date_to_load=%s feed_update=%s",
                   self.cfg.oid, min_date_to_load, feed_update)
        if feed_update < min_date_to_load:
            _LOG.info("RssSource: src=%d feed not update %r < %r",
                      self.cfg.oid, feed_update, min_date_to_load)
            return []

        # prepare dates etc
        articles = self._prepare_entries(doc.get('entries'), feed_update)
        # filter old articles
        if min_date_to_load:
            articles = list(self._filter_by_date(articles, min_date_to_load))
        _LOG.debug("RssSource: src=%d after filtering:  %d articles",
                   self.cfg.oid, len(articles))
        if not articles:
            self.cfg.add_log('info', "Not found new articles")
            return []
        # cache articles in database
        art_cache = dict(self._get_existing_articles(session))
        # create articles with lookup into cache
        articles = (self._create_article(feed, art_cache, feed_update)
                    for feed in articles)
        # left only new/updated articles
        articles = filter(None, articles)

        _LOG.debug("RssSource: src=%d loaded %d articles",
                   self.cfg.oid, len(articles))

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

    @classmethod
    def get_info(cls, source_conf, _session=None):
        info = [("C:" + key, unicode(val))
                for key, val in source_conf.conf.iteritems()]
        if source_conf.meta:
            info.extend(("META: " + key, unicode(val))
                        for key, val in source_conf.meta.iteritems())
        return info

    @classmethod
    def update_configuration(cls, source_conf, session=None):
        org_conf = source_conf.conf
        source_conf.conf = {'url': org_conf.get('url') or ''}
        return source_conf

    def _get_document(self, url, cntr=10):
        _LOG.info("RssSource: src=%d get_document %r", self.cfg.oid, url)
        if cntr <= 0:
            raise base.GetArticleException(
                "Get rss feed error: to many redirections")
        if not self.cfg.meta:
            _LOG.warn("No meta in %d", self.cfg.oid)
            self.cfg.meta = {}
        etag = self.cfg.meta.get('etag')
        modified = self.cfg.meta.get('modified')
        doc = feedparser.parse(url, etag=etag, modified=modified)
        status = doc.get('status') if doc else 400
        if status >= 400:
            self.cfg.add_log('error', "Error loading RSS feed: %s" % status)
            _LOG.error("RssSource: src=%d error getting items from %s, %r, %r",
                       self.cfg.oid, url, doc, self.cfg)
            raise base.GetArticleException("Get rss feed error: %r" % status)
        elif status == 304:
            _LOG.info("RssSource: src=%s result %d: %r - skipping",
                      self.cfg.oid, status, doc.get('debug_message'))
            return None
        elif status == 301:  # permanent redirects
            self.cfg.meta["url.org"] = url
            self.cfg.conf["url"] = doc.href
            _LOG.info("RssSource: src=%s permanent redirects to %s",
                      self.cfg.oid, doc.href)
            self.cfg.add_log('info',
                             "Permanent redirect to %s; updating configuration"
                             % doc.href)
            return self._get_document(doc.href, cntr=cntr-1)
        elif status == 302:  # temporary redirects
            _LOG.info("RssSource: src=%s temporary redirects to %s",
                      self.cfg.oid, doc.href)
            self.cfg.add_log('info', "Temporary redirect to %s" % doc.href)
            return self._get_document(doc.href, cntr=cntr-1)

        _LOG.info("RssSource: src=%d get_document done %r", self.cfg.oid, url)
        return doc

    def _update_source_cfg(self, doc):
        if not self.cfg.meta:
            _LOG.warn("No meta in %d", self.cfg.oid)
            self.cfg.meta = {}
        self.cfg.meta['etag.old'] = self.cfg.meta.get('etag')
        self.cfg.meta['modified.old'] = self.cfg.meta.get('modified')
        self.cfg.meta['etag'] = doc.get('etag')
        self.cfg.meta['modified'] = doc.get('modified')
        if self.cfg.title == "":
            if 'title' in doc.feed:
                self.cfg.title = doc.feed.title
        if not self.cfg.icon_id:
            icon, icon_name = self._get_icon(doc)
            if icon:
                icon_name = "_".join(('src', str(self.cfg.oid), icon_name))
                self.cfg.icon_id = icon_name
                self._resources[icon_name] = icon
            else:
                self.cfg.icon_id = self.default_icon

    # pylint:disable=no-self-use
    def _prepare_entries(self, entries, feed_updated):
        for entry in entries:
            updated = _ts2datetime(entry.get('updated_parsed'))
            published = _ts2datetime(entry.get('published_parsed'))
            entry['_published'] = published or feed_updated
            entry['_updated'] = updated or published or feed_updated
            yield entry

    def _filter_by_date(self, entries, min_date_to_load):
        for entry in entries:
            if entry['_updated'] > min_date_to_load:
                yield entry

    def _create_article(self, entry, art_cache, feed_updated):
        internal_id = entry.get('id') or \
                DBO.Article.compute_id(
                    entry.get('link'), entry.get('title'), entry.get('author'),
                    self.__class__.get_name())

        content = entry.content[0].value if 'content' in entry \
            else entry.get('value')
        art = art_cache.get(internal_id)
        meta = art.meta.copy() if art and art.meta else {}
        if art and art.updated >= entry['_updated']:
            return None

        content_hash = _entry_hash(entry)
        if art:
            prev_hash = art.meta.get('content_hash') if art.meta else None
            if prev_hash == content_hash:
                return None
            meta['prev_updated'] = repr(art.updated)

        meta['feed_updated'] = repr(feed_updated)
        meta['new_art'] = not art
        meta['content_hash'] = content_hash
        meta['published'] = repr(entry.get('published'))
        meta['id'] = repr(entry.get('id'))
        meta['updated'] = repr(entry.get('updated'))

        art = art or DBO.Article(meta={})
        art.internal_id = internal_id
        art.content = content
        art.summary = entry.get('summary')
        art.score = self.cfg.initial_score
        art.title = entry.get('title')
        art.updated = entry['_updated']
        art.published = entry['_published']
        art.link = entry.get('link')
        art.author = entry.get('author')
        art.read = 0
        art.meta = meta
        return art

    def _get_min_date_to_load(self, global_max_age, now):
        min_date_to_load = self.cfg.last_refreshed
        max_age_to_load = self.cfg.max_age_to_load

        if max_age_to_load == 0:  # use global settings
            max_age_to_load = global_max_age
        elif max_age_to_load == -1:  # no limit; use last refresh
            return min_date_to_load

        if max_age_to_load:  # limit exists
            limit = now - datetime.timedelta(days=max_age_to_load)
            if min_date_to_load:
                min_date_to_load = max(limit, min_date_to_load)
            else:
                min_date_to_load = limit

        return min_date_to_load

    def _get_existing_articles(self, session):
        rows = db.get_all(DBO.Article, session=session,
                          source_id=self.cfg.oid).\
                options(orm.Load(DBO.Article).  # pylint:disable=no-member
                        load_only("oid", "internal_id", "updated", "meta"))
        for row in rows:
            yield (row.internal_id, row)

    def _get_icon(self, content):
        if 'icon' in content.feed:
            try:
                info, page = websupport.download_page(content.feed.icon,
                                                      None, None)
                if page:
                    return page, os.path.basename(content.feed.icon)
            except websupport.LoadPageError, err:
                _LOG.info("RssSource: src=%d _get_icon error %r",
                          self.cfg.oid, err)
        if 'link' in content.feed:
            try:
                info, page = websupport.download_page(content.feed.link,
                                                      None, None)
                if page:
                    icon = websupport.get_icon(content.feed.link, page,
                                               info['_encoding'])
                    if icon and icon[0]:
                        return icon
            except websupport.LoadPageError, err:
                _LOG.info("RssSource: src=%d _get_icon error %r",
                          self.cfg.oid, err)
        return None, None


class OpmlImportTool(base.AbstractTool):
    """ Import opml file """

    name = "Import OPML"
    description = ""

    @classmethod
    def is_available(cls):
        return True

    def run(self, parent, _sel_article, _sel_source, _sel_group):
        fname = QtGui.QFileDialog.getOpenFileName(  # pylint:disable=no-member
            parent, "Select OPML file")
        if fname:
            opml.import_opml_file(fname)
