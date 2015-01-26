# -*- coding: utf-8 -*-

import tornado.gen

from handler.base import BaseHandler


class LotteryHandler(BaseHandler):
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
                'content': u'您好, 欢迎关注彩象彩票!'
            })
            self.send_response(post_resp_data)
        else:
            post_resp_data.update({
                'msg_type': 'text',
                'content': u'您好, 感谢您关注彩象彩票!'
            })
            self.send_response(post_resp_data)
