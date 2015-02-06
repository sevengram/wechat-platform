# -*- coding: utf-8 -*-

import time

from util import storage


class WechatStorage(storage.Storage):
    def __init__(self, host, user, passwd):
        super(WechatStorage, self).__init__('wechat_platform', host, user, passwd)

    def add_user_info(self, user, noninsert=None):
        self.replace('wechat_user_info', user,
                     noninsert=noninsert)

    def add_access_token(self, appid, access_token, expires_in):
        self.replace('wechat_app_token', {
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
                        {'openid': openid, 'appid': appid},
                        select_key=select_key)

    def get_site_info(self, siteid, select_key='*'):
        return self.get('site_info',
                        {'siteid': siteid},
                        select_key=select_key)

    def get_user_info(self, appid, openid='', unionid='', select_key='*'):
        return self.get('wechat_user_info',
                        {'appid': appid, 'openid': openid, 'unionid': unionid},
                        select_key=select_key)

#
# wechat_storage = WechatStorage(host='newbuy01.mysql.rds.aliyuncs.com',
#                                user='wechat_admin',
#                                passwd='_WecAd456')

# wechat_storage = WechatStorage(host='127.0.0.1',
#                                user='root',
#                                passwd='eboue')

wechat_storage = WechatStorage(host='eridanus.mysql.rds.aliyuncs.com',
                               user='wechat_admin',
                               passwd='Waeboue123')