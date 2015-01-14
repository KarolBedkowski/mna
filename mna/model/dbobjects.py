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

from sqlalchemy import (Column, Integer, Unicode, DateTime, Boolean,
                        ForeignKey, Index)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm, and_
from sqlalchemy import select, func
from sqlalchemy.ext.associationproxy import association_proxy

from mna.model import jsonobj

_LOG = logging.getLogger(__name__)

# SQLAlchemy
Base = declarative_base()  # pylint: disable=C0103
Session = orm.sessionmaker()  # pylint: disable=C0103


class BaseModelMixin(object):
    """ Utilities method for database objects """

    def save(self, commit=False, session=None):
        """ Save object into database. """
        if session:
            session.merge(self)
        else:
            session = Session.object_session(self) or Session()
            session.add(self)
        if commit:
            session.commit()
        return session

    def delete(self, commit=False, session=None):
        """ Delete object from database. """
        if session:
            session.merge(self)
        else:
            session = Session.object_session(self) or Session()
            session.delete(self)
        if commit:
            session.commit()
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
    name = Column(Unicode)
    default_actions_group_id = Column(Integer, ForeignKey("actions.oid"))

    def get_articles(self, unread_only=False, sorting=None):
        """ Get list articles for all sources in current group.

        Args:
            unread_only (bool): filter articles by read flag
            sorting (str): name of column to sort; default - "updated"

        Return:
            list of Article objects
        """
        session = orm.object_session(self) or Session()
        articles = session.query(Article).\
                    join(Article.source).\
                    filter(Source.group_id == self.oid)
        if unread_only:
            articles = articles.filter(Article.read == 0)
        if sorting:
            articles = articles.order_by(sorting)
        else:
            articles = articles.order_by("updated")
        return list(articles)

    def is_valid(self):
        return bool(self.name)


class Source(BaseModelMixin, Base):
    """Source configuration"""

    __tablename__ = "sources"

    # Database (internal) source id
    oid = Column(Integer, primary_key=True)
    # Source name (package and class)
    name = Column(Unicode)
    # Displayed source title
    title = Column(Unicode)
    last_refreshed = Column(DateTime)
    # Refresh interval; default=1h
    interval = Column(Integer, default=3600)
    next_refresh = Column(DateTime, default=datetime.datetime.utcnow,
                          index=True)
    initial_score = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    processing = Column(Boolean, default=False)
    last_error = Column(Unicode)
    last_error_date = Column(DateTime)

    max_articles_to_load = Column(Integer, default=0)
    # number days back to load
    max_age_to_load = Column(Integer, default=0)

    # delete old articles
    delete_old_articles = Column(Boolean, default=True)
    num_articles_to_keep = Column(Integer, default=0)
    age_articles_to_keep = Column(Integer, default=0)

    conf = Column('conf', jsonobj.JSONEncodedDict)
    meta = Column(jsonobj.JSONEncodedDict)

    group_id = Column(Integer, ForeignKey("groups.oid"))

    group = orm.relationship(Group, backref=orm.backref("sources",
                               cascade="all, delete-orphan"))

    def force_refresh(self):
        self.next_refresh = datetime.datetime.now()

    @classmethod
    def force_refresh_all(cls):
        """ Force refresh all sources. """
        _LOG.info("Sources.force_refresh_all()")
        session = Session()
        session.query(cls).update({"next_refresh": datetime.datetime.now()})
        session.commit()

    @property
    def unread(self):
        cnt = orm.object_session(self).\
                scalar(select([func.count(Article.oid)]).
                       where(and_(Article.source_id == self.oid,
                                  Article.read == 0)))
        return cnt

    def get_articles(self, unread_only=False, sorting=None):
        """ Get list articles for source. If `unread_only` filter articles by
            `read` flag.
        """
        session = orm.object_session(self) or Session()
        articles = session.query(Article).\
                    filter(Article.source_id == self.oid)
        if unread_only:
            articles = articles.filter(Article.read == 0)
        if sorting:
            articles = articles.order_by(sorting)
        else:
            articles = articles.order_by("updated")
        return list(articles)

    @classmethod
    def get_last_article(self, source_id, session=None):
        """  Find last article for `source_id` """
        session = session or Session()
        article = session.query(Article).\
            filter(Article.source_id == source_id).\
            order_by(Article.updated.desc()).first()
        return article

    def add_to_log(self, category, message, commit=False):
        session = orm.object_session(self)
        log = SourceLog()
        log.source_id = self.oid
        log.category = category
        log.message = message
        session.add(log)
        if commit:
            session.commit()

    def get_logs(self):
        """  Find logs for `source_id` """
        session = orm.object_session(self) or Session()
        article = session.query(SourceLog).\
            filter(SourceLog.source_id == self.oid).\
            order_by(SourceLog.date.desc()).all()
        return article


class Task(BaseModelMixin, Base):
    """Tasks (i.e. filters) configuration"""

    __tablename__ = "tasks"

    oid = Column(Integer, primary_key=True)
    # Filter name
    name = Column(Unicode)
    enabled = Column(Integer, default=0)
    conf = Column('conf', jsonobj.JSONEncodedDict)


class Actions(BaseModelMixin, Base):
    """Group of task"""

    __tablename__ = "actions"

    oid = Column(Integer, primary_key=True)
    name = Column(Unicode)
    # actions
    actions = association_proxy("actions_tasks", "actions")


class Article(BaseModelMixin, Base):
    """One Article object"""

    __tablename__ = "articles"

    # database id
    oid = Column(Integer, primary_key=True)
    # publish date
    published = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    # last update date
    updated = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    # article read?
    read = Column(Integer, default=0)
    title = Column(Unicode)
    summary = Column(Unicode)
    content = Column(Unicode)
    # internal id (hash)
    internal_id = Column(Unicode, index=True)
    link = Column(Unicode)
    author = Column(Unicode)
    meta = Column(jsonobj.JSONEncodedDict)
    score = Column(Integer, default=0)
    starred = Column(Boolean, default=False)


    # tags
    source_id = Column(Integer, ForeignKey("sources.oid"))

    source = orm.relationship(Source, backref=orm.backref("articles",
                              cascade="all, delete-orphan"))

    @staticmethod
    def compute_id(link, title, author, source_id):
        if link:
            return link
        return"".join(map(hash, (title, author, source_id)))


Index('idx_articles_chs', Article.source_id, Article.internal_id, Article.oid)
Index('idx_articles_read', Article.source_id, Article.read, Article.updated,
      Article.oid)


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


class SourceLog(BaseModelMixin, Base):
    """One log entry for source"""

    __tablename__ = "sources_log"

    # database id
    oid = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    category = Column(Unicode)
    message = Column(Unicode)

    source_id = Column(Integer, ForeignKey("sources.oid"))
    source = orm.relationship(Source,
                              backref=orm.backref("source_log",
                                                  cascade="all, delete-orphan"))
