# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
import tornado.httpclient

from handler.site_base import SiteBaseHandler
from wxclient import MockBrowser


class TestHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, siteid):
        browser = MockBrowser()
        yield browser.login('wxfc87c2547449c2c6')
        result = yield browser.send_single_message('wxfc87c2547449c2c6', '1899417504', u'你好')
        self.send_response(result)