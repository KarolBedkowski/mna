#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin """

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-01-18"

import hashlib
import datetime
import logging
import difflib
import base64

from PyQt4 import QtGui, QtCore

from mna.model import base
from mna.model import dbobjects as DBO
from mna.plugins import frm_sett_web_ui
from mna.plugins import dlg_sett_web_xpath_ui
from mna.gui import _validators
from mna.lib import websupport

_LOG = logging.getLogger(__name__)


def create_checksum(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest().lower()


def create_config_hash(source):
    conf = source.conf
    return create_checksum("|".join((conf['url'], conf['mode'],
                                     conf['xpath'])))


def accept_page(article, _session, source, threshold):
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
        content = article['content']
        similarity = difflib.SequenceMatcher(None, last.content,
                                             content).ratio()
        _LOG.debug("similarity: %r %r", similarity, threshold)
        if similarity > threshold:
            _LOG.debug("Article skipped - similarity %r > %r",
                       similarity, threshold)
            return False
        article['meta']['similarity'] = similarity
    return True


class FrmSettWeb(QtGui.QFrame):  # pylint: disable=no-member
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)  # pylint: disable=no-member
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
        if dlg.exec_() == QtGui.QDialog.Accepted:  # pylint: disable=no-member
            self._ui.e_url.setText(dlg.url)
            self._ui.e_xpath.setPlainText(dlg.xpath)


class WebSource(base.AbstractSource):
    """Load article from website"""

    name = "Web Page Source"
    conf_panel_class = FrmSettWeb
    default_icon = ":icons/web-icon.svg"

    def __init__(self, cfg):
        super(WebSource, self).__init__(cfg)
        self._icon = None

    def get_items(self, session=None, max_load=-1, max_age_load=-1):
        url = self.cfg.conf.get("url") if self.cfg.conf else None
        if not url:
            return []

        _LOG.info("WebSource.get_items src=%r from %r - %r", self.cfg.oid,
                  url, self.cfg.conf)
        if not self.cfg.meta:
            self.cfg.meta = {}
        try:
            info, page = websupport.download_page(
                url, self.cfg.meta.get('etag'),
                self.cfg.meta.get('last-modified'))
        except websupport.LoadPageError, err:
            self.cfg.add_log('error',
                             "Error loading page: " + str(err))
            raise base.GetArticleException("Get web page error: %s" % err)

        self.cfg.meta['last-modified'] = info['_modified']
        self.cfg.meta['etag'] = info.get('etag')

        if info['_status'] == 304:  # not modified
            _LOG.info("WebSource.get_items %r from %r - not modified",
                      self.cfg.oid, url)
            return []

        if not self.cfg.icon_id:
            icon, name = websupport.get_icon(url, page, info['_encoding'])
            if icon:
                name = "_".join(('src', str(self.cfg.oid), name))
                self.cfg.icon_id = name
                self._resources[name] = icon
            else:
                self.cfg.icon_id = self.default_icon

        if self.cfg.title == "":
            self.cfg.title = websupport.get_title(page, info['_encoding'])

        if not self.is_page_updated(info, max_age_load):
            _LOG.info("WebSource.get_items src=%r page not updated",
                      self.cfg.oid)
            return []

        parts = self._get_articles(info, page)
        articles = self._prepare_articles(parts)
        articles = self._filter_articles(articles, session)
        articles = (self._create_article(art, info) for art in articles)
        articles = filter(None, articles)

        _LOG.debug("WebSource: loaded %d articles", len(articles))
        if not articles:
            self.cfg.add_log('info', "Not found new articles")
            return []
        self.cfg.add_log('info', "Found %d new articles" % len(articles))
        # Limit number articles to load
        articles = self._limit_articles(articles, max_load)
        return articles

    @classmethod
    def get_info(cls, source_conf, _session=None):
        info = [('URL', source_conf.conf.get("url"))]
        mode = source_conf.conf.get("mode")
        if mode == "part":
            info.append(('Mode', 'page parts'))
            info.append(("Selector", source_conf.conf.get('xpath')))
        elif mode == "page_one_part":
            info.append(('Mode', 'one page part'))
            info.append(("Selector", source_conf.conf.get('xpath')))
            info.append(("Similarity level",
                         str(source_conf.conf.get('similarity', 1) * 100)))
        else:
            info.append(('Mode', 'load whole page'))
            info.append(("Similarity level",
                         str(source_conf.conf.get('similarity', 1) * 100)))
        if __debug__:
            if source_conf.conf:
                info.extend(("CONF: " + key, unicode(val))
                            for key, val in source_conf.conf.iteritems())
            if source_conf.meta:
                info.extend(("META: " + key, unicode(val))
                            for key, val in source_conf.meta.iteritems())
        return info

    def _get_articles(self, info, page):
        selector = self.cfg.conf.get('xpath')
        mode = self.cfg.conf.get("mode")
        articles = []
        if mode == "part" and selector:
            articles = websupport.get_page_part(info, page, selector)
        elif mode == "page_one_part" and selector:
            parts = list(websupport.get_page_part(info, page, selector))
            if parts:
                articles = [parts[0]]
        else:
            articles = websupport.get_page_part(info, page, "//html")
        return articles

    def _prepare_articles(self, parts):  # pylint:disable=no-self-use
        for part in parts:
            yield {'content': part,
                   'checksum': create_checksum(part),
                   'meta': {}}

    def _filter_articles(self, articles, session):
        selector = self.cfg.conf.get('xpath')
        mode = self.cfg.conf.get("mode")
        if mode == "part" and selector:
            cache = set(self._get_existing_articles(session))
            articles = (art for art in articles
                        if art['checksum'] not in cache)
        else:
            sim = self.cfg.conf.get('similarity') or 1
            articles = (art for art in articles
                        if accept_page(art, session, self.cfg, sim))
        return articles

    def _create_article(self, article, info):
        content = article['content']
        art = DBO.Article()
        art.internal_id = article['checksum']
        art.content = content
        art.summary = None
        art.score = self.cfg.initial_score
        art.title = websupport.get_title(content, info['_encoding'])
        art.updated = datetime.datetime.now()
        art.published = info.get('_last-modified')
        art.link = self.cfg.conf.get('url')
        art.meta = {'conf': create_config_hash(self.cfg)}
        art.meta.update(article['meta'])
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

    def _get_existing_articles(self, session):
        return (row[0] for row in session.query(DBO.Article.internal_id).
                filter_by(source_id=self.cfg.oid))


class _DlgSettWebXPath(QtGui.QDialog):  # pylint: disable=no-member
    """ Select web page element dialog. """

    def __init__(self, parent, url, xpath=None):
        QtGui.QDialog.__init__(self, parent)  # pylint: disable=no-member
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
        self._ui.web_page.load(QtCore.QUrl(url))  # pylint: disable=no-member

    @property
    def xpath(self):
        return self._ui.e_xpath.toPlainText()

    def done(self, result):
        if result == QtGui.QDialog.Accepted:  # pylint: disable=no-member
            if not self.url:
                self._ui.e_url.focus()
                return False
        return QtGui.QDialog.done(self, result)  # pylint: disable=no-member

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
        # pylint: disable=no-member
        page.settings().setUserStyleSheetUrl(QtCore.QUrl(css))

    @QtCore.pyqtSlot(str)  # pylint: disable=no-member
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
