# -*- coding: utf-8 -*-

import tornado.gen
import tornado.ioloop
import tornado.options
from tornado.options import define

define('env', default='dev', help="run on the given environment", type=str)
define('conf', default='config', help="config file dir", type=str)

tornado.options.parse_command_line()

from wxclient import create_menu


@tornado.gen.engine
def foo():
    result = yield create_menu('wxebaa11f9ddee1dc2', {
        "button": [
            {
                "type": "click",
                "name": "用户注册",
                "key": "REGISTER"
            },
            {
                "type": "click",
                "name": "用户注册",
                "key": "REGISTER2"
            }
        ]
    })
    print(result)
    print(result['err_msg'])


if __name__ == "__main__":
    foo()
    tornado.ioloop.IOLoop.instance().start()
