# -*- coding: utf-8 -*-

import ConfigParser
import sys

__url_parser = ConfigParser.ConfigParser()
__url_parser.read('/home/wechat/service/config/url.conf')

__db_parser = ConfigParser.ConfigParser()
__db_parser.read('/home/wechat/service/config/database.conf')

mch_url = dict(__url_parser.items('mch'))

wechat_url = dict(__url_parser.items('wechat'))


def db_conf(env):
    print env
    sys.stdout.flush()
    return dict(__db_parser.items(env))
