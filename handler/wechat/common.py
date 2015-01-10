# -*- coding: utf-8 -*-

from pyexpat import ExpatError

import tornado.gen
from tornado.web import HTTPError

from handler.base import BaseHandler

from util import security
from util import dtools
from consts import err_code as err


class WechatCommonHandler(BaseHandler):
    def initialize(self, sign_check=False, sign_key=''):
        super(WechatCommonHandler, self).initialize(sign_check, sign_key)
        self.post_args = {}

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        try:
            self.post_args = dtools.xml2dict(self.request.body)
        except ExpatError:
            raise HTTPError(400)
        if self.sign_check and self.sign_key and not security.check_signature(self.post_args, self.sign_key):
            self.send_response(err_code=8001)
            raise tornado.gen.Return(True)
        else:
            raise tornado.gen.Return(False)

    def send_response(self, data=None, err_code=0, err_msg=''):
        if not data:
            data = {}
        data['return_code'] = err.simple_map.get(err_code) or 'FAIL'
        data['return_msg'] = err.simple_map.get(err_code) or 'ERROR'
        self.write(dtools.dict2xml(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        data = {'return_code': 'FAIL', 'return_msg': str(status_code)}
        self.write(dtools.dict2xml(data))
