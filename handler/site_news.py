# -*- coding: utf-8 -*-

import tornado.gen

from handler.site_base import SiteBaseHandler
from wxclient import mock_browser


class NewsHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')
        resp = yield mock_browser.get_ticket(appid)
        if resp['err_code'] != 0:
            self.send_response(err_code=resp['err_code'])
            raise tornado.gen.Return()
        ticket = resp['data']['ticket']
        resp = yield mock_browser.upload_image(appid, ticket, "http://www.mydeepsky.com/image/solar/Earth.jpg", "1.jpg",
                                               300)
        print resp
