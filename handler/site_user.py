# -*- coding: utf-8 -*-

import hashlib

import tornado.gen
import tornado.httpclient

import url
import wxclient
from handler.site_base import SiteBaseHandler
from util import http
from util import dtools


class UserHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, siteid, openid, *args, **kwargs):
        # Search user info from db
        user_info = self.storage.get_user_info(appid=self.get_argument('appid'), openid=openid)
        get_resp_data = dtools.transfer(
            user_info,
            copys=[
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
                'headimgurl',
                'subscribe_time'
            ])
        self.send_response(get_resp_data)

    @tornado.gen.coroutine
    def put(self, siteid, openid, *args, **kwargs):
        appid = self.get_argument('appid')
        # Update user info from wechat
        user_info_result = yield wxclient.get_user_info(appid, openid)
        err_code = user_info_result.get('err_code', 1)
        if err_code != 0:
            self.send_response(err_code=err_code)
        else:
            post_resp_data = dict(user_info_result['data'],
                                  appid=appid,
                                  uid=hashlib.md5(appid + '_' + openid).hexdigest(),
                                  lang=user_info_result['data'].get('language', ''))
            self.send_response(data=post_resp_data)
            self.storage.add_user_info(post_resp_data, noninsert=['remark', 'language'])

    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        appid = self.get_argument('appid')
        appinfo = self.storage.get_app_info(appid=appid)
        if not appinfo:
            self.send_response(err_code=3201)
            raise tornado.gen.Return()

        req_data1 = {
            'code': self.get_argument('code'),
            'appid': appid,
            'secret': appinfo['secret'],
            'grant_type': 'authorization_code',
        }
        try:
            resp1 = yield http.get_dict(url=url.wechat_oauth_access_token, data=req_data1)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data1 = self.parse_oauth_resp(resp1)
        if resp_data1:
            openid = resp_data1['openid']
            post_resp_data = {
                'openid': openid,
                'appid': appid,
                'uid': hashlib.md5(appid + '_' + openid).hexdigest()
            }
            # Get user info from wechat
            if 'snsapi_userinfo' in [v.strip() for v in resp_data1['scope'].split(',')]:
                req_data2 = {
                    'access_token': resp_data1['access_token'],
                    'openid': openid,
                    'lang': 'zh_CN'
                }
                try:
                    resp2 = yield http.get_dict(url=url.wechat_oauth_userinfo, data=req_data2)
                except tornado.httpclient.HTTPError:
                    self.send_response(err_code=1001)
                    raise tornado.gen.Return()
                resp_data2 = self.parse_oauth_resp(resp2)
                if resp_data2:
                    post_resp_data.update(resp_data2)
                    post_resp_data['lang'] = post_resp_data.get('language', '')
            self.send_response(post_resp_data)
            self.storage.add_user_info(post_resp_data, noninsert=['privilege', 'language'])
