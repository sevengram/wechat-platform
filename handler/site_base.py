# -*- coding: utf-8 -*-

import json

from tornado.web import HTTPError

import errinfo
from util import dtools, security
from util.web import BaseHandler
from wxstorage import wechat_storage


class SiteBaseHandler(BaseHandler):
    def initialize(self, sign_check=True):
        super(SiteBaseHandler, self).initialize(sign_check=sign_check)
        self.storage = wechat_storage

    def prepare(self):
        if self.sign_check:
            parts = self.request.path.split('/')
            key = self.storage.get_site_info(parts[parts.index('sites') + 1], select_key='sitekey')
            self.check_signature({k: v[0].encode('utf8') for k, v in self.request.arguments.items() if v},
                                 sign_key=key, method='md5')

    def head(self, *args, **kwargs):
        raise HTTPError(405)

    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        raise HTTPError(405)

    def delete(self, *args, **kwargs):
        raise HTTPError(405)

    def patch(self, *args, **kwargs):
        raise HTTPError(405)

    def put(self, *args, **kwargs):
        raise HTTPError(405)

    def options(self, *args, **kwargs):
        raise HTTPError(405)

    def parse_payment_resp(self, resp, sign_key):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = dtools.xml2dict(resp.body.decode('utf8'))
        if resp_data['return_code'].lower() != 'success':
            self.send_response(err_code=1001, err_msg=resp_data.get('return_msg'))
            return None
        if not security.check_sign(resp_data, sign_key, 'md5'):
            self.send_response(err_code=1002)
            return None
        if resp_data['result_code'].lower() != 'success':
            self.send_response(err_code=errinfo.alias_map.get(resp_data.get('err_code'), 9001),
                               err_msg=resp_data.get('err_code_des'))
            return None
        return resp_data

    def parse_oauth_resp(self, resp):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = json.loads(resp.body.decode('utf8'))
        if resp_data.get('errcode'):
            self.send_response(None, *errinfo.wechat_map[int(resp_data.get('errcode'))])
            return None
        return resp_data

    def send_response(self, data=None, err_code=0, err_msg=''):
        resp = {'err_code': err_code,
                'err_alias': errinfo.err_map[err_code][0],
                'err_msg': err_msg or errinfo.err_map[err_code][1],
                'data': data or ''}
        self.write(resp)
        self.finish()
