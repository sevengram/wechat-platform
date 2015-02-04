# -*- coding: utf-8 -*-

import json

import tornado.gen
import tornado.httpclient

from util import security
from util import dtools
from util import async_http as ahttp
from handler.base import BaseHandler
from util.storage import Storage

meduo_key = 'ecf42d7f40480dffd3b9cc8f911552c9'


class MeduoStorage(Storage):
    def __init__(self, host, user, passwd):
        super(MeduoStorage, self).__init__('meduo_service', host, user, passwd)

    def add_user_info(self, user, noninsert=None):
        self.replace('meduo_user_info', user,
                     noninsert=noninsert)


meduo_storage = MeduoStorage(host='127.0.0.1',
                             user='root',
                             passwd='eboue')


class MeduoUserHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        req_data = {
            'appid': self.get_argument('appid'),
            'code': self.get_argument('code'),
        }
        security.add_sign(req_data, meduo_key)

        try:
            # TODO: change url
            resp = yield ahttp.post_dict(
                url='http://wechat_platform/sites/meduo/users',
                data=req_data)
        except tornado.httpclient.HTTPError:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()
        if resp.code != 200:
            self.send_response(err_code=9002)
            raise tornado.gen.Return()

        resp_data = json.loads(resp.body)
        if resp_data['err_code'] != 0:
            self.send_response(err_code=resp_data['err_code'])
            raise tornado.gen.Return()
        save_data = dtools.transfer(src=resp_data['data'], copys=[
            'appid',
            'openid',
            'nickname',
            'sex',
            'city',
            'province',
            'country'
        ])
        save_data['phone'] = self.get_argument('phone', '')
        save_data['channel'] = self.get_argument('channel', '')
        meduo_storage.add_user_info(save_data, noninsert=['code'])


class MeduoMsgHandler(BaseHandler):
    @tornado.gen.coroutine
    def process_subscribe(self):
        self.post_resp_data.update({
            'msg_type': 'text',
            'content': 'hello'  # TODO: define message
        })
        self.send_response(self.post_resp_data)

        req_data = {
            'appid': self.get_argument('appid'),
        }
        security.add_sign(req_data, meduo_key)

        # get use info
        try:
            # TODO: change url
            resp = yield ahttp.get_dict(
                url='http://wechat_platform/sites/meduo/users/%s' % self.get_argument('from_openid'),
                data=req_data)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return()
        if resp.code != 200:
            raise tornado.gen.Return()

        resp_data = json.loads(resp.body)
        if resp_data['err_code'] != 0:
            raise tornado.gen.Return()
        save_data = dtools.transfer(src=resp_data['data'], copys=[
            'appid',
            'openid',
            'nickname',
            'sex',
            'city',
            'province',
            'country'
        ])
        meduo_storage.add_user_info(save_data)

    @tornado.gen.coroutine
    def post(self):
        msg_type = self.get_argument('msg_type', '')
        event_type = self.get_argument('event_type', '')
        self.post_resp_data = {
            'appid': self.get_argument('appid'),
            'to_openid': self.get_argument('from_openid'),
            'from_openid': self.get_argument('to_openid'),
        }
        if msg_type == 'event' and event_type == 'subscribe':
            yield self.process_subscribe()
