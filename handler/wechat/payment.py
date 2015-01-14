# -*- coding: utf-8 -*-
import json

import tornado.gen
import tornado.httpclient

import consts.errcode as err
from consts.key import magento_sitekey, newbuy_apikey
from handler.wechat.base import WechatBaseHandler
from util import dtools
from util import security
from util import async_http as ahttp


class WechatPayHandler(WechatBaseHandler):
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
        req_data['unionid'] = req_data['openid']  # TODO: from db
        req_data.update(
            {
                'nonce_str': security.nonce_str(),
            }
        )
        req_key = magento_sitekey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(
                url='http://121.40.32.246/newbuy/newbuy_order/index/wechatPayment',  # TODO: from db
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            return
        if resp.code == 200:
            resp_data = json.loads(resp.body)
            self.send_response(err_code=err.alias_map.get(resp_data.get('return_code'), 9001))
        else:
            self.send_response(err_code=9002)

    def get_check_key(self, refer_dict):
        return newbuy_apikey  # TODO: from db
