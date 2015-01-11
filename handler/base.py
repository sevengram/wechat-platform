# -*- coding: utf-8 -*-
import sys

import tornado.web
import tornado.gen

from util import security
from consts import err_code as err


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, sign_check=False):
        self.sign_check = sign_check

    @tornado.gen.coroutine
    def prepare(self):
        req_args = {k: v[0] for k, v in self.request.arguments.iteritems() if v}
        self.check_sign(req_args)

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

    def send_response(self, data=None, err_code=0, err_msg=''):
        self.write(
            {'err_code': err_code,
             'err_alias': err.code_map[err_code][0],
             'err_msg': err_msg or err.code_map[err_code][1],
             'data': data or ''})
        self.finish()
        sys.stdout.flush()

    def write_error(self, status_code, **kwargs):
        self.write({'err_code': status_code})
        sys.stdout.flush()

    def check_sign(self, refer_dict):
        if self.sign_check:
            sign_key = self.get_check_key(refer_dict)
            if not sign_key:
                self.send_response(err_code=8002)
                return False
            if not security.check_signature(refer_dict, sign_key):
                self.send_response(err_code=8001)
                return False
        return True

    def get_check_key(self, refer_dict):
        raise NotImplementedError()
