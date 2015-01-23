# -*- coding:utf8 -*-

import time
import hashlib
import sys

import tornado.web
import tornado.gen
import tornado.httpclient

from util import async_http as ahttp
from handler.base import BaseHandler
from consts.key import magento_sitekey
from util import security
from util import dtools


# TODO: should remove
def get_coupon(openid):
    return hashlib.md5(openid).hexdigest()[:8]


class WechatMsgHandler(BaseHandler):
    @tornado.gen.coroutine
    def prepare(self):
        if self.sign_check:
            self.check_signature({k: v[0] for k, v in self.request.arguments.iteritems() if v}, method='sha1')

    @tornado.gen.coroutine
    def get(self):
        self.write(self.get_argument('echostr', 'get ok'))
        self.finish()

    @tornado.gen.coroutine
    def post(self):
        self.post_args = dtools.xml2dict(self.request.body)
        req_data = dtools.transfer(
            self.post_args,
            renames=[
                ('FromUserName', 'openid'),
                ('MsgType', 'msg_type'),
                ('Content', 'content'),
                ('MsgId', 'msg_id')]
        )
        appinfo = self.storage.get_app_info(openid=self.post_args['ToUserName'])
        appid = appinfo['appid']
        req_data.update(
            {
                'appid': appid,
                'openid': req_data['openid'],
                'unionid': self.storage.get_user_info(appid=appid,
                                                      openid=req_data['openid'],
                                                      select_key='unionid') or '',
                'nonce_str': security.nonce_str()
            }
        )
        site_info = self.storage.get_site_info(appinfo['siteid'])
        req_key = site_info['sitekey']
        req_data['sign'] = security.build_sign(req_data, req_key)
        try:
            resp = yield ahttp.post_dict(
                url=site_info['msg_notify_url'],
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            return
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
                'FromUserName': self.post_args['ToUserName']
            }
        )
        self.send_response(post_resp_data)

    def get_check_key(self, refer_dict):
        return 'wechat_platform'

    def send_response(self, data=None, err_code=0, err_msg=''):
        self.write(dtools.dict2xml(data))
        self.finish()
