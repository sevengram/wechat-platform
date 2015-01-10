# -*- coding:utf8 -*-
import time

import tornado.web
import tornado.gen
import tornado.httpclient

from util import security
from util import dtools
from base import BaseHandler
from consts import url
from consts import err_code as err
from consts.key import newbuy_apikey


class OrderHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        if (yield super(OrderHandler, self).post()):
            # Finish in super
            return
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
        data = dtools.transfer(
            parse_args,
            copys=['appid',
                   'out_trade_no',
                   'total_fee',
                   'spbill_create_ip',
                   'trade_type',
                   'detail',
                   'goods_tag'],
            renames=[('title', 'body')]
        )
        data.update(
            {
                'mch_id': '10010984',  # TODO: from db
                'nonce_str': security.nonce_str(),
                'openid': 'oIvjEs_zh_VFqnFfiXkXBUyxsdMY',  # TODO: search by unionId from db
                'notify_url': 'http://uri/notify/payment/',  # TODO
                'attach': '',  # TODO
            }
        )
        data['sign'] = security.build_signature(data, newbuy_apikey)
        client = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(
            url=url.unified_order,
            method='POST',
            body=dtools.dict2xml(data)
        )
        try:
            resp = yield client.fetch(req)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=1001)
            return
        if resp.code == 200:
            resp_data = dtools.xml2dict(resp.body)
            if resp_data['return_code'].lower() == 'success':
                if security.check_signature(resp_data, newbuy_apikey):
                    if resp_data['result_code'].lower() == 'success':
                        post_resp_data = {
                            'appId': resp_data['appid'],
                            'timeStamp': str(int(time.time())),
                            'nonceStr': security.nonce_str(),
                            'package': 'prepay_id=' + resp_data['prepay_id'],
                            'signType': 'MD5'
                        }
                        post_resp_data['sign'] = security.build_signature(post_resp_data, newbuy_apikey)
                        self.send_response(post_resp_data)
                    else:
                        self.send_response(err_code=err.alias_map.get(resp_data.get('err_code'), 9001),
                                           err_msg=resp_data.get('err_code_des'))
                else:
                    self.send_response(err_code=1002)
            else:
                self.send_response(err_code=1001, err_msg=resp_data['return_msg'])
        else:
            self.send_response(err_code=1001, err_msg='wechat %d' % resp.code)

