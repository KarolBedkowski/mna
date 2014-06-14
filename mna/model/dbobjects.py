#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=W0105

""" SqlAlchemy objects definition.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""
__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-12"


import logging
import gettext
import datetime

try:
    import cjson
    _JSON_DECODER = cjson.decode
    _JSON_ENCODER = cjson.encode
except ImportError:
    import json
    _JSON_DECODER = json.loads
    _JSON_ENCODER = json.dumps


from sqlalchemy import Column, Integer, String, DateTime, Boolean
# , ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, VARCHAR
# from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import orm  # , or_, and_
# from sqlalchemy import select, func

_LOG = logging.getLogger(__name__)
_ = gettext.gettext

# SQLAlchemy
Base = declarative_base()  # pylint: disable=C0103
Session = orm.sessionmaker()  # pylint: disable=C0103


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    Fron: sqlalchemy manual

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = _JSON_ENCODER(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = _JSON_DECODER(value)
        return value


class BaseModelMixin(object):
    """ Utilities method for database objects """

    def save(self):
        """ Save object into database. """
        session = Session.object_session(self) or Session()
        session.add(self)
        return session

    def clone(self, cleanup=True):
        """ Clone current object.

        Args:
            cleanup: clean specific to instance values.
        """
        newobj = type(self)()
        for prop in orm.object_mapper(self).iterate_properties:
            if isinstance(prop, orm.ColumnProperty) or \
                    (isinstance(prop, orm.RelationshipProperty)
                     and prop.secondary):
                setattr(newobj, prop.key, getattr(self, prop.key))
        if hasattr(newobj, 'uuid') and cleanup:
            newobj.uuid = None
        if hasattr(self, 'children'):
            for child in self.children:
                newobj.children.append(child.clone())
        return newobj

    def compare(self, obj):
        """ Compare objects. """
        for prop in orm.object_mapper(self).iterate_properties:
            if isinstance(prop, orm.ColumnProperty) or \
                    (isinstance(prop, orm.RelationshipProperty)
                     and prop.secondary):
                if getattr(obj, prop.key) != getattr(self, prop.key):
                    return False
        return True

    def update_modify_time(self):
        if hasattr(self, 'modified'):
            self.modified = datetime.datetime.utcnow()  # pylint: disable=W0201

    @classmethod
    def all(cls, order_by=None, session=None):
        """ Return all objects this class.

        Args:
            order_by: optional order_by query argument
        """
        session = session or Session()
        query = session.query(cls)
        if hasattr(cls, 'deleted'):
            query = query.filter(cls.deleted.is_(None))
        if order_by:
            query = query.order_by(order_by)
        return query  # pylint: disable=E1101

    @classmethod
    def get(cls, session=None, **kwargs):
        """ Get one object with given attributes.

        Args:
            session: optional sqlalchemy session
            kwargs: query filters.

        Return:
            One object.
        """
        return (session or Session()).query(cls).filter_by(**kwargs).first()

    def __repr__(self):
        info = []
        for prop in orm.object_mapper(self).iterate_properties:
            if isinstance(prop, orm.ColumnProperty) or \
                    (isinstance(prop, orm.RelationshipProperty)
                     and prop.secondary):
                info.append("%r=%r" % (prop.key, getattr(self, prop.key)))
        return "<" + self.__class__.__name__ + ' ' + ','.join(info) + ">"


class Article(BaseModelMixin, Base):
    """One Article object"""

    __tablename__ = "articles"

    oid = Column(Integer, primary_key=True)
    score = Column(Integer, default=0)
    updated = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    readed = Column(Integer, default=0)
    title = Column(String)
    content = Column(String)
    # tags
    # group_id
    # source_id
    # actions_group_id


class ActionsGroup(BaseModelMixin, Base):
    """Group of actions definition"""

    __tablename__ = "actions_groups"

    oid = Column(Integer, primary_key=True)
    name = Column(String)
    # actions


class Group(BaseModelMixin, Base):
    """Group sources/articles"""

    __tablename__ = "groups"

    oid = Column(Integer, primary_key=True)
    name = Column(String)
    # source_id
    # default_actions_group_id


class SourceConf(BaseModelMixin, Base):
    """Source configuration"""

    __tablename__ = "sources_conf"

    oid = Column(Integer, primary_key=True)
    # Source name
    name = Column(String)
    last_refreshed = Column(DateTime)
    initial_score = Column(Integer, default=0)
    # group_id
    enabled = Column(Boolean, default=0)
    conf = Column('conf', JSONEncodedDict)


class FilterConf(BaseModelMixin, Base):
    """Filter configuration"""

    __tablename__ = "filters_conf"

    oid = Column(Integer, primary_key=True)
    # Source name
    name = Column(String)
    enabled = Column(Integer, default=0)
    conf = Column('conf', JSONEncodedDict)
