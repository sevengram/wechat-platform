# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
from redisco import containers as redis

from util import dtools


class Storage(object):
    def __init__(self, dbname, host, user, passwd):
        self.usr = user
        self.pwd = passwd
        self.dbname = dbname
        self.host = host
        self.connect()

    def connect(self):
        self.connection = MySQLdb.connect(
            user=self.usr, passwd=self.pwd, host=self.host, db=self.dbname, charset='utf8')

    def execute(self, query, args, cursorclass=MySQLdb.cursors.DictCursor):
        cursor = self.connection.cursor(cursorclass)
        result = None
        try:
            cursor.execute(query, args)
            result = cursor.fetchone()
        except (AttributeError, MySQLdb.OperationalError):
            self.connection.close()
            self.connect()
            cursor = self.connection.cursor(cursorclass)
            cursor.execute(query, args)
            result = cursor.fetchone()
        finally:
            cursor.close()
            return result

    def get(self, table, queries, select_key='*'):
        queries = {k: v for k, v in queries.iteritems() if v}
        if not queries:
            return None
        redis_key = dtools.get_redis_key(table, queries, queries.keys())
        cache = redis.Hash(redis_key)
        if not len(cache):
            placeholders = ', '.join(map(lambda n: n + ' = %s', queries.keys()))
            request = 'SELECT %s FROM %s WHERE %s' % (select_key, table, placeholders)
            records = self.execute(request, queries.values())
            if records:
                cache.update(records)
        else:
            records = cache.dict
        if not records:
            return None
        else:
            if select_key == '*':
                return {k: v.decode('utf8') if type(v) is str else v for k, v in records.iteritems()}
            else:
                result = records.get(select_key)
                return result.decode('utf8') if type(result) is str else result

    def set(self, table, data, noninsert=None, cache_keys=None):
        if not noninsert:
            noninsert = []
        insert_dict = {k: v for k, v in data.iteritems() if k not in noninsert}
        columns = ', '.join(insert_dict.keys())
        insert_holders = ', '.join(['%s'] * len(insert_dict))
        request = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, insert_holders)
        self.execute(request, insert_dict.values())
        if not cache_keys:
            redis_key = dtools.get_redis_key(table, insert_dict, cache_keys)
            redis.Hash(redis_key).update(insert_dict)

    def replace(self, table, data, noninsert=None, nonupdate=None, cache_keys=None):
        if not nonupdate:
            nonupdate = []
        if not noninsert:
            noninsert = []
        insert_dict = {k: v for k, v in data.iteritems() if k not in noninsert}
        columns = ', '.join(insert_dict.keys())
        insert_holders = ', '.join(['%s'] * len(insert_dict))
        update_dict = {k: v for k, v in insert_dict.iteritems() if k not in nonupdate}
        update_holders = ', '.join(map(lambda n: n + ' = %s', update_dict.keys()))
        request = 'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (
            table, columns, insert_holders, update_holders)
        self.execute(request, insert_dict.values() + update_dict.values())
        if not cache_keys:
            redis_key = dtools.get_redis_key(table, insert_dict, cache_keys)
            redis.Hash(redis_key).update(insert_dict)


class WechatStorage(Storage):
    def __init__(self, host, user, passwd):
        super(WechatStorage, self).__init__('wechat_platform', host, user, passwd)

    def add_user_info(self, user, noninsert=None):
        self.replace('wechat_user_info', user, noninsert=noninsert, nonupdate=['utime'], cache_keys=['appid', 'openid'])

    def get_app_info(self, appid='', openid='', select_key='*'):
        return self.get('wechat_app_info', {'openid': openid, 'appid': appid}, select_key=select_key)

    def get_site_info(self, siteid, select_key='*'):
        return self.get('site_info', {'siteid': siteid}, select_key=select_key)

    def get_user_info(self, appid, openid='', unionid='', select_key='*'):
        return self.get('wechat_user_info', {'appid': appid, 'openid': openid, 'unionid': unionid},
                        select_key=select_key)