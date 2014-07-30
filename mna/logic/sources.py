#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Sources logic """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-15"


from mna.model import dbobjects as DBO


def add_source(clazz, params):
    """ Add new source.

    :param clazz: source class to add
    :param params: dictionary of params.
    :return: DBO.Group object if success."""
    # TODO check name uniques
    group = DBO.Group()
    group.name = params.get('name')
    group.save(True)
    return group


def mark_source_read(source_id):
    """ Mark all article from source read """
    session = DBO.Session()
    cnt = session.query(DBO.Article).\
            filter(DBO.Article.source_id == source_id,
                   DBO.Article.read == 0).\
            update({'read': 1})
    session.commit()
    return cnt
