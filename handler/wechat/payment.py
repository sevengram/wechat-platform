# -*- coding: utf-8 -*-

import json

import tornado.web
import tornado.gen
import tornado.httpclient

import model
import consts.errcode as err
from handler.base import BaseHandler
from util import dtools
from util import security
from util import async_http as ahttp


class WechatPayHandler(BaseHandler):
    def initialize(self, sign_check=False):
        super(WechatPayHandler, self).initialize(sign_check)
        self.post_args = {}

    @tornado.gen.coroutine
    def prepare(self):
        self.post_args = dtools.xml2dict(self.request.body)
        if self.sign_check:
            self.check_signature(self.post_args)

    @tornado.gen.coroutine
    def post(self):
        req_data = dtools.transfer(
            self.post_args,
            copys=['appid',
                   'result_code',
                   'err_code_des',
                   'out_trade_no',
                   'total_fee',
                   'openid',
                   'transaction_id',
                   'attach',
                   'time_end']
        )
        req_data.update(
            {
                'unionid': req_data['openid'],  # TODO: from db
                'nonce_str': security.nonce_str()
            }
        )
        siteid = 'newbuy'  # TODO: code here
        site_info = self.storage.get_site_info(siteid=siteid)
        req_key = model.Siteinfo(site_info).get_sitekey()
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(
                url=site_info['pay_notify_url'],
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            return

        if resp.code == 200:
            try:
                resp_data = json.loads(resp.body)
                self.send_response(err_code=err.alias_map.get(resp_data.get('return_code'), 9001))
            except ValueError:
                self.send_response(err_code=9101)
        else:
            self.send_response(err_code=9002)

    def get_check_key(self, refer_dict):
        appid = refer_dict['appid']
        appinfo = self.storage.get_app_info(appid=appid)
        return model.Appinfo(appinfo).get_apikey()

    def send_response(self, data=None, err_code=0, err_msg=''):
        if not data:
            data = {}
        data['return_code'] = err.simple_map[err_code][0]
        data['return_msg'] = err.err_map[err_code][1]
        self.write(dtools.dict2xml(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        data = {'return_code': 'FAIL', 'return_msg': str(status_code)}
        self.write(dtools.dict2xml(data))
