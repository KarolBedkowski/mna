# -*- coding: utf-8 -*-
""" Main module.

Copyright (c) Karol Będkowski, 2014

This file is part of mna
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014"
__version__ = "2014-06-14"

import sys
import optparse
import logging

_LOG = logging.getLogger(__name__)


from mna import version


def _parse_opt():
    """ Parse cli options. """
    optp = optparse.OptionParser(version=version.NAME + version.VERSION)
    group = optparse.OptionGroup(optp, "Debug options")
    group.add_option("--debug", "-d", action="store_true", default=False,
                     help="enable debug messages")
    group.add_option("--debug-sql", action="store_true", default=False,
                     help="enable sql debug messages")
    group.add_option("--shell", action="store_true", default=False,
                     help="start shell")
    optp.add_option_group(group)
    return optp.parse_args()[0]


def run():
    """ Run application. """
    # parse options
    options = _parse_opt()

    # logowanie
    from mna.lib.logging_setup import logging_setup
    logging_setup("mna.log", options.debug, options.debug_sql)

    # app config
    from mna.lib import appconfig
    config = appconfig.AppConfig("mna.cfg", "mna")
    config.load_defaults(config.get_data_file("defaults.cfg"))
    config.load()
    config.debug = options.debug

    # locale
    from mna.lib import locales
    locales.setup_locale(config)

    # connect to databse
    from mna.model import db
    db.connect(db.find_db_file(config), options.debug_sql)

    # load plugins
    from mna import plugins
    plugins.load_plugins()

    if options.shell:
        # starting interactive shell
        from IPython.terminal import ipapp
        app = ipapp.TerminalIPythonApp.instance()
        app.initialize(argv=[])
        app.start()
        return

    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)

    from mna.logic import worker
    main_worker = worker.MainWorker()
    main_worker.start()

    from mna.gui import wnd_main

    window = wnd_main.WndMain()
    window.show()
    app.exec_()

    main_worker.terminate()
    config.save()
