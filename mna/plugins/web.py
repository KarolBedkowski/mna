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
from HTMLParser import HTMLParser

from lxml import etree

from mna.common import objects
from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


class LoadPageError(RuntimeError):
    pass


def download_page(url):
    """ Download Page from `url` """
    try:
        conn = urllib2.urlopen(url)
        info = dict(conn.headers)
        info['_url'] = url
        modified = conn.headers.getdate('last-modified') or \
                conn.headers.getdate('last-modified')
        info['_last_modified'] = \
                datetime.datetime.fromtimestamp(time.mktime(modified)) \
                if modified else None
        _LOG.debug("%r", dict(info))
        content = conn.read()
        return info, content
    except urllib2.URLError, err:
        raise LoadPageError(err)


def get_page_part(info, page, selector):
    """ Find all elements of `page` by `selector` xpath expression. """
    if info.get('content_type') == 'text/html':
        parser = etree.HTMLParser(encoding='UTF-8')
    else:
        parser = etree.XMLParser(recover=True, encoding='UTF-8')
    tree = etree.fromstring(page, parser)
    return (etree.tostring(elem).strip() for elem in tree.xpath(selector))


def create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest().lower()


class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_html_tags(html):
    stripper = TagStripper()
    stripper.feed(html)
    return stripper.get_data()


class WebSource(objects.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"

    def get_items(self, session=None):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        _LOG.info("WebSourc.get_items from %r", url)

        try:
            info, page = download_page(url)
        except LoadPageError, err:
            raise objects.GetArticleException("Get web page error: %s" % err)

        last_refreshed = self.cfg.last_refreshed
        # if max_age_to_load defined - set limit last_refreshed
        if self.cfg.max_age_to_load:
            offset = datetime.datetime.now() - \
                    datetime.timedelta(days=self.cfg.max_age_to_load)
            last_refreshed = max(last_refreshed, offset)

        page_modification = info.get('_last-modified')
        if page_modification and page_modification < last_refreshed:
            _LOG.info("No page %s modification since %s", self.cfg.title,
                      last_refreshed)
            return []

        parts = []
        selector = self.cfg.conf.get('xpath')
        if selector:
            parts = list(get_page_part(info, page, selector))
        else:
            parts = [page]

        if not parts:
            return []

        now = datetime.datetime.now()
        initial_score = self.cfg.initial_score
        articles = []
        for part in parts:
            if not part:
                continue

            checksum = create_checksum(part)
            art = DBO.Article.get(session=session, internal_id=checksum)
            if art:
                _LOG.debug("Article already in db - skipping: %r", checksum)
                continue

            art = art or DBO.Article()
            art.internal_id = checksum
            art.content = part
            art.summary = None
            art.score = initial_score
            art.title = strip_html_tags(part)
            if len(art.title) > 100:
                art.title = art.title[:97] + "..."
            art.updated = now
            art.published = page_modification
            art.link = url
            articles.append(art)

        _LOG.debug("WebSource: loaded %d articles", len(articles))
        # Limit number articles to load
        if self.cfg.max_articles_to_load and \
                len(articles) > self.cfg.max_articles_to_load:
            _LOG.debug("WebSource: loaded >max_articles - truncating")
            articles = articles[-self.cfg.max_articles_to_load:]
        return articles

    @classmethod
    def get_params(cls):
        return {'name': 'Name',
                'url': "Website URL",
                'xpath': 'Web part selector'}
