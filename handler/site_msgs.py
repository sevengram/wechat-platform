# -*- coding: utf-8 -*-

import tornado.gen

from handler.site_base import SiteBaseHandler
from wxclient import mock_browser
from wxstorage import wechat_storage


class MsgsHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')
        openid = self.get_argument('openid')
        msg_type = self.get_argument('msg_type')
        content = self.get_argument('content', '')

        fakeid = wechat_storage.get_user_info(appid=appid, openid=openid, select_key='fakeid')
        if fakeid:
            if msg_type == 'text' and content:
                result = yield mock_browser.send_single_message(appid, fakeid, content)
                if result['err_code'] == 0:
                    self.send_response()
                else:
                    self.send_response(result['err_code'])
            else:
                self.send_response(4101)
        else:
            self.send_response(err_code=7102)

            # TODO: use offical api if authorize


class MultiMsgsHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')
        groupid = self.get_argument('groupid', -1)
        appmsgid = self.get_argument('appmsgid')
        resp = yield mock_browser.get_operation_seq(appid)
        if resp['err_code'] != 0:
            self.send_response(err_code=resp['err_code'], err_msg=resp.get('err_msg', ''))
            return
        seq = resp['data']['seq']
        for i in range(2):
            resp = yield mock_browser.presend_multi_message(appid, appmsgid, i)
            if resp['err_code'] != 0:
                self.send_response(err_code=resp['err_code'], err_msg=resp.get('err_msg', ''))
                return
        resp = yield mock_browser.send_multi_message(appid, appmsgid, seq, groupid)
        if resp['err_code'] != 0:
            self.send_response(err_code=resp['err_code'], err_msg=resp.get('err_msg', ''))
        else:
            self.send_response()
