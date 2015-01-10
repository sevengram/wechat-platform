# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen

from consts import err_code as err
from util import security


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, sign_check=False, sign_key=''):
        self.sign_check = sign_check
        self.sign_key = sign_key

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        if self.sign_check and self.sign_key and not security.check_signature(self.request.arguments, self.sign_key):
            self.send_response(err_code=8001)
            raise tornado.gen.Return(True)
        else:
            raise tornado.gen.Return(False)

    def prepare(self):
        pass

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

    def write_error(self, status_code, **kwargs):
        self.write({'err_code': status_code})

