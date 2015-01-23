# -*- coding: utf-8 -*-

import tornado.gen
import tornado.web


class NewbuyHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        pass