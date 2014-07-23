#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Standard plugins """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"

import pkgutil
import logging

from mna.common import objects

_LOG = logging.getLogger(__name__)
MODULES = {}
SOURCES = {}


def load_plugins():
    """ Load plugins (standard and user) """
    if MODULES:
        return
    _LOG.info('Loading modules...')
    _LOG.debug('Searching for standard modules from %s... ', __path__[0])
    for modname, _ispkg in pkgutil.ImpImporter(__path__[0]).iter_modules():
        if modname.startswith('_') or modname.endswith('_support'):
            continue
        if modname.startswith('test_') or modname.endswith('_test'):
            continue
        _LOG.debug('Loading module %s', modname)
        try:
            __import__(__package__ + '.' + modname, fromlist=[modname])
        except (ImportError, ValueError):
            _LOG.exception("Load module %s error", modname)

    SOURCES.update(_load_sources_from_subclass(objects.AbstractSource))
    _LOG.info('Modules: %s', ', '.join(sorted(MODULES.keys())))
    _LOG.info('Sources: %s', ', '.join(sorted(SOURCES.keys())))


def _load_sources_from_subclass(base_class):
    for source_class in base_class.__subclasses__():
        if hasattr(source_class, 'DISABLED'):
            continue
        module = source_class.__module__
        name = source_class.get_name()
        if name.startswith('Test') or module.endswith('_test') or \
                module.endswith('_support'):
            continue
        _LOG.debug(' loading %s from %s', name, module)
        yield (name, source_class)
        if source_class.__subclasses__():
            _load_sources_from_subclass(source_class)
