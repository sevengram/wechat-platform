# -*- coding:utf8 -*-

import time
import hashlib

import pyexpat
import tornado.web
import tornado.gen
import tornado.httpclient

from handler.common import CommonHandler
from consts.key import magento_sitekey
from util import security
from util import dtools


# TODO: should remove
def get_coupon(openid):
    return hashlib.md5(openid).hexdigest()[:8]


class WechatMsgHandler(CommonHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write(self.get_argument('echostr', 'get ok'))
        self.finish()

    @tornado.gen.coroutine
    def post(self):
        try:
            post_args = dtools.xml2dict(self.request.body)
        except pyexpat.ExpatError:
            raise tornado.web.HTTPError(400)
        req_data = dtools.transfer(
            post_args,
            renames=[
                ('FromUserName', 'openid'),
                ('MsgType', 'msg_type'),
                ('Content', 'content'),
                ('MsgId', 'msg_id')]
        )
        req_data.update(
            {
                'appid': self.storage.get_app_info(openid=post_args['ToUserName'], select_key='appid'),
                'unionid': req_data['openid'],  # TODO: from db
                'nonce_str': security.nonce_str()
            }
        )
        req_key = magento_sitekey  # TODO from db
        req_data['sign'] = security.build_sign(req_data, req_key)

        # try:
        #     resp = yield ahttp.post_dict(
        #         url='http://msg_notify_url',
        #         data=req_data)
        # except tornado.httpclient.HTTPError:
        #     self.send_response(err_code=9002)
        #     return
        # if resp.code == 200:
        #     resp_data = json.loads(resp.body)
        #     self.send_response(err_code=err.alias_map.get(resp_data.get('return_code'), 9001))
        # else:
        #     self.send_response(err_code=9002)
        # TODO: test data
        resp_data = {
            'appid': 'wx7394ce44a23b3225',
            'openid': req_data['openid'],
            'msg_type': 'text',
            'content': get_coupon(req_data['openid'])  # TODO: from upstream
        }
        post_resp_data = dtools.transfer(
            resp_data,
            renames=[
                ('openid', 'ToUserName'),
                ('msg_type', 'MsgType'),
                ('content', 'Content')]
        )
        post_resp_data.update(
            {
                'CreateTime': int(time.time()),
                'FromUserName': post_args['ToUserName']
            }
        )
        self.send_response(post_resp_data)

    def check_signature(self, refer_dict, method='sha1'):
        super(WechatMsgHandler, self).check_signature(refer_dict, method)

    def get_check_key(self, refer_dict):
        return 'ilovedeepsky'

    def send_response(self, data):
        self.write(dtools.dict2xml(data))
        self.finish()
