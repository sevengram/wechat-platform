# -*- coding: utf-8 -*-

from util import security


class Appinfo(object):
    def __init__(self, appinfo):
        self.appinfo = appinfo

    def get(self, key):
        return self.appinfo.get(key)

    def get_apikey(self):
        if not self.appinfo:
            return ''
        mch_id = self.appinfo.get('mch_id', '')
        apikey = self.appinfo.get('apikey', '')
        utime = self.appinfo['utime']
        if mch_id and apikey:
            return security.decrypt(apikey, mch_id, utime)
        else:
            return ''

    def get_secret(self):
        appid = self.appinfo.get('appid', '')
        secret = self.appinfo.get('secret', '')
        utime = self.appinfo['utime']
        if appid and secret:
            return security.decrypt(secret, appid, utime)
        else:
            return ''