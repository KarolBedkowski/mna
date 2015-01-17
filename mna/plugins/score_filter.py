#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RSS/Atom source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"


from mna.model import base


class ScoreFilter(base.AbstractFilter):
    """ Filter articles with too low score. """

    name = "Basic score filter"

    def __init__(self):
        super(ScoreFilter, self).__init__()
        self.minimal_score = 0

    def filter(self, article):
        if article.score >= self.minimal_score:
            return article
        return None
