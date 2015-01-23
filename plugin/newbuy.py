# -*- coding: utf-8 -*-

import hashlib

import tornado.gen
import tornado.web

from handler.base import BaseHandler


def get_coupon(openid):
    return hashlib.md5(openid).hexdigest()[:6]


class NewbuyHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        msg_type = self.get_argument('msg_type', '')
        event_type = self.get_argument('event_type', '')
        post_resp_data = {
            'appid': self.get_argument('appid'),
            'to_openid': self.get_argument('from_openid'),
            'from_openid': self.get_argument('to_openid'),
        }
        if msg_type == 'event' and event_type == 'subscribe':
            post_resp_data.update({
                'msg_type': 'text',
                'content': u'您好, 欢迎关注向星-牛掰, 您的优惠码是:' + get_coupon(self.get_argument('to_openid'))
            })
            self.send_response(post_resp_data)
        else:
            post_resp_data.update({
                'msg_type': 'text',
                'content': u'您好, 感谢您关注向星牛掰, 成为光荣de"牛粪"-牛掰粉儿!'
            })
            self.send_response(post_resp_data)