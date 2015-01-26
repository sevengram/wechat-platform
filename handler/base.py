# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen

import storage
from util import security
from consts import errno


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, sign_check=False):
        self.sign_check = sign_check
        self.storage = storage.wechat_storage
        self.post_args = {}

    def assign_arguments(self, essential, extra):
        try:
            r1 = {key: self.get_argument(key) for key in essential}
            r2 = {key: self.get_argument(key, defult) for key, defult in extra}
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(400)
        for key in essential:
            if not r1.get(key):
                raise tornado.web.HTTPError(400)
        return dict(r1, **r2)

    def get_check_key(self, refer_dict):
        raise NotImplementedError()

    def check_signature(self, refer_dict, method):
        sign_key = self.get_check_key(refer_dict)
        if not sign_key:
            self.send_response(err_code=8002)
            return False
        if not security.check_sign(refer_dict, sign_key, method):
            self.send_response(err_code=8001)
            return False
        return True

    def send_response(self, data=None, err_code=0, err_msg=''):
        resp = {'err_code': err_code,
                'err_alias': errno.err_map[err_code][0],
                'err_msg': err_msg or errno.err_map[err_code][1],
                'data': data or ''}
        self.write(resp)
        self.finish()

    def write_error(self, status_code, **kwargs):
        self.write({'err_code': status_code})
