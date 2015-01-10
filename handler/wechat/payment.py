# -*- coding: utf-8 -*-
import json

import tornado.web

import tornado.gen
import tornado.httpclient

import consts.err_code as err
from consts.key import newbuy_apikey
from handler.wechat.common import WechatCommonHandler
from util import dtools
from util import security


class WechatPayHandler(WechatCommonHandler):
    @tornado.gen.coroutine
    def post(self):
        if (yield super(WechatPayHandler, self).post()):
            # Finish in super
            return
        data = dtools.transfer(
            self.post_args,
            copys=['appid',
                   'result_code',
                   'err_code_des',
                   'out_trade_no',
                   'total_fee',
                   'unionid',
                   'transaction_id',
                   'attach',
                   'time_end']
        )
        data.update(
            {
                'nonce_str': security.nonce_str(),
            }
        )
        data['sign'] = security.build_signature(data, newbuy_apikey)
        client = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(
            url='http://121.40.32.246/newbuy/newbuy_order/index/wechatPayment',  # TODO: from db
            method='POST',
            body=json.dumps(data)
        )
        try:
            resp = yield client.fetch(req)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1)
            return
        if resp.code == 200:
            resp_data = json.loads(resp.body)
            self.send_response(err_code=err.alias_map.get(resp_data.get('return_code'), 9001))
        else:
            self.send_response(err_code=1)

