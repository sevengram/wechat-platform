# -*- coding: utf-8 -*-

from pyexpat import ExpatError

import tornado.gen
import tornado.web

from util import dtools
from consts import err_code as err
from handler.base import BaseHandler


class WechatCommonHandler(BaseHandler):
    def initialize(self, sign_check=False):
        super(WechatCommonHandler, self).initialize(sign_check)
        self.post_args = {}

    @tornado.gen.coroutine
    def prepare(self):
        try:
            self.post_args = dtools.xml2dict(self.request.body)
        except ExpatError:
            raise tornado.web.HTTPError(400)
        self.check_sign(self.post_args)

    def send_response(self, data=None, err_code=0, err_msg=''):
        if not data:
            data = {}
        data['return_code'] = err.simple_map.get(err_code, ('FAIL', 'ERROR'))[0]
        data['return_msg'] = err.code_map.get(err_code, ('FAIL', 'ERROR'))[1]
        self.write(dtools.dict2xml(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        data = {'return_code': 'FAIL', 'return_msg': str(status_code)}
        self.write(dtools.dict2xml(data))
