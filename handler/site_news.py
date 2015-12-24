# -*- coding: utf-8 -*-

import tornado.gen

from handler.site_base import SiteBaseHandler
from wxclient import mock_browser


class NewsHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')
        title = self.get_argument('title')
        picurl = self.get_argument('picurl')
        content = self.get_argument('content')
        digest = self.get_argument('digest')
        source_url = self.get_argument('source_url', '')

        resp = yield mock_browser.get_ticket(appid)
        if resp['err_code'] == 0:
            self.send_response()
            ticket = resp['data']['ticket']
            resp = yield mock_browser.upload_image(appid, ticket, picurl, picurl.split('/')[-1], width=640)
            if resp['err_code'] == 0:
                fileid = resp['data']['content']
                yield mock_browser.save_news(appid, title, content, digest, '', fileid, source_url)
        else:
            self.send_response(err_code=resp['err_code'], err_msg=resp.get('err_msg', ''))

    @tornado.gen.coroutine
    def get(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')

        resp = yield mock_browser.get_latest_news(appid)
        if resp['err_code'] != 0:
            self.send_response(err_code=resp['err_code'], err_msg=resp.get('err_msg', ''))
        else:
            self.send_response(resp['data'])
