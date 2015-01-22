# -*- coding: utf-8 -*-

import json

from tornado.web import HTTPError

from consts import errno
from handler.base import BaseHandler
from util import dtools
from util import security


class SiteBaseHandler(BaseHandler):
    def prepare(self):
        if self.sign_check:
            parts = self.request.path.split('/')
            self.check_signature({'siteid': parts[parts.index('sites') + 1]}, method='md5')

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

    def get_check_key(self, refer_dict):
        return self.storage.get_site_info(refer_dict['siteid'], select_key='sitekey')

    def parse_payment_resp(self, resp, sign_key):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = dtools.xml2dict(resp.body)
        if resp_data['return_code'].lower() != 'success':
            self.send_response(err_code=1001, err_msg=resp_data.get('return_msg'))
            return None
        if not security.check_sign(resp_data, sign_key, 'md5'):
            self.send_response(err_code=1002)
            return None
        if resp_data['result_code'].lower() != 'success':
            self.send_response(err_code=errno.alias_map.get(resp_data.get('err_code'), 9001),
                               err_msg=resp_data.get('err_code_des'))
            return None
        return resp_data

    def parse_oauth_resp(self, resp):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = json.loads(resp.body)
        if resp_data.get('errcode'):
            self.send_response(None, *errno.wechat_map[int(resp_data.get('errcode'))])
            return None
        return resp_data
