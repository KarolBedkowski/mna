#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Jamendo source plugin


Find new albums for given artist.
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-02-17"

import datetime
import logging
import urllib
import locale

try:
    import simplejson as json
except ImportError:
    import json

from PyQt4 import QtGui

from mna.model import base
from mna.model import dbobjects as DBO
from mna.lib import websupport

from . import frm_sett_jamendo_ui

_LOG = logging.getLogger(__name__)

# TODO: get own client id
_CLIENT_ID = "f919df7d"
_COUNTRY_CODE = locale.getdefaultlocale()[0][:2]


class FrmSettJamendo(QtGui.QFrame):  # pylint: disable=no-member
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)  # pylint: disable=no-member
        self._ui = frm_sett_jamendo_ui.Ui_FrmSettRss()
        self._ui.setupUi(self)

    def validate(self):
        if not self._ui.e_artist.text():
            self._ui.e_artist.setFocus()
            return False
        return True

    def from_window(self, source):
        source.conf["artist_id"] = self._ui.e_artist.text()
        return True

    def to_window(self, source):
        self._ui.e_artist.setText(source.conf.get("artist_id") or "")


class JamendoArtistAlbumsSource(base.AbstractSource):
    """Load albums for configured artist from Jamendo"""

    name = "Jamendo - Artist's Albums"
    conf_panel_class = FrmSettJamendo
    default_icon = ":plugins-jamendo/jamendo-icon.png"

    def __init__(self, cfg):
        super(JamendoArtistAlbumsSource, self).__init__(cfg)
        self._icon = None
        if not self.cfg.meta:
            self.cfg.meta = {}

    @classmethod
    def get_name(cls):
        return 'mna.plugins.jamendo.artistalbums'

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        _logtitle = "JamendoArtistAlbumsSource.get_items src=%r " % \
            self.cfg.oid
        _LOG.info(_logtitle + "start")

        if not self.cfg.icon_id:
            self.cfg.icon_id = self.default_icon

        artist_id = self.cfg.conf.get('artist_id')
        if not artist_id:
            _LOG.warn(_logtitle + "missing artist_id")
            return
        min_date = self.cfg.meta.get('last_min_date')
        max_date = datetime.datetime.now().strftime('%Y-%m-%d')

        isok, _, _, results = self._get_albums(artist_id, min_date, max_date)
        if not isok or not results:
            return []

        if not self.cfg.title:
            self.cfg.title = results[0].get('name')
        self.cfg.meta['last_min_date'] = max_date

        albums = results[0].get('albums')
        if not albums:
            _LOG.info(_logtitle + "no albums")
            return []

        albums = self._filter_new_albums(albums)
        if not albums:
            _LOG.info(_logtitle + "no new albums")
            return []

        new_last_sid = max(album['id'] for album in albums)
        albums = self._prepare_albums(albums)
        albums = self._filter_by_date(albums, max_age_load)
        articles = [self._create_article(album, self.cfg.title)
                    for album in albums]

        _LOG.debug(_logtitle + "loaded %d articles", len(articles))
        if not articles:
            self._log_info("Not found new articles")
            return []
        self._log_info("Found %d new articles" % len(articles))
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        self.cfg.meta['last_sid'] = new_last_sid
        return articles

    @classmethod
    def get_info(cls, source_conf, _session=None):
        return []

    def _get_albums(self, artist_id, min_date, max_date):
        """ Get albums for given  `artist_id` released between `min_date`
        and `max_date`.

        Returns:
            (ok, http_info, response header, response result)
        """
        url = 'https://api.jamendo.com/v3.0/artists/albums?'
        query = {
            'client_id': _CLIENT_ID,
            'format': 'json',
        }
        try:
            query['id'] = int(artist_id)
        except ValueError:
            query['name'] = artist_id
        if min_date:
            query['album_datebetween'] = min_date + "_" + max_date
        url += urllib.urlencode(query)
        _LOG.debug('JamendoArtistAlbumsSource._get_albums: %r', url)
        try:
            info, page = websupport.download_page(url)
        except websupport.LoadPageError, err:
            self._log_error("Error loading page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        if not page:
            return False, info, None, None

        page = json.loads(page.decode('utf-8'))
        if not page:
            _LOG.info("JamendoArtistAlbumsSource._get_albums empty result: %r",
                      info)
            return False, info, None, None

        headers = page.get('headers')  # pylint: disable=maybe-no-member
        results = page.get('results')  # pylint: disable=maybe-no-member
        if not headers or headers['status'] != 'success':
            _LOG.info("JamendoArtistAlbumsSource._get_albums error result: %r",
                      page['headers'])
            return False, info, headers, results
        return True, info, headers, results

    def _prepare_albums(self, albums):  # pylint:disable=no-self-use
        for album in albums:
            album = album.copy()
            album['releasedate_p'] = datetime.datetime.strptime(
                album['releasedate'], '%Y-%m-%d')
            yield album

    def _filter_new_albums(self, albums):
        last_sid = self.cfg.meta.get('last_sid')
        _LOG.debug('JamendoArtistAlbumsSource.get_items: last_sid=%r',
                   last_sid)
        if last_sid:
            albums = [album for album in albums if album['id'] > last_sid]
        return albums

    def _filter_by_date(self, albums, max_age_load):
        # filter by timme
        min_date_to_load = self._get_min_date_to_load(max_age_load)
        if min_date_to_load:
            albums = (album for album in albums
                      if album['releasedate_p'] >= min_date_to_load)
        return albums

    def _create_article(self, album, artist):
        art = DBO.Article()
        art.internal_id = album['id']
        url = 'http://www.jamendo.com/%s/list/a%s' % (
            _COUNTRY_CODE, album['id'])
        art.content = '<a href="%s"><img src="%s" /><br/>%s</a>' % \
            (url, album.get('image'), album['name'])
        art.summary = None
        art.score = self.cfg.initial_score
        art.title = album['name']
        art.updated = album['releasedate_p']
        art.published = art.updated
        art.link = url
        art.author = artist
        art.meta = {}
        return art

    def _get_min_date_to_load(self, global_max_age):
        min_date_to_load = self.cfg.last_refreshed
        max_age_to_load = self.cfg.max_age_to_load

        if max_age_to_load == 0:  # use global settings
            max_age_to_load = global_max_age
        elif max_age_to_load == -1:  # no limit; use last refresh
            return min_date_to_load

        if max_age_to_load:  # limit exists
            now = datetime.datetime.now()
            limit = now - datetime.timedelta(days=max_age_to_load)
            if min_date_to_load:
                min_date_to_load = max(limit, min_date_to_load)
            else:
                min_date_to_load = limit

        return min_date_to_load

    @classmethod
    def update_configuration(cls, source_conf, session=None):
        org_conf = source_conf.conf
        source_conf.conf = {
            'artist_id': org_conf.get('artist_id') or ''
        }
        if not source_conf.interval:
            source_conf.interval = 60 * 60 * 24  # 1d
        return source_conf
