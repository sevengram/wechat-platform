# -*- coding: utf-8 -*-

import tornado.gen
import tornado.httpclient

from handler.base import BaseHandler


class MeduoUserHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        appid = self.get_argument('appid')
        code = self.get_argument('code')
        channel = self.get_argument('channel')
