# -*- coding: utf-8 -*-

import time
import ConfigParser

from tornado.options import options

from util import sqldb


class WechatStorage(sqldb.Sqldb):
    def __init__(self, db_name, db_host, db_user, db_pwd):
        super(WechatStorage, self).__init__(db_name, db_host, db_user, db_pwd)

    def add_user_info(self, user):
        self.replace('wechat_user_info', user)

    def add_access_token(self, pid, appid, access_token, expires_in):
        self.replace('wechat_app_token', {
            'id': pid,
            'appid': appid,
            'access_token': access_token,
            'expires_in': expires_in,
            'access_token_utime': int(time.time())
        })

    def get_access_token(self, appid):
        token_info = self.get('wechat_app_token', {'appid': appid})
        if token_info:
            if int(time.time()) - token_info['access_token_utime'] < token_info['expires_in']:
                return token_info['access_token']
            else:
                return ''
        else:
            return ''

    def get_app_info(self, appid='', openid='', select_key='*'):
        return self.get('wechat_app_info',
                        {'appid': appid, 'openid': openid},
                        select_key=select_key)

    def get_site_info(self, siteid, select_key='*'):
        return self.get('site_info',
                        {'siteid': siteid},
                        select_key=select_key)

    def get_user_info(self, uid='', appid='', openid='', unionid='', select_key='*'):
        return self.get('wechat_user_info',
                        {'uid': uid, 'appid': appid, 'openid': openid, 'unionid': unionid},
                        select_key=select_key)


__db_parser = ConfigParser.ConfigParser()
__db_parser.read(options.conf + '/db.conf')

wechat_storage = WechatStorage(**dict(__db_parser.items(options.env)))
