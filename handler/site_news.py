# -*- coding: utf-8 -*-

import tornado.gen

from handler.site_base import SiteBaseHandler


class NewsHandler(SiteBaseHandler):
    @tornado.gen.coroutine
    def post(self, siteid, *args, **kwargs):
        pass