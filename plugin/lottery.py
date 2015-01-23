# -*- coding: utf-8 -*-

import sys

import tornado.gen
import tornado.web


class LotteryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print(self.request.body)
        sys.stdout.flush()
        self.write('ok')
        self.finish()
