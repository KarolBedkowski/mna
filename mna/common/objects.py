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


class AbstractSource(object):
    """Basic source"""

    # Human readable name
    name = "dummy"

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


class AbstractPresenter(object):
    """Base class for all presenters - converters `Article` content to html
    displayed in gui.
    """
    # Human readable name
    name = "Abstract presenter"

    def __init__(self, cfg):
        """ Constructor

        Args:
            cfg (obj): configuration loaded from database
        """
        super(AbstractPresenter, self).__init__()
        self.cfg = cfg

    def to_gui(self, article):
        """ Convert article content to html.

        Args:
            article (Article): object to convert

        Returns:
            formatted article

        """
        result = []
        if article.title:
            result.append("<h1>" + article.title + r"</h1>")
        if article.summary:
            result.append("<p><i>" + article.summary + r"</i></p>")
        if article.content:
            result.append("<article><p>" + article.content + r"</p></article>")
        return "".join(result)
