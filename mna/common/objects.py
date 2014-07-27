#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=W0105

""" Abstracts objects..

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""
__author__ = u"Karol Będkowski"
__copyright__ = u"Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-12"


class SimplePresenter(object):
    """Base class for all presenters - converters `Article` content to html
    displayed in gui.
    """
    # Human readable name
    name = "Abstract presenter"

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
        result = ["<!doctype html><html><head>",
                  '<meta charset="UTF-8">',
                  '<title></title>',
                  '</head><body>']
        if article.title:
            result.append("<h1>")
            if article.link:
                result.append('<a href="' + article.link + '">"')
            result.append(article.title)
            if article.link:
                result.append('</a>')
            result.append("</h1>")
        result.append('<header>')
        if article.author:
            result.append("<p><small>" + article.author + "</small></p>")
        if article.published:
            result.append("<p><small><strong>Published:</strong> ")
            result.append(unicode(article.published))
            if article.updated and article.updated != article.published:
                result.append("<strong>Updated:</strong> ")
                result.append(unicode(article.updated))
            result.append("</small></p>")
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

    def __init__(self, cfg):
        super(AbstractSource, self).__init__()
        # configuration
        self.cfg = cfg

    def get_items(self):
        return []

    def format_item_for_view(self, item):
        return str(item)

    @classmethod
    def get_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_params(cls):
        return {}


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
