#! /usr/bin/env python2
# -*- coding:utf8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

define('port', default=33600, help="run on the given port", type=int)
define('env', default='dev', help="run on the given environment", type=str)
define('conf', default='config', help="config file dir", type=str)

tornado.options.parse_command_line()

from handler import site_order, site_user, site_news
from handler.wx_msg import WechatMsgHandler
from handler.wx_pay import WechatPayHandler


application = tornado.web.Application(
    handlers=[
        (r'/notify/messages', WechatMsgHandler, dict(sign_check=True)),
        (r'/notify/payment', WechatPayHandler, dict(sign_check=True)),
        (r'/sites/(\w+)/news', site_news.NewsHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/users', site_user.UserHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/users/(\w+)', site_user.UserHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/orders', site_order.OrderHandler, dict(sign_check=False)),
        (r'/sites/(\w+)/orders/(\w+)', site_order.OrderHandler, dict(sign_check=False))
    ], debug=True
)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
