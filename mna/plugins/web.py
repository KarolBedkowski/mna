#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-03"

import urllib2
import hashlib
import time
import datetime
import logging
import itertools
import difflib

from lxml import etree
from PyQt4 import QtGui

from mna.common import objects
from mna.model import dbobjects as DBO
from mna.gui import ui_frm_sett_web
from mna.gui import _validators

_LOG = logging.getLogger(__name__)


class LoadPageError(RuntimeError):
    pass


def download_page(url):
    """ Download Page from `url` """
    try:
        conn = urllib2.urlopen(url)
        info = dict(conn.headers)
        info['_url'] = url
        info['_encoding'] = conn.headers.getencoding()
        if info['_encoding'] == '7bit':
            info['_encoding'] = None
        modified = conn.headers.getdate('last-modified') or \
                conn.headers.getdate('last-modified')
        info['_last_modified'] = \
                datetime.datetime.fromtimestamp(time.mktime(modified)) \
                if modified else None
        content = conn.read()
        return info, content
    except urllib2.URLError, err:
        raise LoadPageError(err)


def get_page_part(info, page, selector):
    """ Find all elements of `page` by `selector` xpath expression. """
    content_type = info.get('content-type')
    if content_type and content_type.startswith('text/html'):
        parser = etree.HTMLParser(encoding='UTF-8', remove_blank_text=True,
                                  remove_comments=True, remove_pis=True)
    else:
        parser = etree.XMLParser(recover=True, encoding='UTF-8')
    tree = etree.fromstring(page, parser)
    for elem in itertools.chain(tree.xpath("//comment()"),
                                tree.xpath("//script"),
                                tree.xpath("//style")):
        elem.getparent().remove(elem)
    return (etree.tostring(elem).strip() for elem in tree.xpath(selector))


def create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest().lower()


def get_title(html, encoding):
    parser = etree.HTMLParser(encoding=encoding, remove_blank_text=True,
                              remove_comments=True, remove_pis=True)
    # try to find title
    tree = etree.fromstring(html, parser)
    for tag in ('//head/title', '//h1', '//h2'):
        titles = tree.xpath(tag)
        if titles:
            title = titles[0].text.strip()
            if title:
                return title

    # title not found, use page text
    html = etree.tostring(tree, encoding='UTF-8', method="text")
    title = unicode(html.replace('\n', ' ').replace('\t', ' ').
                    replace('\r', ' ').strip(), 'UTF-8')
    if len(title) > 100:
        title = title[:97] + "..."
    return title


def articles_similarity(art1, art2):
    return difflib.SequenceMatcher(None, art1, art2).ratio()


def accept_part(session, source_id, checksum):
    """ Check is given part don't already exists in database for given  part
        `checksum` and `source_id`.
    """
    return DBO.Article.count(session=session, internal_id=checksum,
                             source_id=source_id) == 0


def accept_page(page, session, source_id, threshold):
    """ Check is page change from last time, optionally check similarity ratio
        if `threshold`  given - reject pages with similarity ratio > threshold.
    """
    # find last article
    last = DBO.Source.get_last_article(source_id, session)
    if last:
        similarity = articles_similarity(last.content, page)
        _LOG.debug("similarity: %r %r", similarity, threshold)
        if similarity > threshold:
            _LOG.debug("Article skipped - similarity %r > %r",
                       similarity, threshold)
            return False
    return True


class FrmSettWeb(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.ui = ui_frm_sett_web.Ui_FrmSettWeb()
        self.ui.setupUi(self)

    def validate(self):
        try:
            _validators.validate_empty_string(self.ui.e_url, 'URL')
            if self.ui.rb_scan_parts.isChecked():
                _validators.validate_empty_string(self.ui.e_xpath, 'Xpath')
        except _validators.ValidationError:
            return False
        return True

    def from_window(self, source):
        source.conf["url"] = unicode(self.ui.e_url.text())
        source.conf["xpath"] = unicode(self.ui.e_xpath.toPlainText())
        source.conf["similarity"] = \
            self.ui.sb_similarity_ratio.value() / 100.0
        if self.ui.rb_scan_page.isChecked():
            source.conf["mode"] = "page"
        else:
            source.conf["mode"] = "part"
        return True

    def to_window(self, source):
        self.ui.e_url.setText(source.conf.get("url") or "")
        self.ui.e_xpath.setPlainText(source.conf.get("xpath") or "")
        self.ui.sb_similarity_ratio.setValue((source.conf.get('similarity')
                                             or 0.5) * 100.0)
        scan_part = source.conf.get("mode") == "part"
        self.ui.rb_scan_page.setChecked(not scan_part)
        self.ui.rb_scan_page.toggled.emit(not scan_part)
        self.ui.rb_scan_parts.setChecked(scan_part)
        self.ui.rb_scan_parts.toggled.emit(scan_part)


class WebSource(objects.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"
    conf_panel_class = FrmSettWeb

    def get_items(self, session=None):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        _LOG.info("WebSource.get_items from %r - %r", url, self.cfg.conf)

        try:
            info, page = download_page(url)
        except LoadPageError, err:
            self.cfg.add_to_log('error',
                                "Error loading page: " + str(err))
            raise objects.GetArticleException("Get web page error: %s" % err)

        last_refreshed = self.cfg.last_refreshed
        # if max_age_to_load defined - set limit last_refreshed
        if self.cfg.max_age_to_load:
            offset = datetime.datetime.now() - \
                    datetime.timedelta(days=self.cfg.max_age_to_load)
            last_refreshed = max(last_refreshed, offset)

        page_modification = info.get('_last-modified')
        if page_modification and page_modification < last_refreshed:
            self.cfg.add_to_log('info',
                                "Page not modified according to header")
            _LOG.info("No page %s modification since %s", self.cfg.title,
                      last_refreshed)
            return []

        articles = []
        selector_xpath = self.cfg.conf.get('xpath')
        if self.cfg.conf.get("mode") == "part" and selector_xpath:
            articles = (self._process_part(part, info, session)
                        for part in get_page_part(info, page, selector_xpath))
        else:
            articles = (self._process_page(part, info, session)
                        for part in get_page_part(info, page, "//html"))

        articles = filter(None, articles)

        _LOG.debug("WebSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_to_log('info', "Not found new articles")
            return []
        self.cfg.add_to_log('info', "Found %d new articles" % len(articles))
        # Limit number articles to load
        if self.cfg.max_articles_to_load and \
                len(articles) > self.cfg.max_articles_to_load:
            _LOG.debug("WebSource: loaded >max_articles - truncating")
            articles = articles[-self.cfg.max_articles_to_load:]
            self.cfg.add_to_log('info',
                                "Loaded only %d articles because of limit." %
                                len(articles))
        return articles

    def _process_page(self, page, info, session):
        if accept_page(page, session, self.cfg.oid,
                       self.cfg.conf.get('similarity') or 1):
            return self._create_article(page, info)
        return None

    def _process_part(self, part, info, session):
        checksum = create_checksum(part)
        if accept_part(session, self.cfg.oid, checksum):
            return self._create_article(part, info, checksum)
        return None

    def _create_article(self, part, info, checksum=None):
        art = DBO.Article()
        art.internal_id = checksum or create_checksum(part)
        art.content = part
        art.summary = None
        art.score = self.cfg.initial_score
        art.title = get_title(part, info['_encoding'])
        art.updated = datetime.datetime.now()
        art.published = info.get('_last-modified')
        art.link = self.cfg.conf.get('url')
        return art

    @classmethod
    def get_params(cls):
        return {'name': 'Name',
                'url': "Website URL",
                'xpath': 'Web part selector',
                'similarity': 'Similarity threshold'}
