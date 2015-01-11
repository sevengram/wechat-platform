# -*- coding: utf-8 -*-

import tornado.gen

import tornado.httpclient

from consts import url
from util import async_http as ahttp

from handler.site import SiteHandler


class UserHandler(SiteHandler):
    @tornado.gen.coroutine
    def put(self, site_id, *args, **kwargs):
        req_data1 = {
            'code': self.get_argument('code'),
            'appid': self.get_argument('appid'),
            'secret': '7beb21d84d4505815eb6165568b7a328',  # TODO: from db
            'grant_type': 'authorization_code',
        }
        try:
            resp1 = yield ahttp.get_dict(url=url.oauth_access_token, data=req_data1)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data1 = self.parse_oauth_resp(resp1)
        if not resp_data1:
            raise tornado.gen.Return()

        post_resp_data = {
            'openid': resp_data1['openid'],
            'unionid': resp_data1['openid'],
            'appid': self.get_argument('appid')
        }
        if 'snsapi_userinfo' in [v.strip() for v in resp_data1['scope'].split(',')]:
            req_data2 = {
                'access_token': resp_data1['access_token'],
                'openid': resp_data1['openid'],
                'lang': 'zh_CN'
            }
            try:
                resp2 = yield ahttp.get_dict(url=url.oauth_userinfo, data=req_data2)
            except tornado.httpclient.HTTPError:
                self.send_response(err_code=1001)
                raise tornado.gen.Return()

            resp_data2 = self.parse_oauth_resp(resp2, default_data=post_resp_data)
            if not resp_data2:
                raise tornado.gen.Return()
            post_resp_data.update(resp_data2)
        self.send_response(post_resp_data)