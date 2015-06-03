#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Web source plugin - configuration gui"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2014-2015"
__version__ = "2015-02-15"

import logging
import base64

from PyQt4 import QtGui, QtCore

from mna.gui import _validators

from . import frm_sett_web_ui
from . import dlg_sett_web_xpath_ui

_LOG = logging.getLogger(__name__)


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
    for (var i = 0; i < siblings.length; i++) {
        var sibling = siblings[i];
        if (sibling === element) {
            var tagname = element.localName;
            if (tagname != "tbody" && tagname != "tfoot") {
                return getXPath(element.parentNode) + '/' + tagname + '[' + (ix + 1) + ']';
            } else {
                return getXPath(element.parentNode);
            }
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
