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

from mna.common import objects


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


class SimplePresenter(object):
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
                   article)
        result = ["<!doctype html><html><head>",
                  '<meta charset="UTF-8">',
                  '<title></title>',
                  '</head><body>']
        result.extend(_sp_build_title(article))
        result.append('<header>')
        result.extend(_sp_build_author(article))
        result.extend(_sp_build_published(article))
        result.append('</header>')
        if article.summary and article.content:
            result.append("<p><i>" + article.summary + r"</i></p>")
        if article.summary or article.content:
            result.append("<article><p>" + (article.content or article.summary)
                          + r"</p></article>")
        result.append('</body></html>')
        return "".join(result)


class AbstractSource(object):
    """Basic source"""

    # Human readable name
    name = "dummy"
    presenter = SimplePresenter
    # subclass of QFrame
    conf_panel_class = None

    def __init__(self, cfg):
        super(AbstractSource, self).__init__()
        # configuration
        self.oid = cfg.oid
        self.cfg = cfg
        self.group_id = cfg.group_id

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        return []

    def format_item_for_view(self, item):
        return str(item)

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_params(cls):
        return {}

    def emit_updated(self, new_articles_cnt):
        if new_articles_cnt > 0:
            objects.MESSENGER.emit_source_updated(self.oid, self.group_id)
            objects.MESSENGER.emit_announce(u"%s updated - %d new articles" %
                                            (self.cfg.title, new_articles_cnt))
        else:
            objects.MESSENGER.emit_announce(u"%s updated" % self.cfg.title)


class AbstractFilter(object):
    """Basic Filter object"""

    # Human readable name
    name = "dummy"

    def __init__(self, cfg):
        super(AbstractFilter, self).__init__()
        # configuration
        self.cfg = cfg

    def filter(self, article):
        """ Process article by filter """
        return article

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__


class GetArticleException(Exception):
    """ General refresh source error. """
    pass
