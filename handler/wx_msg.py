# -*- coding:utf8 -*-

import json
import time

import tornado.gen
import tornado.httpclient

import wxclient
from util import http, security, dtools
from util.web import BaseHandler
from wxstorage import wechat_storage


def build_response(from_id, to_id, data):
    if not data:
        return None
    msg_type = data['msg_type']
    result = {
        'FromUserName': from_id,
        'ToUserName': to_id,
        'MsgType': msg_type,
        'Tag': data.get('tag', '')
    }
    if msg_type == 'text':
        result.update({
            'Content': data['content'],
            'CreateTime': int(time.time())
        })
    elif msg_type == 'news':
        result.update({
            'ArticleCount': len(data['articles']),
            'Articles': {
                'item': []
            },
            'CreateTime': int(time.time())
        })
        for article in data['articles']:
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
    def initialize(self, sign_check=True):
        super(WechatMsgHandler, self).initialize(sign_check=sign_check)
        self.storage = wechat_storage
        self.post_args = {}

    @tornado.gen.coroutine
    def prepare(self):
        if self.sign_check:
            self.check_signature({k: v[0] for k, v in self.request.arguments.iteritems() if v},
                                 sign_key='wechat_platform',
                                 method='sha1')

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
                ('MsgId', 'msg_id'),
                ('CreateTime', 'msg_time'),
                ('Content', 'content'),
                ('Event', 'event_type'),
                ('PicUrl', 'pic_url'),
                ('Location_X', 'latitude'),
                ('Location_Y', 'longitude'),
                ('Label', 'label'),
                ('MediaId', 'media_id')],
            allow_empty=False
        )
        appinfo = self.storage.get_app_info(openid=self.post_args['ToUserName'])
        appid = appinfo['appid']
        req_data['appid'] = appid
        site_info = self.storage.get_site_info(appinfo['siteid'])
        security.add_sign(req_data, site_info['sitekey'])
        try:
            contact_resp = yield http.post_dict(
                url=site_info['msg_notify_url'],
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()
        if contact_resp.code != 200:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()

        try:
            resp_data = json.loads(contact_resp.body)
            if resp_data.get('err_code', 1) == 0:
                self.send_response(build_response(from_id=self.post_args['ToUserName'],
                                                  to_id=self.post_args['FromUserName'],
                                                  data=resp_data.get('data')))
            else:
                self.send_response(err_code=9003)
        except ValueError:
            self.send_response(err_code=9101)

        # Add basic user info
        openid = req_data['openid']
        user_info = self.storage.get_user_info(appid=appid, openid=openid)
        if not user_info:
            if appinfo['is_verified']:
                yield wxclient.update_user_info(appid, openid)
            else:
                self.storage.add_user_info({
                    'appid': appid,
                    'openid': openid
                })

        # Add more user info
        if not user_info or not user_info.get('fakeid'):
            user_resp = yield wxclient.mock_browser.find_user(
                appid=appid,
                timestamp=long(req_data['msg_time']),
                content=req_data['content'],
                mtype=req_data['msg_type'])
            if user_resp['err_code'] == 0:
                more_info = {
                    'appid': appid,
                    'openid': openid,
                    'fakeid': user_resp['data']['fakeid'],
                    'nickname': user_resp['data']['nick_name']
                }
                if not appinfo['is_verified']:
                    contact_resp = yield wxclient.mock_browser.get_contact_info(
                        appid=appid,
                        fakeid=user_resp['data']['fakeid'],
                        msg_id=user_resp['data']['id']
                    )
                    contact_info = contact_resp['data']['contact_info']
                    more_info.update({
                        'sex': contact_info['gender'],
                        'city': contact_info['city'],
                        'province': contact_info['province'],
                        'country': contact_info['country']
                    })
                self.storage.add_user_info(more_info)

    def send_response(self, data=None, err_code=0, err_msg=''):
        if data:
            self.write(dtools.dict2xml(data))
        self.finish()
