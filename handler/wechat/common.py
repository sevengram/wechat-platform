# -*- coding: utf-8 -*-

from pyexpat import ExpatError

import tornado.gen
import tornado.web

import consts.errcode as err
from util import dtools
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
        if self.sign_check:
            self.check_signature(self.post_args)

    def send_response(self, data=None, err_code=0, err_msg=''):
        if not data:
            data = {}
        data['return_code'] = err.simple_map.get(err_code)[0]
        data['return_msg'] = err.err_map.get(err_code)[1]
        self.write(dtools.dict2xml(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        data = {'return_code': 'FAIL', 'return_msg': str(status_code)}
        self.write(dtools.dict2xml(data))
