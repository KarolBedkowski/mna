#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import hashlib
import datetime
import logging
import difflib

from mna.model import base
from mna.model import dbobjects as DBO
from mna.lib import websupport

from . import frm_sett_web

_LOG = logging.getLogger(__name__)


def _create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest().lower()


def _create_config_hash(source):
    conf = source.conf
    return _create_checksum("|".join((conf['url'], conf['mode'],
                                      conf['xpath'])))


def accept_page(article, _session, source, threshold):
    """ Check is page change from last time, optionally check similarity ratio
        if `threshold`  given - reject pages with similarity ratio > threshold.
    """
    # find last article
    last = source.get_last_article()
    if last:
        if last.meta:
            # check for parameters changed
            last_conf_hash = last.meta.get('conf')
            if not last_conf_hash or \
                    last_conf_hash != _create_config_hash(source):
                return True
        content = article.content
        similarity = difflib.SequenceMatcher(None, last.content,
                                             content).ratio()
        _LOG.debug("similarity: %r %r", similarity, threshold)
        if similarity > threshold:
            if __debug__:
                source.add_log("debug", "similarity %r > %r" %
                               (similarity, threshold))
            _LOG.debug("Article skipped - similarity %r > %r",
                       similarity, threshold)
            return False
        article.meta['similarity'] = similarity
    return True


class WebSource(base.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"
    conf_panel_class = frm_sett_web.FrmSettWeb
    default_icon = ":icons/web-icon.svg"

    def __init__(self, cfg):
        super(WebSource, self).__init__(cfg)

    @classmethod
    def get_name(cls):
        return 'mna.plugins.web.WebSource'

    @classmethod
    def update_configuration(cls, source_conf, session=None):
        org_conf = source_conf.conf
        source_conf.conf = {
            'url': org_conf.get('url') or '',
            'mode': org_conf.get('mode') or 'page',
            'xpath': org_conf.get('xpath') or '',
            'similarity': org_conf.get('similarity') or 0.5
        }
        return source_conf

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return None

        _LOG.info("WebSource.get_items src=%r from %r - %r", self.cfg.oid,
                  url, self.cfg.conf)

        info, page = self._download_page(url)
        if info['_status'] == 304:  # not modified
            _LOG.info("WebSource.get_items %r from %r - not modified",
                      self.cfg.oid, url)
            self._log_debug("page not modified")
            return None

        self._download_page_info(url, page, info)

        if not self.is_page_updated(info, max_age_load):
            _LOG.info("WebSource.get_items src=%r page not updated",
                      self.cfg.oid)
            self._log_debug("page not updated")
            return None

        parts = self._get_articles(info, page)
        articles = (DBO.Article(content=part,
                                internal_id=_create_checksum(part),
                                meta={})
                    for part in parts)
        articles = self._filter_articles(articles, session)
        articles = (self._update_article_meta(art, info) for art in articles)
        articles = self._limit_articles(articles, max_load)
        return articles

    @classmethod
    def get_info(cls, source_conf, _session=None):
        info = [('URL', source_conf.conf.get("url"))]
        mode = source_conf.conf.get("mode")
        if mode == "part":
            info.append(('Mode', 'page parts'))
            info.append(("Selector", source_conf.conf.get('xpath')))
        elif mode == "page_one_part":
            info.append(('Mode', 'one page part'))
            info.append(("Selector", source_conf.conf.get('xpath')))
            info.append(("Similarity level",
                         str(source_conf.conf.get('similarity', 1) * 100)))
        else:
            info.append(('Mode', 'load whole page'))
            info.append(("Similarity level",
                         str(source_conf.conf.get('similarity', 1) * 100)))
        if __debug__:
            if source_conf.conf:
                info.extend(("CONF: " + key, unicode(val))
                            for key, val in source_conf.conf.iteritems())
            if source_conf.meta:
                info.extend(("META: " + key, unicode(val))
                            for key, val in source_conf.meta.iteritems())
        return info

    def _download_page(self, url):
        try:
            info, page = websupport.download_page(
                url, self.cfg.meta.get('etag'),
                self.cfg.meta.get('last-modified'))
        except websupport.LoadPageError, err:
            self._log_error("Error loading page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        self.cfg.meta['last-modified'] = info['_modified']
        self.cfg.meta['etag'] = info.get('etag')
        return info, page

    def _get_articles(self, info, page):
        selector = self.cfg.conf.get('xpath')
        mode = self.cfg.conf.get("mode")
        articles = []
        if mode == "part" and selector:
            articles = websupport.get_page_part(info, page, selector)
        elif mode == "page_one_part" and selector:
            parts = list(websupport.get_page_part(info, page, selector))
            if parts:
                articles = [parts[0]]
        else:
            articles = websupport.get_page_part(info, page, None)
        return articles

    def _filter_articles(self, articles, session):
        selector = self.cfg.conf.get('xpath')
        mode = self.cfg.conf.get("mode")
        if mode == "part" and selector:
            cache = set(row[0] for row
                        in session.query(DBO.Article.internal_id).
                        filter_by(source_id=self.cfg.oid))
            articles = (art for art in articles
                        if art.internal_id not in cache)
        else:
            sim = self.cfg.conf.get('similarity') or 1
            articles = (art for art in articles
                        if accept_page(art, session, self.cfg, sim))
        return articles

    def _update_article_meta(self, article, info):
        article.score = self.cfg.initial_score
        article.title = websupport.get_title(article.content,
                                             info['_encoding'])
        article.updated = self._now
        article.published = info.get('_last-modified')
        article.link = self.cfg.conf.get('url')
        article.meta['conf'] = _create_config_hash(self.cfg)
        return article

    def is_page_updated(self, info, max_age_load):
        last_refreshed = self.cfg.last_refreshed
        if last_refreshed is None:
            return True
        # if max_age_to_load defined - set limit last_refreshed
        if self.cfg.max_age_to_load > 0 or (self.cfg.max_age_to_load == 0
                                            and max_age_load > 0):
            max_age_to_load = self.cfg.max_age_to_load or max_age_load
            offset = self._now - datetime.timedelta(days=max_age_to_load)
            last_refreshed = max(last_refreshed, offset)

        page_modification = info.get('_last-modified')
        if page_modification and page_modification < last_refreshed:
            self._log_info("Page not modified according to header")
            _LOG.info("No page %s modification since %s", self.cfg.title,
                      last_refreshed)
            return False
        return True

    def _download_page_info(self, url, page, info):
        """ Get page icon, title, etc. """
        if not self.cfg.icon_id:
            icon, name = websupport.get_icon(url, page, info['_encoding'])
            if icon:
                name = "_".join(('src', str(self.cfg.oid), name))
                self.cfg.icon_id = name
                self._resources[name] = icon
            else:
                self.cfg.icon_id = self.default_icon
            self.mark_conf_updated()
        if self.cfg.title == "":
            self.cfg.title = websupport.get_title(page, info['_encoding'])
            self.mark_conf_updated()
