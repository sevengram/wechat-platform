#! /usr/bin/env python2
# -*- coding:utf8 -*-

import logging

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

define('port', default=33600, help="run on the given port", type=int)
define('env', default='dev', help="run on the given environment", type=str)
define('conf', default='config', help="config file dir", type=str)

tornado.options.parse_command_line()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

from handler import site_order, site_user, site_news, site_msgs
from handler.wx_msg import WechatMsgHandler
from handler.wx_pay import WechatPayHandler

if __name__ == '__main__':
    debug = options.env == 'dev'
    param = {'sign_check': not debug}
    application = tornado.web.Application(
        handlers=[
            (r'/notify/messages', WechatMsgHandler, param),
            (r'/notify/payment', WechatPayHandler, param),
            (r'/sites/(\w+)/news', site_news.NewsHandler, param),
            (r'/sites/(\w+)/users', site_user.UserHandler, param),
            (r'/sites/(\w+)/users/(\w+)', site_user.UserHandler, param),
            (r'/sites/(\w+)/orders', site_order.OrderHandler, param),
            (r'/sites/(\w+)/orders/(\w+)', site_order.OrderHandler, param),
            (r'/sites/(\w+)/msgs', site_msgs.MsgsHandler, param),
            (r'/sites/(\w+)/multimsgs', site_msgs.MultiMsgsHandler, param)
        ], debug=debug
    )
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
