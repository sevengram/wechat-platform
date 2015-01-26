# -*- coding:utf8 -*-

import time

import tornado.web
import tornado.gen
import tornado.httpclient

from util import dtools
from util import security
from util import async_http as ahttp
from consts import url
from handler.site_base import SiteBaseHandler


class PrepayHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        parse_args = self.assign_arguments(
            essential=['appid',
                       'title',
                       'out_trade_no',
                       'total_fee',
                       'spbill_create_ip',
                       'trade_type'],
            extra=[('detail', ''),
                   ('unionid', ''),
                   ('openid', '')]
        )
        if not parse_args.get('unionid') and not parse_args.get('openid'):
            raise tornado.web.HTTPError(400)

        req_data = dtools.transfer(
            parse_args,
            copys=['appid',
                   'out_trade_no',
                   'detail',
                   'total_fee',
                   'spbill_create_ip',
                   'trade_type',
                   'openid'],
            renames=[('title', 'body')]
        )
        if not req_data.get('openid'):
            # search from db
            req_data['openid'] = self.storage.get_user_info(appid=parse_args['appid'],
                                                            unionid=parse_args['unionid'],
                                                            select_key='openid')
        appinfo = self.storage.get_app_info(appid=req_data['appid'])
        if not appinfo:
            self.send_response(err_code=3201)
            raise tornado.gen.Return()

        req_data.update(
            {
                'attach': 'siteid=' + siteid,
                'mch_id': appinfo.get('mch_id'),
                'nonce_str': security.nonce_str(),
                'notify_url': self.storage.get_site_info(siteid, select_key='pay_notify_url'),
            }
        )
        req_key = appinfo['apikey']
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(url=url.mch_order_add, data=req_data, data_type='xml')
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            raise tornado.gen.Return()

        resp_data = self.parse_payment_resp(resp, req_key)
        if resp_data:
            real_sign_data = {
                'appId': resp_data['appid'],
                'timeStamp': str(int(time.time())),
                'nonceStr': security.nonce_str(),
                'package': 'prepay_id=' + resp_data['prepay_id'],
                'signType': 'MD5'
            }
            post_resp_data = {
                'appid': real_sign_data['appId'],
                'timestamp': real_sign_data['timeStamp'],
                'noncestr': real_sign_data['nonceStr'],
                'prepay_id': resp_data['prepay_id'],
                'sign_type': real_sign_data['signType'],
                'pay_sign': security.build_sign(real_sign_data, req_key)
            }
            self.send_response(post_resp_data)


class OrderHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def get(self, siteid, out_trade_no, *args, **kwargs):
        appid = self.get_argument('appid')
        appinfo = self.storage.get_app_info(appid=appid)
        if not appinfo:
            self.send_response(err_code=3201)
            raise tornado.gen.Return()

        req_data = {
            'appid': appid,
            'mch_id': appinfo.get('mch_id'),
            'transaction_id': '',
            'out_trade_no': out_trade_no,
            'nonce_str': security.nonce_str(),
        }
        req_key = appinfo['apikey']
        req_data['sign'] = security.build_sign(req_data, req_key)

        try:
            resp = yield ahttp.post_dict(url=url.mch_order_query, data=req_data, data_type='xml')
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
                    'time_end'
                ]
            )
            self.send_response(post_resp_data)
