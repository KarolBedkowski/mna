#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Basic filters plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-02-06"


import logging
import pprint

from mna.model import base
from mna.model import dbobjects as DBO
from mna.model import db
from mna.common import dlg_info


_LOG = logging.getLogger(__name__)


def get_article_info(article_oid):
    article = db.get_one(DBO.Article, oid=article_oid)
    _LOG.info(pprint.pformat(article))
    info = []
    info.append(('OID', article.oid))
    info.append(('published', article.published))
    info.append(('updated', article.updated))
    info.append(('read', article.oid))
    info.append(('title', article.title))
    info.append(('internal_id', article.internal_id))
    info.append(('link', article.link))
    info.append(('author', article.author))
    info.append(('score', article.score))
    info.append(('starred', article.starred))
    info.append(('summary', article.summary))
    if __debug__ and article.meta:
        info.extend(("META: " + key, val) for key, val
                    in article.meta.iteritems())
    res = "".join(u"<dt><b>%s</b></dt><dd>%s</dd>" % keyval for keyval in info)
    return "<dl>" + res + "</dl>"


class ArticleInfoTool(base.AbstractTool):
    """ Log information about selected article """

    name = "Log article details"
    description = ""

    @classmethod
    def is_available(cls):
        return __debug__

    def run(self, parent, selected_article, selected_source, selected_group):
        if not selected_article:
            return
        article = get_article_info(selected_article)
        dlg = dlg_info.DlgInfo(parent, "Article %d" % selected_article,
                               article)
        dlg.exec_()
