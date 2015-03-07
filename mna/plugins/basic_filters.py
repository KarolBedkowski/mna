#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Basic filters plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-18"


import logging

from mna.model import base
from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


class MinLenFilter(base.AbstractFilter):
    """ Filter articles with too short content. """

    name = "Length filter"
    description = "Ignore articles with content shorten than configured."

    def __init__(self, cfg):
        assert isinstance(cfg, DBO.Filter), 'Invalid object type: %r' % cfg
        super(MinLenFilter, self).__init__(cfg)

    def filter(self, article):
        _LOG.debug('MinLenFilter.filter(%r)', article.oid)
        conf = self.cfg.conf
        min_length = conf.get('min_length')
        content_len = len(article.content or '') + len(article.summary or '')
        if not content_len:
            content_len = len(article.title or '')
        if not content_len:
            content_len = len(repr(article.meta))
        if min_length and content_len < min_length:
            article.score += conf.get('score', 0)
            _LOG.debug('MinLenFilter.filter(%r) = %d -> %r finished',
                       article.oid, content_len, article.score)
        return article

    @classmethod
    def get_params(cls):
        """ Get dict of filter params: {param_key -> (human_name,
            type (int/str), default_value} """
        return {'min_length': ("Minimal content length", int, 0),
                'score': ("Score to apply when content is too small",
                          int, -99)}

    @classmethod
    def get_label(cls, cfg):
        conf = cfg.conf
        return cls.name + " (length<%d -> score%+d)" % (conf.get("min_length"),
                                                        conf.get("score"))


class KeywordFilter(base.AbstractFilter):
    """ Filter articles with too short content. """

    name = "Keyword filter"
    description = "Find keywords in articles."

    def __init__(self, cfg):
        assert isinstance(cfg, DBO.Filter), 'Invalid object type: %r' % cfg
        super(KeywordFilter, self).__init__(cfg)
        conf = self.cfg.conf
        self._score = conf.get('score', 0)
        self._keywords = None
        keywords = conf.get('keywords')
        if keywords:
            keywords = keywords.split(',')
            self._keywords = [kwrd.strip().lower() for kwrd in keywords]

    def filter(self, article):
        _LOG.debug('KeywordFilter.filter(%r)', article.oid)
        for kwrd in self._keywords or []:
            if kwrd in (article.content or '').lower() or \
                    kwrd in (article.summary or '').lower():
                article.score += self._score
                _LOG.debug('KeywordFilter.filter(%r) = %s -> %r finished',
                           article.oid, kwrd, article.score)
                break
        return article

    @classmethod
    def get_params(cls):
        return {'keywords': ("Keyword separated by ','", str, ''),
                'score': ("Score to apply when content is too small",
                          int, 10)}

    @classmethod
    def get_label(cls, cfg):
        conf = cfg.conf
        return cls.name + " (%s -> score%+d)" % \
            (conf.get("keywords") or "", conf.get("score"))
