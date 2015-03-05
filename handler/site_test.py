# -*- coding: utf-8 -*-
import sys

import tornado.web
import tornado.gen
import tornado.httpclient

from handler.site_base import SiteBaseHandler
from wxclient import MockBrowser
import wxclient


class TestHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, siteid):
        # browser = MockBrowser()
        # yield browser.login('wxfc87c2547449c2c6')
        # yield browser.send_single_message('wxfc87c2547449c2c6', '1899417504', u'你好')
        result = yield wxclient.get_user_info('wxfc87c2547449c2c6', 'owPaGjv_SB5DnzAQN4_knohnvC_I')
        # result = yield browser.find_user('wxfc87c2547449c2c6', 1425542418, u'云南省昆明市东川区', 'text')
        print result
        sys.stdout.flush()
        self.send_response(data=result.get('data', ''), err_code=result.get('err_code', 0))