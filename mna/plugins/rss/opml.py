#!/usr/bin/python
# -*- coding: utf-8 -*-
""" OPML functions """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-02-05"


import logging

from lxml import etree

from mna.model import db
from mna.model import dbobjects as DBO


_LOG = logging.getLogger(__name__)


def import_opml(xmlstr):
    """ Get groups and items from opml string

    Return:
        iter<group title, [{item}]>
    """
    parser = etree.XMLParser(  # pylint:disable=no-member
        recover=True, encoding='UTF-8')
    tree = etree.fromstring(xmlstr, parser)  # pylint: disable=no-member
    if not tree:
        return
    for group in tree.xpath('//body/outline'):
        title = group.attrib.get('title') or group.attrib.get('text')
        if not title:
            continue
        items = [dict(item.attrib) for item in group.iterchildren()
                 if item.tag == 'outline' and item.attrib.get('type') == 'rss']
        if items:
            yield title, items


def import_opml_file(filename, session=None):
    """ Import opml rss groups and feed from file.

    Args:
        filename (str): opml file name
        session: optional SqlAlchemy session

    Return:
        number loaded sources
    """
    session = session or db.Session()
    xml_data = None
    try:
        with open(filename) as xml:
            xml_data = xml.read()
    except IOError, err:
        _LOG.error("import_opml_file: load file %r error: %r", filename, err)
        return 0
    if not xml_data:
        return 0
    cntr = 0
    for group, items in import_opml(xml_data):
        group_obj = db.get_one(DBO.Group, session, name=group)
        if group_obj is None:
            group_obj = DBO.Group(name=group)
            session.add(group_obj)
        for item in items:
            if 'xmlUrl' not in item:
                continue
            title = item.get('title') or item.get('text')
            if not title:
                continue
            # TODO: check that is source already exist
            src = DBO.Source(name="mna.plugins.rss.RssSource", title=title,
                             conf={'url': item['xmlUrl'],
                                   'web': item.get('htmlUrl')})
            group_obj.sources.append(src)  # pylint:disable=maybe-no-member
            cntr += 1
    session.commit()
    return cntr
