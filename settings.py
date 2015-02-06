# -*- coding: utf-8 -*-

import ConfigParser

__url_parser = ConfigParser.ConfigParser()
__url_parser.read('conf/url.conf')

__db_parser = ConfigParser.ConfigParser()
__db_parser.read('conf/database.conf')


def mch_url(item):
    return __url_parser.get('mch', item)


def wechat_url(item):
    return __url_parser.get('wechat', item)


def db_name(environment):
    return __db_parser.get(environment, 'db_name')


def db_host(environment):
    return __db_parser.get(environment, 'db_host')


def db_user(environment):
    return __db_parser.get(environment, 'db_user')


def db_pwd(environment):
    return __db_parser.get(environment, 'db_pwd')