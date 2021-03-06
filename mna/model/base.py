#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Base/common objects definition.

Copyright (c) Karol Będkowski, 2014

This file is part of  mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-17"

import logging
import itertools
import datetime

from mna.lib import appconfig

_LOG = logging.getLogger(__name__)


def _sp_build_title(article):
    if article.title:
        yield "<h1>"
        if article.link:
            yield '<a href="' + article.link + '">'
        yield article.title
        if article.link:
            yield '</a>'
        yield "</h1>"


def _sp_build_author(article):
    if article.author:
        yield "<p><small>" + article.author + "</small></p>"


def _sp_build_published(article):
    if article.published:
        yield "<p><small><strong>Published:</strong> "
        yield unicode(article.published)
        if article.updated and article.updated != article.published:
            yield "&nbsp;&nbsp;&nbsp;<strong>Updated:</strong> "
            yield unicode(article.updated)
        yield "</small></p>"


class SimplePresenter(object):  # pylint:disable=too-few-public-methods
    """Base class for all presenters - converters `Article` content to html
    displayed in gui.
    """
    # Human readable name
    name = "Simple presenter"

    def __init__(self, source=None):
        """ Constructor

        Args:
            source (AbstractSource): configuration loaded from database
        """
        super(SimplePresenter, self).__init__()
        self.source = source

    def to_gui(self, article):
        """ Convert article content to html.

        Args:
            article (Article): object to convert

        Returns:
            formatted article

        TODO:
            use some template system
        """
        _LOG.debug("SimplePresenter: %s - render %r", self.name,
                   article.oid)
        css = appconfig.AppConfig().get('view.base_css')
        result = ["<!doctype html><html><head>",
                  '<meta charset="UTF-8">',
                  '<title></title>'
                  '<style type="text/css">', css, '</style>',
                  '</head><body>']
        result.append('<header>')
        result.extend(_sp_build_title(article))
        result.extend(_sp_build_author(article))
        result.extend(_sp_build_published(article))
        result.append('</header>')
        result.extend(self._format_content(article))
        result.append('</body></html>')
        return "".join(result)

    def _format_content(self, article):  # pylint: disable=no-self-use
        if article.summary or article.content:
            yield ("<article><p>" + (article.content or article.summary)
                   + r"</p></article>")


class AbstractSource(object):
    """Basic source"""

    # Human readable name
    name = "dummy"
    presenter = SimplePresenter
    # subclass of QFrame
    conf_panel_class = None
    # default icon for sources this type
    default_icon = "unknown"

    def __init__(self, cfg):
        super(AbstractSource, self).__init__()
        # configuration
        self.oid = cfg.oid
        self.cfg = cfg
        self.group_id = cfg.group_id
        self._resources = {}
        self._now = datetime.datetime.now()  # starting, base date
        if not self.cfg.meta:
            self.cfg.meta = {}

    # pylint:disable=unused-argument,no-self-use
    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        """ Get articles from sources

        Args:
            session: SqlAlchemy session
            max_load: maximum number of articles to load
            max_age_load: maximum age of articles to load

        Errors:
            GetArticleException: all errors

        Returns:
            iter<Article> | [Article]
        """
        return []

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    # pylint:disable=unused-argument
    def get_info(cls, source_conf, session=None):
        """ Get additional information specific to given source. """
        return None

    def get_resources(self):  # pylint:disable=no-self-use
        """ Get additional resources to store in cache (i.e. icons).

        Returns:
            iter((name, content))
        """
        return self._resources.iteritems()

    def mark_conf_updated(self):
        self.cfg.conf_updated = datetime.datetime.now()

    def _log_info(self, message):
        """ Add info `message` to source log. """
        self.cfg.add_log('info', message)

    def _log_error(self, message):
        """ Add error `message` to source log. """
        self.cfg.add_log('error', message)

    def _log_debug(self, message, *args):
        """ Add debug `message` to source log. """
        if __debug__:
            self.cfg.add_log('debug', message % args)

    @classmethod
    def update_configuration(cls, source_conf, session=None):
        """ Update `source_conf` with default source parameters.
        Remove wrong parameters. """
        return source_conf

    def _limit_articles(self, articles, max_load):
        """ Limit number of articles to configured value or global `max_load`.

        Args:
            articles: iter or list of articles
            max_load: optional maximum number of articles
        """
        # skip empty articles
        articles = itertools.ifilter(None, articles)
        if self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0):
            max_articles_to_load = self.cfg.max_articles_to_load or max_load
            articles = list(articles)
            return articles[-max_articles_to_load:]
        return articles

    def _get_min_date_to_load(self, global_max_age, now=None):
        min_date_to_load = self.cfg.last_refreshed
        max_age_to_load = self.cfg.max_age_to_load
        now = now or self._now

        if max_age_to_load == 0:  # use global settings
            max_age_to_load = global_max_age
        elif max_age_to_load == -1:  # no limit; use last refresh
            self._log_debug("min date to load: %r", min_date_to_load)
            return min_date_to_load

        if max_age_to_load:  # limit exists
            limit = now - datetime.timedelta(days=max_age_to_load)
            if min_date_to_load:
                min_date_to_load = max(limit, min_date_to_load)
            else:
                min_date_to_load = limit

        self._log_debug("min date to load: %r", min_date_to_load)
        return min_date_to_load


class AbstractFilter(object):
    """Basic Filter object"""

    # Human readable name
    name = "dummy"
    description = ""

    def __init__(self, cfg):
        super(AbstractFilter, self).__init__()
        # configuration
        self.cfg = cfg

    def filter(self, article):  # pylint:disable=no-self-use
        """ Process article by filter """
        return article

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_params(cls):
        """ Get dict of filter params: {param_key -> (human_name,
            type (int/str), default_value} """
        return {}

    @classmethod
    def get_label(cls, cfg):  # pylint:disable=unused-argument
        """ Get human name of filter type; can show params from `cfg` """
        return cls.name


class GetArticleException(Exception):
    """ General refresh source error. """
    pass


class AbstractTool(object):
    """Basic Tool object"""

    # Human readable name
    name = "dummy"
    description = ""
    group = ""

    def __init__(self):
        super(AbstractTool, self).__init__()

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def is_available(cls):
        return False

    def run(self, parent, selected_article, selected_source, selected_group):
        pass
