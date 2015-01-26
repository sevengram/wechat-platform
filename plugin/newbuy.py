# -*- coding: utf-8 -*-

import hashlib

import tornado.gen

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
                'content': u'亲, 你总算来了! 0元领29元极小分子玻尿酸面膜白+黑2片装. 白天敷白片, 不干燥; 晚上敷黑片, 睡得香! '
                           u'点击菜单"粉丝福利-面膜0元领", 下单输入优惠码"%s"即可!' % get_coupon(self.get_argument('to_openid'))
            })
            self.send_response(post_resp_data)
        else:
            post_resp_data.update({
                'msg_type': 'text',
                'content': u'感谢您关注向星牛掰, 成为光荣de"牛粪"-牛掰粉儿!'
            })
            self.send_response(post_resp_data)