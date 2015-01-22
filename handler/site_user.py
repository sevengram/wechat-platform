# -*- coding: utf-8 -*-

import hashlib

import tornado.gen
import tornado.httpclient

from consts import url
from util import async_http as ahttp
from handler.site_base import SiteBaseHandler


class UserHandler(SiteBaseHandler):
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
            resp1 = yield ahttp.get_dict(url=url.oauth_access_token, data=req_data1)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data1 = self.parse_oauth_resp(resp1)
        if resp_data1:
            post_resp_data = {
                'openid': resp_data1['openid'],
                'appid': self.get_argument('appid')
            }
            if 'snsapi_userinfo' in [v.strip() for v in resp_data1['scope'].split(',')]:
                req_data2 = {
                    'access_token': resp_data1['access_token'],
                    'openid': resp_data1['openid'],
                    'lang': 'zh_CN'
                }
                # TODO: check db first
                try:
                    resp2 = yield ahttp.get_dict(url=url.oauth_userinfo, data=req_data2)
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