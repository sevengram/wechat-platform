# -*- coding: utf-8 -*-

import tornado.gen
import tornado.httpclient

import url
import wxclient
from handler.site_base import SiteBaseHandler
from util import httputils, dtools

user_attrs = [
    'uid',
    'appid',
    'openid',
    'unionid',
    'nickname',
    'subscribe',
    'sex',
    'city',
    'province',
    'country',
    'language',
    'headimgurl',
    'subscribe_time']


class UserHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, siteid, uid):
        # Search user info from db
        user_info = self.storage.get_user_info(uid)
        get_resp_data = dtools.transfer(user_info, copys=user_attrs)
        self.send_response(get_resp_data)

    @tornado.gen.coroutine
    def put(self, siteid, uid):
        user_info = self.storage.get_user_info(uid)
        # Update user info from wechat
        resp = yield wxclient.update_user_info(user_info['appid'], user_info['openid'])
        if resp['err_code'] != 0:
            self.send_response(err_code=resp['err_code'])
        else:
            resp['data']['uid'] = int(uid)
            self.send_response(data=resp['data'])

    @tornado.gen.coroutine
    def post(self, siteid):
        appid = self.get_argument('appid')
        appinfo = self.storage.get_app_info(appid=appid)
        if not appinfo:
            self.send_response(err_code=3201)
            raise tornado.gen.Return()

        openid = self.get_argument('openid', '')
        if openid:
            res = yield wxclient.update_user_info(appid, openid)
            if res['err_code'] == 0:
                self.send_response(data=res['data'])
                raise tornado.gen.Return()

        code = self.get_argument('code', '')
        if code:
            req_data1 = {
                'code': code,
                'appid': appid,
                'secret': appinfo['secret'],
                'grant_type': 'authorization_code',
            }
            try:
                resp1 = yield httputils.get_dict(url=url.wechat_oauth_access_token, data=req_data1)
            except tornado.httpclient.HTTPError:
                self.send_response(err_code=1001)
                raise tornado.gen.Return()

            resp_data1 = self.parse_oauth_resp(resp1)
            if resp_data1:
                openid = resp_data1['openid']
                res = {
                    'openid': openid,
                    'appid': appid,
                }
                # Get user info from wechat
                if 'snsapi_userinfo' in [v.strip() for v in resp_data1['scope'].split(',')]:
                    req_data2 = {
                        'access_token': resp_data1['access_token'],
                        'openid': openid,
                        'lang': 'zh_CN'
                    }
                    try:
                        resp2 = yield httputils.get_dict(url=url.wechat_oauth_userinfo, data=req_data2)
                    except tornado.httpclient.HTTPError:
                        self.send_response(err_code=1001)
                        raise tornado.gen.Return()
                    resp_data2 = self.parse_oauth_resp(resp2)
                    if resp_data2:
                        res.update(resp_data2)
                post_resp_data = dtools.transfer(res, copys=user_attrs, allow_empty=False)
                self.send_response(post_resp_data)
                self.storage.add_user_info(post_resp_data)
                raise tornado.gen.Return()
        self.send_response(err_code=1)
