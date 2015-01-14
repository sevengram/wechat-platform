# -*- coding:utf8 -*-

import time

import tornado.web
import tornado.gen
import tornado.httpclient

from util import dtools
from util import security
from util import async_http as ahttp
from consts import url
from consts.key import newbuy_apikey
from handler.site.base import SiteBaseHandler


class OrderHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, site_id, out_trade_no, *args, **kwargs):
        req_data = {
            'appid': self.get_argument('appid'),
            'mch_id': '10010984',  # TODO: from db
            'transaction_id': '',  # TODO: from db
            'out_trade_no': out_trade_no,
            'nonce_str': security.nonce_str(),
        }
        req_key = newbuy_apikey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(url=url.order_query, data=req_data, data_type='xml')
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data = self.parse_payment_resp(resp, req_key)
        if resp_data:
            post_resp_data = dtools.transfer(
                resp_data,
                copys=[
                    'appid',
                    'trade_state',
                    'out_trade_no',
                    'total_fee',
                    'transaction_id',
                    'attach',
                    'time_end'
                ]
            )
            self.send_response(post_resp_data)


class PrepayHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, site_id, *args, **kwargs):
        parse_args = self.assign_arguments(
            essential=['appid',
                       'title',
                       'out_trade_no',
                       'total_fee',
                       'spbill_create_ip',
                       'trade_type',
                       'site_notify_url',
                       'nonce_str',
                       'sign'],
            extra=[('detail', ''),
                   ('goods_tag', ''),
                   ('unionid', ''),
                   ('openid', '')]
        )
        if not parse_args.get('unionid') and not parse_args.get('openid'):
            raise tornado.web.HTTPError(400)
        req_data = dtools.transfer(
            parse_args,
            copys=['appid',
                   'out_trade_no',
                   'total_fee',
                   'spbill_create_ip',
                   'trade_type',
                   'detail',
                   'openid',
                   'goods_tag',
                   'attach'],
            renames=[('title', 'body')]
        )
        if not req_data.get('openid'):
            req_data['openid'] = req_data['unionid']  # TODO: search by unionId from db
        req_data.update(
            {
                'mch_id': '10010984',  # TODO: from db
                'nonce_str': security.nonce_str(),
                'notify_url': url.payment_notify,
            }
        )
        req_key = newbuy_apikey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(url=url.order_add, data=req_data, data_type='xml')
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data = self.parse_payment_resp(resp, req_key)
        if resp_data:
            post_resp_data = {
                'appid': resp_data['appid'],
                'timestamp': str(int(time.time())),
                'noncestr': security.nonce_str(),
                'prepay_id': resp_data['prepay_id'],
                'sign_type': 'MD5'
            }
            post_resp_data['pay_sign'] = security.build_sign(post_resp_data, req_key)
            self.send_response(post_resp_data)