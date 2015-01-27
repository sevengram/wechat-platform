# -*- coding: utf-8 -*-

import hashlib

import tornado.gen
import tornado.httpclient

from consts import url
from util import async_http as ahttp
from util import dtools
from handler.site_base import SiteBaseHandler


class UserHandler(SiteBaseHandler):
    def get_local_user_info(self, appid, openid):
        user_info = self.storage.get_user_info(appid=appid, openid=openid)
        return dtools.transfer(
            user_info,
            copys=[
                'appid',
                'openid',
                'unionid',
                'nickname',
                'sex',
                'city',
                'province',
                'country',
                'headimgurl'
            ]) if user_info else None

    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        yield self.put(siteid)

    @tornado.gen.coroutine
    def put(self, siteid, *args, **kwargs):
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
            resp1 = yield ahttp.get_dict(url=url.wechat_oauth_access_token, data=req_data1)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data1 = self.parse_oauth_resp(resp1)
        openid = resp_data1['openid']
        if resp_data1:
            post_resp_data = {
                'openid': openid,
                'appid': appid
            }

            # Search user info from local db
            local_user_info = self.get_local_user_info(appid, openid)
            if local_user_info and local_user_info.get('nickname'):
                post_resp_data.update(local_user_info)
                self.send_response(post_resp_data)
                raise tornado.gen.Return()

            if 'snsapi_userinfo' in [v.strip() for v in resp_data1['scope'].split(',')]:
                req_data2 = {
                    'access_token': resp_data1['access_token'],
                    'openid': openid,
                    'lang': 'zh_CN'
                }
                try:
                    resp2 = yield ahttp.get_dict(url=url.wechat_oauth_userinfo, data=req_data2)
                except tornado.httpclient.HTTPError:
                    self.send_response(err_code=1001)
                    raise tornado.gen.Return()
                resp_data2 = self.parse_oauth_resp(resp2)
                if resp_data2:
                    post_resp_data.update(resp_data2)
                    saved_data = dict(post_resp_data,
                                      uid=hashlib.md5(
                                          post_resp_data['appid'] + '_' + post_resp_data['openid']).hexdigest(),
                                      lang=post_resp_data.get('language', ''))
                    self.storage.add_user_info(saved_data, noninsert=['privilege', 'language'])
            self.send_response(post_resp_data)