#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web support functions """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import logging
import itertools
import urllib2
import os.path

from lxml import etree

from .errors import LoadPageError

_LOG = logging.getLogger(__name__)

try:
    from ._requests import download_page
    _LOG.info('websupport using python-requests')
except ImportError:
    from ._raw import download_page
    _LOG.info('websupport using urllib2')


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


def get_page_part(info, page, selector=None):
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
        # pylint: disable=no-member
        return [unicode(
            etree.tostring(tree, encoding='utf-8', method='html').strip(),
            encoding='utf-8', errors="replace")]
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
