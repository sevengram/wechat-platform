# -*- coding: utf-8 -*-

import tornado.gen

from handler.wechat.common import WechatCommonHandler


class WechatPayHandler(WechatCommonHandler):
    @tornado.gen.coroutine
    def post(self):
        if (yield super(WechatPayHandler, self).post()):
            # Finish in super
            return
        print 'out'