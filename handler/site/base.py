# -*- coding: utf-8 -*-

import json

from tornado.web import HTTPError

from consts.key import magento_sitekey
from consts.errcode import wechat_map
from consts import errcode as err
from handler.common import CommonHandler
from util import dtools
from util import security


class SiteBaseHandler(CommonHandler):
    def head(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def get(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def post(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def delete(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def patch(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def put(self, site_id, *args, **kwargs):
        raise HTTPError(405)

    def options(self, site_id, *args, **kwargs):
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

    def parse_oauth_resp(self, resp, default_data=None):
        if resp.code != 200:
            if not default_data:
                self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
                return None
            else:
                self.send_response(default_data)
                return None
        resp_data = json.loads(resp.body)
        if resp_data.get('errcode'):
            if not default_data:
                self.send_response(None, *wechat_map.get(int(resp_data.get('errcode'))))
                return None
            else:
                self.send_response(default_data)
                return None
        return resp_data
