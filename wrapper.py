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
        utime = str(self.appinfo['utime'])
        if mch_id and apikey:
            return security.decrypt(apikey, mch_id, utime)
        else:
            return ''

    def get_secret(self):
        appid = self.appinfo.get('appid', '')
        secret = self.appinfo.get('secret', '')
        utime = str(self.appinfo['utime'])
        if appid and secret:
            return security.decrypt(secret, appid, utime)
        else:
            return ''


class Siteinfo(object):
    def __init__(self, site_info):
        self.site_info = site_info

    def get(self, key):
        return self.site_info.get(key)

    def get_sitekey(self):
        if not self.site_info:
            return ''
        siteid = self.site_info.get('siteid', '')
        sitekey = self.site_info.get('sitekey', '')
        utime = str(self.site_info['utime'])
        if siteid and sitekey:
            return security.decrypt(sitekey, siteid, utime)
        else:
            return ''
