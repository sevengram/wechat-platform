# -*- coding: utf-8 -*-

import ConfigParser

from tornado.options import options


__url_parser = ConfigParser.ConfigParser()
__url_parser.read(options.conf + '/url.conf')

__db_parser = ConfigParser.ConfigParser()
__db_parser.read(options.conf + '/database.conf')

mch_url = dict(__url_parser.items('mch'))

wechat_url = dict(__url_parser.items('wechat'))

db_conf = dict(__db_parser.items(options.env))
