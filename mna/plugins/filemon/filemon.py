#!/usr/bin/python
# -*- coding: utf-8 -*-

""" File source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2015"
__version__ = "2015-01-18"

import os.path
import hashlib
import datetime
import logging
import difflib
import re
import locale
import codecs

from PyQt4 import QtGui

from mna.model import base
from mna.model import db
from mna.model import dbobjects as DBO
from mna.gui import _validators

from . import frm_sett_filemon_ui

_LOG = logging.getLogger(__name__)


def get_file_part(content, selector):
    """ Find all elements of `page` by `selector` - regular expression. """
    cselector = re.compile(selector, re.M | re.U | re.L | re.I)
    return cselector.findall(content)


def create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest().lower()


def articles_similarity(art1, art2):
    return difflib.SequenceMatcher(None, art1, art2).ratio()


def accept_part(session, source_id, checksum):
    """ Check is given part don't already exists in database for given  part
        `checksum` and `source_id`.
    """
    return db.count(DBO.Article, session=session, internal_id=checksum,
                    source_id=source_id) == 0


def accept_page(content, source, threshold):
    """ Check is check similarity ratio if `threshold`  given -
    reject files with similarity ratio > threshold.
    """
    # find last article
    last = source.get_last_article()
    if last:
        similarity = articles_similarity(last.content, content)
        _LOG.debug("similarity: %r %r", similarity, threshold)
        if similarity > threshold:
            _LOG.debug("Article skipped - similarity %r > %r",
                       similarity, threshold)
            return False
    return True


class FrmSettFilemon(QtGui.QFrame):  # pylint:disable=no-member
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)  # pylint:disable=no-member
        self._ui = frm_sett_filemon_ui.Ui_FrmSettFilemon()
        self._ui.setupUi(self)
        self._ui.b_select_file.clicked.connect(self._on_filename_choice)

    def validate(self):
        try:
            _validators.validate_empty_string(self._ui.e_filename, 'filename')
            if self._ui.rb_scan_parts.isChecked():
                _validators.validate_empty_string(self._ui.e_regex,
                                                  'expression')
        except _validators.ValidationError:
            return False
        if self._ui.rb_scan_parts.isChecked():
            cmre = None
            try:
                cmre = re.compile(self._ui.e_regex.toPlainText().strip(),
                                  re.M | re.U | re.L | re.I)
            finally:
                pass
            if not cmre:
                _LOG.debug("invalid regex")
                self._ui.e_regex.setFocus()
                return False
        return True

    def from_window(self, source):
        source.conf["filename"] = self._ui.e_filename.text()
        source.conf["regex"] = self._ui.e_regex.toPlainText()
        source.conf["similarity"] = \
            self._ui.sb_similarity_ratio.value() / 100.0
        if self._ui.rb_scan_file.isChecked():
            source.conf["mode"] = "page"
        else:
            source.conf["mode"] = "part"
        return True

    def to_window(self, source):
        self._ui.e_filename.setText(source.conf.get("filename") or "")
        self._ui.e_regex.setPlainText(source.conf.get("regex") or "")
        self._ui.sb_similarity_ratio.setValue((source.conf.get('similarity')
                                               or 0.5) * 100.0)
        scan_part = source.conf.get("mode") == "part"
        self._ui.rb_scan_file.setChecked(not scan_part)
        self._ui.rb_scan_file.toggled.emit(not scan_part)
        self._ui.rb_scan_parts.setChecked(scan_part)
        self._ui.rb_scan_parts.toggled.emit(scan_part)

    def _on_filename_choice(self):
        curr_filename = self._ui.e_filename.text()
        if curr_filename:
            curr_filename = os.path.expanduser(curr_filename)
        # pylint:disable=no-member
        filename = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr("Select file"),  # pylint:disable=no-member
            curr_filename,
            self.tr("All Files (*);;Text Files (*.txt)"))
        if filename:
            self._ui.e_filename.setText(filename)


class FileSource(base.AbstractSource):
    """Load article from plain file"""

    name = "Plain File Source"
    conf_panel_class = FrmSettFilemon

    @classmethod
    def get_name(cls):
        return 'mna.plugins.filemon.FileSource'

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        filename = self._filename
        if not filename:
            return []

        _LOG.info("FileSource.get_items from %r - %r", filename, self.cfg.conf)

        if not os.path.isfile(filename):
            raise base.GetArticleException("Load file error: file not exists")

        if not self.is_file_updated(filename, max_age_load):
            return []

        content = self._get_file_content(filename)

        articles = []
        selector = self.cfg.conf.get('regex')
        if self.cfg.conf.get("mode") == "part" and selector:
            articles = (self._process_part(part, session)
                        for part in get_file_part(content, selector))
        else:
            articles = [self._process_page(content)]

        articles = filter(None, articles)

        _LOG.debug("FileSource: loaded %d articles", len(articles))
        if not articles:
            self._log_info("Not found new articles")
            return []
        self.cfg.add_log('info',
                         "Found %d new articles" % len(articles))
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        return articles

    @classmethod
    def update_configuration(cls, source_conf, session=None):
        org_conf = source_conf.conf
        source_conf.conf = {
            'filename': org_conf.get('filename') or '',
            'regex': org_conf.get('regex'),
            'mode': org_conf.get('mode')
        }
        return source_conf

    @property
    def _filename(self):
        filename = self.cfg.conf.get("filename") if self.cfg.conf else None
        if filename:
            filename = os.path.expanduser(filename)
        return filename

    def _get_file_content(self, filename):
        local_encoding = locale.getpreferredencoding()
        try:
            with codecs.open(filename, 'r', encoding=local_encoding,
                             errors="replace") as srcfile:
                return srcfile.read()
        except IOError, err:
            self._log_error("Error loading file: " + str(err))
            raise base.GetArticleException("Load file error: %s" % err)
        return None

    def _process_page(self, content):
        if accept_page(content, self.cfg,
                       self.cfg.conf.get('similarity') or 1):
            return self._create_article(content)
        return None

    def _process_part(self, part, session):
        checksum = create_checksum(part)
        if accept_part(session, self.cfg.oid, checksum):
            return self._create_article(part, checksum)
        return None

    def _create_article(self, part, checksum=None):
        filename = self._filename
        file_modification = datetime.datetime.fromtimestamp(
            os.path.getmtime(filename))
        art = DBO.Article()
        art.internal_id = checksum or create_checksum(part)
        art.content = part
        art.summary = None
        art.score = self.cfg.initial_score
        art.updated = datetime.datetime.now()
        art.title = filename + " " + file_modification.strftime("%x %X")
        art.published = file_modification
        art.link = None
        return art

    def is_file_updated(self, filename, max_age_load):
        last_refreshed = self.cfg.last_refreshed
        if last_refreshed is None:
            return True
        # if max_age_to_load defined - set limit last_refreshed
        if self.cfg.max_age_to_load > 0 or (self.cfg.max_age_to_load == 0
                                            and max_age_load > 0):
            max_age_to_load = self.cfg.max_age_to_load or max_age_load
            offset = datetime.datetime.now() - \
                    datetime.timedelta(days=max_age_to_load)
            last_refreshed = max(last_refreshed, offset)

        file_modification = datetime.datetime.fromtimestamp(
            os.path.getmtime(filename))
        if file_modification < last_refreshed:
            self.cfg.add_log(
                'info', "File not modified according to modification time")
            _LOG.info("No page %s modification since %s", self.cfg.title,
                      last_refreshed)
            return False
        return True
