#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Web support functions - requests lib """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import urllib2
import time
import datetime
import logging
import email.utils as eut

import requests

from . import errors

_LOG = logging.getLogger(__name__)


def _parse_date(date):
    if date:
        return eut.parsedate(date)
    return date


_SESSION = requests.Session()
_SESSION.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686; rv:36.0) '\
        'Gecko/20100101 Firefox/36.0'


def download_page(url, etag=None, modified=None):
    """ Download Page from `url` with optional last etag and modified time.
        When no updates return code 304 and no content.

    Args:
        url (str): address object to download
        etag (str): optional previous etag
        modified (str): optional previous modification date

    Return:
        (page headers, page content)        Custom page headers:
        Custom page headers:
            _encoding - page encoding
            _status - connection status code
            _modified - last modified date
            _url - page url
    """
    headers = {}
    if modified:
        headers['If-Modified-Since'] = modified
    if etag:
        headers['If-None-Match'] = etag

    try:
        request = _SESSION.get(url, headers=headers)
        info = dict(request.headers)
        info['_status'] = request.status_code
        info['_url'] = url
        info['_encoding'] = request.encoding
        if info['_encoding'] == '7bit':
            info['_encoding'] = None
        modified = _parse_date(info.get('Last-Modified')) or \
                _parse_date(info.get('last-modified'))
        info['_modified'] = modified
        info['_last_modified'] = \
                datetime.datetime.fromtimestamp(time.mktime(modified)) \
                if modified else None
        if request.status_code == 200:
            content = request.content
            return info, content
        elif request.status_code == 304:  # not modified
            return info, None
        raise errors.LoadPageError("%d: %s" % (request.status_code,
                                               request.reason))
    except urllib2.URLError, err:
        raise errors.LoadPageError(err)
