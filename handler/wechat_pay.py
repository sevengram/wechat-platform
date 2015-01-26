# -*- coding: utf-8 -*-

import json

import tornado.gen
import tornado.httpclient

from consts import errno
from handler.base import BaseHandler
from util import dtools
from util import security
from util import async_http as ahttp


class WechatPayHandler(BaseHandler):
    @tornado.gen.coroutine
    def prepare(self):
        self.post_args = dtools.xml2dict(self.request.body)
        if self.sign_check:
            self.check_signature(self.post_args, method='md5')

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
                   'time_end']
        )
        req_data.update(
            {
                'unionid': self.storage.get_user_info(appid=req_data['appid'],
                                                      openid=req_data['openid'],
                                                      select_key='unionid'),
                'nonce_str': security.nonce_str()
            }
        )
        attach = dict([t.split('=') for t in self.post_args['attach'].split(',')])
        site_info = self.storage.get_site_info(siteid=attach['siteid'])
        req_key = site_info['sitekey']
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
                self.send_response(err_code=errno.alias_map.get(resp_data.get('return_code'), 9001))
            except ValueError:
                self.send_response(err_code=9101)
        else:
            self.send_response(err_code=9002)

    def get_check_key(self, refer_dict):
        return self.storage.get_app_info(appid=refer_dict['appid'], select_key='apikey')

    def send_response(self, data=None, err_code=0, err_msg=''):
        if not data:
            data = {}
        data['return_code'] = errno.simple_map[err_code][0]
        data['return_msg'] = errno.err_map[err_code][1]
        self.write(dtools.dict2xml(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        data = {'return_code': 'FAIL', 'return_msg': str(status_code)}
        self.write(dtools.dict2xml(data))
