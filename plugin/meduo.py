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

    def get_user_info(self, appid='', openid='', uid='', select_key='*'):
        return self.get('meduo_user_info',
                        {'appid': appid, 'openid': openid, 'uid': uid},
                        select_key=select_key)


# TODO: local test db
meduo_storage = MeduoStorage(host='eridanus.mysql.rds.aliyuncs.com',
                             user='meduo_admin',
                             passwd='Meaeboue123')


class MeduoUserHandler(BaseHandler):
    @tornado.gen.coroutine
    def put(self, uid, *args, **kwargs):
        post_args = self.assign_arguments(
            essential=['']
        )

        appid = self.get_argument('appid')
        openid = self.get_argument('openid')

        # Check user
        if not meduo_storage.get_user_info(openid=openid, appid=appid, uid=uid):
            pass
        else:
            self.send_response(err_code=2002)


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
        save_data['channel'] = self.get_argument('channel', '')
        meduo_storage.add_user_info(save_data, noninsert=['code'])
        post_resp_data = dtools.filter_data(
            meduo_storage.get_user_info(appid=save_data['appid'], uid=save_data['openid']),
            nonblank=True,
            delkeys=['password'])
        self.send_response(post_resp_data)


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

        # Get user info
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
