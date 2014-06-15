# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
""" Application configuration.

Copyright (c) Karol Będkowski, 2007-2014

This file is part of kPyLibs,mna

This is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-14"

import sys
import os
import imp
import logging

try:
    import cjson
    _JSON_DECODER = cjson.decode
    _JSON_ENCODER = cjson.encode
except ImportError:
    import json
    _JSON_DECODER = json.loads
    _JSON_ENCODER = json.dumps

from mna import configuration
from mna.lib.singleton import Singleton

_LOG = logging.getLogger(__name__)


class AppConfig(Singleton):
    """ Object holding, loading and saving configuration.

    Args:
        filename: path for configuration file
        app_name: name of applicaiton
        main_dir: directory containing main file
    """
    # pylint: disable=R0902

    def _init(self, filename, app_name, main_dir=None):
        # pylint: disable=W0221
        _LOG.debug('AppConfig.__init__(%r, %r, %r)', filename, app_name,
                   main_dir)
        self._user_home = os.path.expanduser('~')
        self.app_name = app_name
        self.main_is_frozen = is_frozen()
        self.main_dir = main_dir or self._get_main_dir()
        self.config_path = self._get_config_path(app_name)
        self.data_dir = self._get_data_dir()
        self._filename = os.path.join(self.config_path, filename)
        self.clear()
        _LOG.debug('AppConfig.__init__: frozen=%(main_is_frozen)r, '
                   'main_dir=%(main_dir)s, config=%(_filename)s, '
                   'data=%(data_dir)s', self.__dict__)

    ###########################################################################

    def __setitem__(self, key, value):
        self._config.__setitem__(key, value)

    def __getitem__(self, key):
        return self._config.__getitem__(key)

    def __dellitem__(self, key):
        self._config.__delitem__(key)

    def get(self, key, default=None):
        return self._config.get(key, default)

    ###########################################################################

    def _get_debug(self):
        return self._runtime_params.get('DEBUG', False)

    def _set_debug(self, value):
        self._runtime_params['DEBUG'] = value

    debug = property(_get_debug, _set_debug)

    ###########################################################################

    @property
    def locales_dir(self):
        """ Find directory with localisation files. """
        if self.main_is_frozen:
            if not sys.platform.startswith('win32'):
                return os.path.join(sys.prefix,
                                    configuration.LINUX_LOCALES_DIR)
        return os.path.join(self.main_dir, configuration.LOCALES_DIR)

    @property
    def user_share_dir(self):
        """ Get path to app local/share directory.

        Default: ~/.local/share/<app_name>/
        """
        return os.path.join(self._user_home, '.local', 'share', self.app_name)

    def clear(self):
        """ Clear all data in object. """
        self._runtime_params = {}
        self._config = {}

    def load(self):
        """ Load application configuration file. """
        if self.load_configuration_file(self._filename):
            self._after_load(self._config)

    def load_defaults(self, filename):
        """ Load default configuration file. """
        if filename:
            self.load_configuration_file(filename)

    def load_configuration_file(self, filename):
        """ Load configuration file. """
        if not os.path.exists(filename):
            _LOG.warn("AppConfig.load_configuration_file: file %r not found",
                      filename)
            return False
        _LOG.info('AppConfig.load_configuration_file: %r', filename)
        try:
            with open(filename, 'r') as cfile:
                self._config.update(_JSON_DECODER(cfile.read()))
        except StandardError:
            _LOG.exception('AppConfig.load_configuration_file error')
            return False
        _LOG.debug('AppConfig.load_configuration_file finished')
        return True

    def save(self):
        """ Save configuration. """
        _LOG.debug('AppConfig.save')
        self._before_save(self._config)
        try:
            with open(self._filename, 'w') as cfile:
                cfile.write(_JSON_ENCODER(self._config))
        except StandardError:
            _LOG.exception('AppConfig.save error')
        _LOG.debug('AppConfig.save finished')

    def get_data_file(self, filename):
        """ Get full path to file in data directory.

        Args:
            filename: file name to find

        Returns:
            Full path or None if file not exists.
        """
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            return path
        _LOG.warn('AppConfig.get_data_file(%s) not found', filename)
        return None

    def _get_main_dir(self):
        """ Find main application directory. """
        if self.main_is_frozen:
            if sys.platform == 'win32':
                return os.path.abspath(os.path.dirname(sys.executable))
        return os.path.abspath(os.path.dirname(sys.argv[0]))

    def _get_config_path(self, app_name):
        """ Get path to config file. Create directories if not exists.

        Config is stored in ~/.config/<app_name>
        """
        config_path = os.path.join(self._user_home, '.config', app_name)
        if not os.path.exists(config_path):
            try:
                os.makedirs(config_path)
            except IOError:
                _LOG.exception('Error creating config directory: %s',
                               self.config_path)
                config_path = self.main_dir
        return config_path

    def _get_data_dir(self):
        """ Find path to directory with data files. """
        if self.main_is_frozen:
            if not sys.platform == 'win32':
                return os.path.join(sys.prefix, configuration.LINUX_DATA_DIR)
        return os.path.join(self.main_dir, configuration.DATA_DIR)

    def _after_load(self, config):
        """ Action to take after loaded configuration. """
        pass

    def _before_save(self, config):
        """ Action to take before save configuration. """
        pass


def is_frozen():
    """ Check if application is frozen. """
    if __file__.startswith(sys.prefix):
        return True
    return (hasattr(sys, "frozen")      # new py2exe
            or hasattr(sys, "importers")        # old py2exe
            or imp.is_frozen("__main__"))       # tools/freeze


if __name__ == '__main__':
    acfg = AppConfig('test.cfg')
    acfg.save()

    acfg.clear()

    acfg = AppConfig('test.cfg')
    acfg.load()
