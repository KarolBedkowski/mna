#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import urllib2
import hashlib
import time
import datetime
import logging
import itertools
import difflib
import base64

from lxml import etree
from PyQt4 import QtGui, QtCore

from mna.model import base
from mna.model import db
from mna.model import dbobjects as DBO
from mna.plugins import frm_sett_web_ui
from mna.plugins import dlg_sett_web_xpath_ui
from mna.gui import _validators

_LOG = logging.getLogger(__name__)


class LoadPageError(RuntimeError):
    pass


def download_page(url):
    """ Download Page from `url` """
    try:
        conn = urllib2.urlopen(url)
        info = dict(conn.headers)
        info['_url'] = url
        info['_encoding'] = conn.headers.getencoding()
        if info['_encoding'] == '7bit':
            info['_encoding'] = None
        modified = conn.headers.getdate('last-modified') or \
                conn.headers.getdate('last-modified')
        info['_last_modified'] = \
                datetime.datetime.fromtimestamp(time.mktime(modified)) \
                if modified else None
        content = conn.read()
        return info, content
    except urllib2.URLError, err:
        raise LoadPageError(err)


def get_page_part(info, page, selector):
    """ Find all elements of `page` by `selector` xpath expression. """
    content_type = info.get('content-type')
    if content_type and content_type.startswith('text/html'):
        parser = etree.HTMLParser(encoding='UTF-8', remove_blank_text=True,
                                  remove_comments=True, remove_pis=True)
    else:
        parser = etree.XMLParser(recover=True, encoding='UTF-8')
    tree = etree.fromstring(page, parser)
    for elem in itertools.chain(tree.xpath("//comment()"),
                                tree.xpath("//script"),
                                tree.xpath("//style")):
        elem.getparent().remove(elem)
    return (unicode(etree.tostring(elem, encoding='utf-8',
                                   method='html').strip(),
                    encoding='utf-8', errors="replace")
            for elem in tree.xpath(selector))


def create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest().lower()


def create_config_hash(source):
    conf = source.conf
    return create_checksum("|".join((conf['url'], conf['mode'],
                                     conf['xpath'])))


def get_title(html, encoding):
    parser = etree.HTMLParser(encoding=encoding, remove_blank_text=True,
                              remove_comments=True, remove_pis=True)
    # try to find title
    tree = etree.fromstring(html, parser)
    for tag in ('//head/title', '//h1', '//h2'):
        titles = tree.xpath(tag)
        if titles:
            title = titles[0].text
            if title:
                title = title.strip()
                if title:
                    return title

    # title not found, use page text
    html = etree.tostring(tree, encoding='UTF-8', method="text")
    title = unicode(html.replace('\n', ' ').replace('\t', ' ').
                    replace('\r', ' ').strip(), 'UTF-8')
    if len(title) > 100:
        title = title[:97] + "..."
    return title


def articles_similarity(art1, art2):
    return difflib.SequenceMatcher(None, art1, art2).ratio()


def accept_part(session, source_id, checksum):
    """ Check is given part don't already exists in database for given  part
        `checksum` and `source_id`.
    """
    return db.count(DBO.Article, session=session, internal_id=checksum,
                    source_id=source_id) == 0


def accept_page(page, session, source, threshold):
    """ Check is page change from last time, optionally check similarity ratio
        if `threshold`  given - reject pages with similarity ratio > threshold.
    """
    # find last article
    last = source.get_last_article()
    if last:
        if last.meta:
            # check for parameters changed
            last_conf_hash = last.meta.get('conf')
            if not last_conf_hash or \
                    last_conf_hash != create_config_hash(source):
                return True
        similarity = articles_similarity(last.content, page)
        _LOG.debug("similarity: %r %r", similarity, threshold)
        if similarity > threshold:
            _LOG.debug("Article skipped - similarity %r > %r",
                       similarity, threshold)
            return False
    return True


class FrmSettWeb(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self._ui = frm_sett_web_ui.Ui_FrmSettWeb()
        self._ui.setupUi(self)
        self._ui.b_path_sel.clicked.connect(self._on_btn_xpath_sel)

    def validate(self):
        try:
            _validators.validate_empty_string(self._ui.e_url, 'URL')
            if self._ui.rb_scan_parts.isChecked():
                _validators.validate_empty_string(self._ui.e_xpath, 'Xpath')
        except _validators.ValidationError:
            return False
        return True

    def from_window(self, source):
        source.conf["url"] = self._ui.e_url.text()
        source.conf["xpath"] = self._ui.e_xpath.toPlainText()
        source.conf["similarity"] = \
            self._ui.sb_similarity_ratio.value() / 100.0
        if self._ui.rb_scan_page.isChecked():
            source.conf["mode"] = "page"
        elif self._ui.rb_scan_one_part.isChecked():
            source.conf["mode"] = "page_one_part"
        else:
            source.conf["mode"] = "part"
        return True

    def to_window(self, source):
        self._ui.e_url.setText(source.conf.get("url") or "")
        self._ui.e_xpath.setPlainText(source.conf.get("xpath") or "")
        self._ui.sb_similarity_ratio.setValue((source.conf.get('similarity')
                                               or 0.5) * 100.0)
        mode = source.conf.get("mode")
        if mode == "page":
            self._ui.rb_scan_page.setChecked(True)
            self._ui.rb_scan_page.toggled.emit(True)
        elif mode == "page_one_part":
            self._ui.rb_scan_one_part.setChecked(True)
            self._ui.rb_scan_one_part.toggled.emit(True)
        else:
            self._ui.rb_scan_parts.setChecked(True)
            self._ui.rb_scan_parts.toggled.emit(True)

    def _on_btn_xpath_sel(self):
        dlg = _DlgSettWebXPath(self, self._ui.e_url.text(),
                               self._ui.e_xpath.toPlainText())
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self._ui.e_url.setText(dlg.url)
            self._ui.e_xpath.setPlainText(dlg.xpath)


class WebSource(base.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"
    conf_panel_class = FrmSettWeb

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        _LOG.info("WebSource.get_items %r from %r - %r", self.cfg.oid,
                  url, self.cfg.conf)

        try:
            info, page = download_page(url)
        except LoadPageError, err:
            self.cfg.add_log('error',
                             "Error loading page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        if self.cfg.title == "":
            self.cfg.title = get_title(page, info['_encoding'])

        if not self.is_page_updated(info, max_age_load):
            return []

        articles = []
        selector_xpath = self.cfg.conf.get('xpath')
        mode = self.cfg.conf.get("mode")
        if mode == "part" and selector_xpath:
            articles = (self._process_part(part, info, session)
                        for part in get_page_part(info, page, selector_xpath))
        elif mode == "page_one_part" and selector_xpath:
            parts = list(get_page_part(info, page, selector_xpath))
            if parts:
                articles = [self._process_page(parts[0], info, session)]
        else:
            articles = (self._process_page(part, info, session)
                        for part in get_page_part(info, page, "//html"))

        articles = filter(None, articles)

        _LOG.debug("WebSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_log('info', "Not found new articles")
            return []
        self.cfg.add_log('info', "Found %d new articles" % len(articles))
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        return articles

    def _process_page(self, page, info, session):
        if accept_page(page, session, self.cfg,
                       self.cfg.conf.get('similarity') or 1):
            return self._create_article(page, info)
        return None

    def _process_part(self, part, info, session):
        checksum = create_checksum(part)
        if accept_part(session, self.cfg.oid, checksum):
            return self._create_article(part, info, checksum)
        return None

    def _create_article(self, part, info, checksum=None):
        art = DBO.Article()
        art.internal_id = checksum or create_checksum(part)
        art.content = part
        art.summary = None
        art.score = self.cfg.initial_score
        art.title = get_title(part, info['_encoding'])
        art.updated = datetime.datetime.now()
        art.published = info.get('_last-modified')
        art.link = self.cfg.conf.get('url')
        art.meta = {'conf': create_config_hash(self.cfg)}
        return art

    def _limit_articles(self, articles, max_load):
        if self.cfg.max_articles_to_load > 0 or \
                (self.cfg.max_articles_to_load == 0 and max_load > 0):
            max_articles_to_load = self.cfg.max_articles_to_load or max_load
            if len(articles) > max_articles_to_load:
                _LOG.debug("WebSource: loaded >max_articles - truncating")
                articles = articles[-max_articles_to_load:]
                self.cfg.add_log('info',
                                 "Loaded only %d articles (limit)." %
                                 len(articles))
        return articles

    def is_page_updated(self, info, max_age_load):
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

        page_modification = info.get('_last-modified')
        if page_modification and page_modification < last_refreshed:
            self.cfg.add_log('info',
                             "Page not modified according to header")
            _LOG.info("No page %s modification since %s", self.cfg.title,
                      last_refreshed)
            return False
        return True


class _DlgSettWebXPath(QtGui.QDialog):
    """ Select web page element dialog. """

    def __init__(self, parent, url, xpath=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = dlg_sett_web_xpath_ui. Ui_DlgSettWebXPath()
        self._ui.setupUi(self)
        self._ui.e_xpath.setPlainText(xpath or "")
        self._ui.web_page.loadFinished.connect(self._on_web_page_loaded)
        self._ui.b_go.pressed.connect(self._on_btn_go)
        self._set_url(url)

    @property
    def url(self):
        return self._ui.e_url.text().strip()

    def _set_url(self, url):
        if not url:
            self._ui.e_url.setText("")
            return
        if url and not url.startswith('http://') and \
                not url.startswith('https://'):
            url = 'http://' + url
        self._ui.e_url.setText(url)
        self._ui.web_page.load(QtCore.QUrl(url))

    @property
    def xpath(self):
        return self._ui.e_xpath.toPlainText()

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            if not self.url:
                self._ui.e_url.focus()
                return False
        return QtGui.QDialog.done(self, result)

    def _on_btn_go(self):
        self._set_url(self.url)

    def _on_web_page_loaded(self, res):
        if not res:
            _LOG.info("_DlgSettWebXPath._on_web_page_loaded failed")
            return
        page = self._ui.web_page.page()
        frame = page.mainFrame()
        frame.addToJavaScriptWindowObject('click_handler', self)
        frame.evaluateJavaScript(_SEL_ELEM_JS)
        css = "data:text/css;charset=utf-8;base64," + base64.encodestring(_CSS)
        page.settings().setUserStyleSheetUrl(QtCore.QUrl(css))

    @QtCore.pyqtSlot(str)
    def click(self, message):
        """ handle custom clicks in web page """
        self._ui.e_xpath.setPlainText(message)


# based on http://stackoverflow.com/questions/2631820/im-storing-click-
# coordinates-in-my-db-and-then-reloading-them-later-and-showing/2631931#2631931
_SEL_ELEM_JS = """
function getXPath(element) {
    if (element.id !== '')
        return 'id("' + element.id + '")';
    if (element === document.body)
        return element.tagName;
    var ix = 0;
    var siblings = element.parentNode.childNodes;
    for (var i= 0; i < siblings.length; i++) {
        var sibling = siblings[i];
        if (sibling===element) {
            return getPathTo(element.parentNode) + '/' + \
                element.tagName + '[' + (ix + 1) + ']';
        }
        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
            ix++;
        }
    }
}

function clickListener(e) {
    e.preventDefault();
    var clickedElement = (window.event) ? window.event.srcElement : e.target;
    var value = getXPath(clickedElement);
    click_handler.click(value);
}

document.onclick = clickListener;

"""

_CSS = """
*:hover {border: 1px solid red !important;}
"""
