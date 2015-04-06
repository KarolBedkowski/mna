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

from . import errors

_LOG = logging.getLogger(__name__)


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
        raise errors.LoadPageError("%d: %s" % (conn.status, conn.reason))
    except urllib2.URLError, err:
        raise errors.LoadPageError(err)
