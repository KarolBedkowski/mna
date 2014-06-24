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
import datetime

try:
    import simplejson as json
except ImportError:
    import json


from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
# , Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy import orm  # , or_, and_
from sqlalchemy.ext.associationproxy import association_proxy

_LOG = logging.getLogger(__name__)

# SQLAlchemy
Base = declarative_base()  # pylint: disable=C0103
Session = orm.sessionmaker()  # pylint: disable=C0103


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    From: sqlalchemy manual

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                value = json.loads(value)
            except ValueError:
                _LOG.error("JSONEncodedDict.Invalid value to decode: %r",
                           value)
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

    @classmethod
    def count(cls, session=None, **kwargs):
        """ Count objects with given attributes.

        Args:
            session: optional sqlalchemy session
            kwargs: query filters.

        Return:
            One object.
        """
        return (session or Session()).query(cls).filter_by(**kwargs).count()

    def __repr__(self):
        info = []
        for prop in orm.object_mapper(self).iterate_properties:
            if isinstance(prop, orm.ColumnProperty) or \
                    (isinstance(prop, orm.RelationshipProperty)
                     and prop.secondary):
                info.append("%r=%r" % (prop.key, getattr(self, prop.key)))
        return "<" + self.__class__.__name__ + ' ' + ','.join(info) + ">"


class Group(BaseModelMixin, Base):
    """Group sources/articles"""

    __tablename__ = "groups"

    oid = Column(Integer, primary_key=True)
    name = Column(String)
    default_actions_group_id = Column(Integer, ForeignKey("actions.oid"))


class Source(BaseModelMixin, Base):
    """Source configuration"""

    __tablename__ = "sources"

    oid = Column(Integer, primary_key=True)
    # Source name (package and class)
    name = Column(String)
    # Displayed source title
    title = Column(String)
    last_refreshed = Column(DateTime)
    interval = Column(Integer, default=3600)
    next_refresh = Column(DateTime, default=datetime.datetime.utcnow,
                          index=True)
    initial_score = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    processing = Column(Boolean, default=False)
    last_error = Column(String)
    last_error_date = Column(DateTime)
    conf = Column('conf', JSONEncodedDict)
    meta = Column(JSONEncodedDict)

    group_id = Column(Integer, ForeignKey("groups.oid"))

    group = orm.relationship(Group, backref=orm.backref("sources",
                               cascade="all, delete-orphan"))

    def force_refresh(self):
        self.next_refresh = datetime.datetime.now()

    @classmethod
    def force_refresh_all(cls):
        """ Force refresh all sources. """
        session = Session()
        session.query(cls).update({"next_refresh": datetime.datetime.now()})
        session.commit()


class Task(BaseModelMixin, Base):
    """Tasks (i.e. filters) configuration"""

    __tablename__ = "tasks"

    oid = Column(Integer, primary_key=True)
    # Filter name
    name = Column(String)
    enabled = Column(Integer, default=0)
    conf = Column('conf', JSONEncodedDict)


class Actions(BaseModelMixin, Base):
    """Group of task"""

    __tablename__ = "actions"

    oid = Column(Integer, primary_key=True)
    name = Column(String)
    # actions
    actions = association_proxy("actions_tasks", "actions")



class Article(BaseModelMixin, Base):
    """One Article object"""

    __tablename__ = "articles"

    oid = Column(Integer, primary_key=True)
    published = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    readed = Column(Integer, default=0)
    title = Column(String)
    summary = Column(String)
    content = Column(String)
    internal_id = Column(String, index=True)
    link = Column(String)
    author = Column(String)
    meta = Column(JSONEncodedDict)
    score = Column(Integer, default=0)

    # tags
    group_id = Column(Integer, ForeignKey("groups.oid"))
    source_id = Column(Integer, ForeignKey("sources.oid"))


class ActionsTasks(BaseModelMixin, Base):
    """ Actions-Tasks connections. """

    __tablename__ = "actions_tasks"

    actions_id = Column(Integer, ForeignKey("actions.oid", onupdate="CASCADE",
                                            ondelete="CASCADE"),
                        primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.oid", onupdate="CASCADE",
                                         ondelete="CASCADE"),
                     primary_key=True)

    actions = orm.relationship(Actions, backref=orm.backref("actions_tasks",
                               cascade="all, delete-orphan"))
    task = orm.relationship(Task)
