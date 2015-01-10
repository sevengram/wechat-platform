#! /usr/bin/env python2
# -*- coding:utf8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from consts.key import newbuy_apikey, magento_sitekey

from handler.order import OrderHandler
from handler.wechat.message import WechatMsgHandler
from handler.wechat.payment import WechatPayHandler


define("port", default=33600, help="run on the given port", type=int)

application = tornado.web.Application(
    handlers=[
        (r'/notify/messages', WechatMsgHandler),
        (r'/notify/payment', WechatPayHandler, dict(sign_check=False, sign_key=newbuy_apikey)),
        (r'/site/orders', OrderHandler, dict(sign_check=False, sign_key=magento_sitekey))
    ], debug=True
)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
