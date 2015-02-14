#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web support functions """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import urllib2
import time
import datetime
import logging
import itertools
import os.path

from lxml import etree


_LOG = logging.getLogger(__name__)


class LoadPageError(RuntimeError):
    pass


# pylint:disable=no-init
class _DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(
            req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result


def download_page(url, etag=None, modified=None):
    """ Download Page from `url` with optional last etag and modified time.
        When no updates return code 304 and no content.

    Args:
        url (str): address object to download
        etag (str): optional previous etag
        modified (str): optional previous modification date

    Return:
        (page headers, page content)
        Custom page headers:
            _encoding - page encoding
            _status - connection status code
            _modified - last modified date
            _url - page url
    """
    request = urllib2.Request(url)
    opener = urllib2.build_opener(_DefaultErrorHandler())
    if modified:
        request.add_header('If-Modified-Since', modified)
    if etag:
        request.add_header('If-None-Match', etag)
    request.add_header(
        'User-Agent',
        'Mozilla/5.0 (X11; Linux i686; rv:36.0) Gecko/20100101 Firefox/36.0')
    try:
        conn = opener.open(request, timeout=10)
        info = dict(conn.headers)
        info['_status'] = conn.code
        info['_url'] = url
        info['_encoding'] = conn.headers.getencoding()
        if info['_encoding'] == '7bit':
            info['_encoding'] = None
        modified = conn.headers.getdate('Last-Modified') or \
                conn.headers.getdate('last-modified')
        info['_modified'] = modified
        info['_last_modified'] = \
                datetime.datetime.fromtimestamp(time.mktime(modified)) \
                if modified else None
        if conn.code == 200:
            content = conn.read()
            return info, content
        elif conn.code == 304:  # not modified
            return info, None
        raise LoadPageError("%d: %s" % (conn.status, conn.reason))
    except urllib2.URLError, err:
        raise LoadPageError(err)


def _parse_html_content(content, encoding=None):
    # pylint: disable=no-member
    if isinstance(content, (str, unicode)):
        parser = etree.HTMLParser(encoding=encoding)
        # try to find title
        # pylint: disable=no-member
        tree = etree.fromstring(content, parser)
    elif isinstance(content,
                    etree._Element):  # pylint: disable=protected-access
        tree = content
    else:
        raise RuntimeError("get_title invalid arg: %r", content)
    return tree


def get_page_part(info, page, selector):
    """ Find all elements of `page` by `selector` xpath expression.
    If empty selector - return parsed whole page.

    Args:
        info (dict): page heades
        page (str): downloaded page content
        selector (str): optional xpath selector
    """
    content_type = info.get('content-type')
    if content_type and content_type.startswith('text/html'):
        # pylint: disable=no-member
        parser = etree.HTMLParser(encoding='UTF-8', remove_blank_text=True,
                                  remove_comments=True, remove_pis=True)
    else:
        parser = etree.XMLParser(  # pylint:disable=no-member
            recover=True, encoding='UTF-8')
    tree = etree.fromstring(page, parser)  # pylint: disable=no-member
    for elem in itertools.chain(tree.xpath("//comment()"),
                                tree.xpath("//script"),
                                tree.xpath("//style")):
        elem.getparent().remove(elem)
    if not selector:
        return [tree]
    # pylint: disable=no-member
    return (unicode(
        etree.tostring(elem, encoding='utf-8', method='html').strip(),
        encoding='utf-8', errors="replace")
            for elem in tree.xpath(selector))


def get_title(page_content, encoding=None):
    """ Find title in html page or part.

    Args:
        page_content (str|etree.Element): page to process
        encoding (str): optional page encoding

    Return:
        title if founded
    """
    tree = _parse_html_content(page_content, encoding)
    for tag in ('//head/title', '//h1', '//h2'):
        titles = tree.xpath(tag)
        if titles:
            title = titles[0].text
            if title:
                title = title.strip()
                if title:
                    return title

    # title not found, use page text
    # pylint: disable=no-member
    html = etree.tostring(tree, encoding='UTF-8', method="text")
    title = unicode(html.replace('\n', ' ').replace('\t', ' ').
                    replace('\r', ' ').strip(), 'UTF-8')
    if len(title) > 100:
        title = title[:97] + "..."
    return title


_ICONS_XPATH = ['/html/head/link[@rel="icon"]',
                '/html/head/link[@rel="shortcut icon"]',
                '/html/head/link[@rel="apple-touch-icon-precomposed"]']


def get_icon(base_url, page_content, encoding):
    """ Find icon for page and download it.

    Args:
        base_url (str): web page original url
        page_content (str|etree.Element): page content
        encoding (str): page encoding
    Return:
        (icon content, icon name)
    """
    _LOG.info('get_icon for %r', base_url)
    # pylint: disable=no-member
    tree = _parse_html_content(page_content, encoding)
    for xpath in _ICONS_XPATH:
        icon = tree.xpath(xpath)
        if icon:
            _LOG.info('get_icon %r %r %r %r', base_url, xpath, icon,
                      icon[0].attrib)
            icon_href = icon[0].attrib.get('href')
            if not icon_href:
                continue
            url = urllib2.urlparse.urljoin(base_url, icon_href)
            _LOG.debug("get_icon: found icon url=%r", url)
            try:
                _info, icon = download_page(url, None, None)
                if icon:
                    _LOG.debug("get_icon: downloaded icon url=%r", url)
                    return icon, os.path.basename(url)
            except LoadPageError, err:
                _LOG.debug('get_icon: %r error %s', url, err)
    # try to load /favicon.ico
    url = urllib2.urlparse.urljoin(base_url, '/favicon.ico')
    try:
        _info, icon = download_page(url, None, None)
        if icon:
            _LOG.debug("get_icon: downloaded icon url=%r", url)
            return icon, os.path.basename(url)
    except LoadPageError, err:
        _LOG.debug('get_icon: %r error %s', url, err)
    _LOG.info('get_icon: %r not found', url)
    return None, None
