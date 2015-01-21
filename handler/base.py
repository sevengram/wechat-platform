# -*- coding: utf-8 -*-

import sys

import tornado.web
import tornado.gen

from util import storage
from util import security
from consts import errcode as err


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, sign_check=False):
        self.sign_check = sign_check
        self.storage = storage.WechatStorage(host='newbuy01.mysql.rds.aliyuncs.com',
                                             user='wechat_admin',
                                             passwd='_WecAd456')

    @tornado.gen.coroutine
    def prepare(self):
        if self.sign_check:
            req_args = {k: v[0] for k, v in self.request.arguments.iteritems() if v}
            self.check_signature(req_args)

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
        resp = {'err_code': err_code,
                'err_alias': err.err_map[err_code][0],
                'err_msg': err_msg or err.err_map[err_code][1],
                'data': data or ''}
        print resp
        sys.stdout.flush()
        self.write(resp)
        self.finish()

    def write_error(self, status_code, **kwargs):
        self.write({'err_code': status_code})
        sys.stdout.flush()

    def check_signature(self, refer_dict, method='md5'):
        sign_key = self.get_check_key(refer_dict)
        if not sign_key:
            self.send_response(err_code=8002)
        if not security.check_sign(refer_dict, sign_key, method):
            self.send_response(err_code=8001)

    def get_check_key(self, refer_dict):
        raise NotImplementedError()
