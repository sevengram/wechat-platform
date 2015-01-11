# -*- coding:utf8 -*-
import time

import tornado.web
import tornado.gen
import tornado.httpclient

from util import dtools
from util import security
from consts import url
from consts import err_code as err
from consts.key import newbuy_apikey
from handler.site import SiteHandler


class OrderHandler(SiteHandler):
    @tornado.gen.coroutine
    def get(self, prepay_id, *args, **kwargs):
        self.write(prepay_id)
        self.finish()


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
        data = dtools.transfer(
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
        data.update(
            {
                'mch_id': '10010984',  # TODO: from db
                'nonce_str': security.nonce_str(),
                'openid': 'oIvjEs_zh_VFqnFfiXkXBUyxsdMY',  # TODO: search by unionId from db
                'notify_url': 'http://uri/notify/payment/',  # TODO
            }
        )
        resp_key = newbuy_apikey  # TODO from db
        data['sign'] = security.build_signature(data, resp_key)
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
                if security.check_signature(resp_data, resp_key):
                    if resp_data['result_code'].lower() == 'success':
                        post_resp_data = {
                            'appid': resp_data['appid'],
                            'timestamp': str(int(time.time())),
                            'noncestr': security.nonce_str(),
                            'prepay_id': resp_data['prepay_id'],
                            'sign_type': 'MD5'
                        }
                        post_resp_data['sign'] = security.build_signature(post_resp_data, resp_key)
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
