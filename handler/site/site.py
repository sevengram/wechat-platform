# -*- coding: utf-8 -*-

import json

from tornado.web import HTTPError

from consts.key import magento_sitekey
from consts.errcode import wechat_map
from consts import errcode as err
from handler.base import BaseHandler
from util import dtools
from util import security


class SiteHandler(BaseHandler):
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
        return magento_sitekey  # TODO: from db

    def parse_payment_resp(self, resp, sign_key):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = dtools.xml2dict(resp.body)
        if resp_data['return_code'].lower() != 'success':
            self.send_response(err_code=1001, err_msg=resp_data.get('return_msg'))
            return None
        if not security.check_sign(resp_data, sign_key):
            self.send_response(err_code=1002)
            return None
        if resp_data['result_code'].lower() != 'success':
            self.send_response(err_code=err.alias_map.get(resp_data.get('err_code'), 9001),
                               err_msg=resp_data.get('err_code_des'))
            return None
        return resp_data

    def parse_oauth_resp(self, resp):
        if resp.code != 200:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
            return None
        resp_data = json.loads(resp.body)
        if resp_data.get('errcode'):
            self.send_response(None, *wechat_map[int(resp_data.get('errcode'))])
            return None
        return resp_data
