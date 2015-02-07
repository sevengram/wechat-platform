# -*- coding:utf8 -*-

import json
import time

import tornado.gen
import tornado.httpclient

from util import http
from util import security
from util import dtools
from util.web import BaseHandler
from wxstorage import wechat_storage


def transfer_response(src):
    if not src:
        return None
    result = dtools.transfer(
        src,
        renames=[
            ('to_openid', 'ToUserName'),
            ('from_openid', 'FromUserName'),
            ('msg_type', 'MsgType'),
        ]
    )
    msg_type = src['msg_type']
    if msg_type == 'text':
        result.update({
            'Content': src['content'],
            'CreateTime': int(time.time())
        })
    elif msg_type == 'news':
        result.update({
            'ArticleCount': len(src['articles']),
            'Articles': {
                'item': []
            },
            'CreateTime': int(time.time())
        })
        for article in src['articles']:
            item = dtools.transfer(
                article,
                renames=[
                    ('title', 'Title'),
                    ('description', 'Description'),
                    ('picurl', 'PicUrl'),
                    ('url', 'Url')
                ])
            result['Articles']['item'].append(item)
    return result


class WechatMsgHandler(BaseHandler):
    def initialize(self, sign_check=False):
        super(WechatMsgHandler, self).initialize(sign_check=sign_check)
        self.storage = wechat_storage
        self.post_args = {}

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
                ('FromUserName', 'from_openid'),
                ('ToUserName', 'to_openid'),
                ('MsgType', 'msg_type'),
                ('Content', 'content'),
                ('MsgId', 'msg_id'),
                ('CreateTime', 'msg_time'),
                ('Event', 'event_type')]
        )
        appinfo = self.storage.get_app_info(openid=self.post_args['ToUserName'])
        req_data['appid'] = appinfo['appid']
        site_info = self.storage.get_site_info(appinfo['siteid'])
        req_key = site_info['sitekey']
        security.add_sign(req_data, req_key)

        try:
            resp = yield http.post_dict(
                url=site_info['msg_notify_url'],
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()

        if resp.code != 200:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()

        try:
            resp_data = json.loads(resp.body)
            if resp_data.get('err_code', 1) == 0:
                self.send_response(transfer_response(resp_data.get('data')))
            else:
                self.send_response(err_code=9003)
        except ValueError:
            self.send_response(err_code=9101)

    def get_check_key(self, refer_dict):
        return 'wechat_platform'

    def send_response(self, data=None, err_code=0, err_msg=''):
        if data:
            self.write(dtools.dict2xml(data))
        self.finish()
