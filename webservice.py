#! /usr/bin/env python2
# -*- coding:utf8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from handler import site_order
from handler import site_user
from handler.wx_msg import WechatMsgHandler
from handler.wx_pay import WechatPayHandler
from plugin.meduo import MeduoUserHandler
from plugin.lottery import LotteryHandler
from plugin.newbuy import NewbuyHandler


define("port", default=33600, help="run on the given port", type=int)

application = tornado.web.Application(
    handlers=[
        (r'/notify/messages', WechatMsgHandler, dict(sign_check=True)),
        (r'/notify/payment', WechatPayHandler, dict(sign_check=True)),
        (r'/sites/(\w+)/users', site_user.UserHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/users/(\w+)', site_user.UserHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/orders', site_order.OrderHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/orders/(\w+)', site_order.OrderHandler, dict(sign_check=False)),
        (r'/plugin/newbuy', NewbuyHandler),
        (r'/plugin/lottery', LotteryHandler),
        (r'/plugin/meduo/users', MeduoUserHandler)
    ], debug=True
)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
