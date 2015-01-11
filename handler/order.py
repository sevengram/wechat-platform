# -*- coding:utf8 -*-
import time

import tornado.gen
import tornado.httpclient

from util import dtools
from util import security
from util import async_http as ahttp
from consts import url
from consts import err_code as err
from consts.key import newbuy_apikey
from handler.site import SiteHandler


class OrderHandler(SiteHandler):
    @tornado.gen.coroutine
    def get(self, prepay_id, *args, **kwargs):
        req_data = {
            'appid': self.get_argument('appid'),
            'mch_id': '10010984',  # TODO: from db
            'transaction_id': '013467007045764',  # TODO: from db
            'out_trade_no': '1217752501201407033233368018',  # TODO: from db
            'nonce_str': security.nonce_str(),
        }
        req_key = newbuy_apikey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)
        try:
            resp = yield ahttp.post_dict(url=url.order_query, data=req_data, data_type='xml')
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            return
        if resp.code == 200:
            resp_data = dtools.xml2dict(resp.body)
            if resp_data['return_code'].lower() == 'success':
                if security.check_sign(resp_data, req_key):
                    if resp_data['result_code'].lower() == 'success':
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
                    else:
                        self.send_response(err_code=err.alias_map.get(resp_data.get('err_code'), 9001),
                                           err_msg=resp_data.get('err_code_des'))
                else:
                    self.send_response(err_code=1002)
            else:
                self.send_response(err_code=1001, err_msg=resp_data.get('return_msg'))
        else:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)


class PrepayHandler(SiteHandler):
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        parse_args = self.assign_arguments(
            essential=['appid',
                       'title',
                       'out_trade_no',
                       'total_fee',
                       'spbill_create_ip',
                       'trade_type',
                       'site_notify_url',
                       'unionid',
                       #'siteid',
                       'nonce_str',
                       'sign'],
            extra=[('detail', ''),
                   ('goods_tag', '')]
        )
        req_data = dtools.transfer(
            parse_args,
            copys=['appid',
                   'out_trade_no',
                   'total_fee',
                   'spbill_create_ip',
                   'trade_type',
                   'detail',
                   'goods_tag',
                   'attach'],
            renames=[('title', 'body')]
        )
        req_data.update(
            {
                'mch_id': '10010984',  # TODO: from db
                'nonce_str': security.nonce_str(),
                'openid': 'oIvjEs_zh_VFqnFfiXkXBUyxsdMY',  # TODO: search by unionId from db
                'notify_url': 'http://uri/notify/payment/',  # TODO
            }
        )
        req_key = newbuy_apikey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)
        try:
            resp = yield ahttp.post_dict(url=url.order_add, data=req_data, data_type='xml')
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            return
        if resp.code == 200:
            resp_data = dtools.xml2dict(resp.body)
            if resp_data['return_code'].lower() == 'success':
                if security.check_sign(resp_data, req_key):
                    if resp_data['result_code'].lower() == 'success':
                        post_resp_data = {
                            'appid': resp_data['appid'],
                            'timestamp': str(int(time.time())),
                            'noncestr': security.nonce_str(),
                            'prepay_id': resp_data['prepay_id'],
                            'sign_type': 'MD5'
                        }
                        post_resp_data['pay_sign'] = security.build_sign(post_resp_data, req_key)
                        self.send_response(post_resp_data)
                    else:
                        self.send_response(err_code=err.alias_map.get(resp_data.get('err_code'), 9001),
                                           err_msg=resp_data.get('err_code_des'))
                else:
                    self.send_response(err_code=1002)
            else:
                self.send_response(err_code=1001, err_msg=resp_data.get('return_msg'))
        else:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)
