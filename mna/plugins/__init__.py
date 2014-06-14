#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Standard plugins """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-02"

import pkgutil
import logging

from mna.plugins import _base as base

_LOG = logging.getLogger(__name__)
MODULES = {}
SOURCES = {}


def load_plugins():
    """ Load plugins (standard and user) """
    if MODULES:
        return
    _LOG.info('Loading modules...')
    _LOG.debug('Searching for standard modules...')
    for modname, _ispkg in pkgutil.ImpImporter(__path__[0]).iter_modules():
        if modname.startswith('_') or modname.endswith('_support'):
            continue
        if modname.startswith('test_') or modname.endswith('_test'):
            continue
        _LOG.debug('Loading module %s', modname)
        try:
            __import__('.' + modname, fromlist=[modname])
        except ImportError:
            _LOG.exception("Load module %s error", modname)

    SOURCES.update(_load_sources_from_subclass(base.BaseSource))
    _LOG.info('Modules: %s', ', '.join(sorted(MODULES.keys())))


def _load_sources_from_subclass(base_class):
    for source_class in base_class.__subclasses__():
        if hasattr(source_class, 'DISABLED'):
            continue
        name = source_class.__name__
        module = source_class.__module__
        if name.startswith('Test') or module.endswith('_test') or \
                module.endswith('_support'):
            continue
        _LOG.debug(' loading %s from %s', name, module)
        try:
            source_obj = source_class()
            if name and not name.startswith('_'):
                name = name.lower()
                if name in MODULES:
                    name = module + '.' + name
                MODULES[name] = source_obj
        except:
            _LOG.exception('Loading %s from %s error', name, module)
        else:
            _load_sources_from_subclass(base_class)
