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

    def get(self, table, queries, filters=None, select_key='*'):
        queries = {k: v for k, v in queries.iteritems() if v}
        if not queries:
            return None
        if not filters:
            filters = queries.keys()
        redis_key = dtools.get_redis_key(table, queries, filters)
        cache = redis.Hash(redis_key)
        if not len(cache):
            placeholders = ', '.join(map(lambda n: n + ' = %s', filters))
            request = 'SELECT %s FROM %s WHERE %s' % (select_key, table, placeholders)
            records = self.execute(request, [v for k, v in queries.iteritems() if k in filters])
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

    def set(self, table, data, cache_keys=None):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        request = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, placeholders)
        self.execute(request, data.values())
        if not cache_keys:
            redis_key = dtools.get_redis_key(table, data, cache_keys)
            redis.Hash(redis_key).update(data)

    def replace(self, table, data, nonupdate=None, cache_keys=None):
        if not nonupdate:
            nonupdate = []
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        updatedic = {k: v for k, v in data.iteritems() if k not in nonupdate}
        updateholders = ', '.join(map(lambda n: n + ' = %s', updatedic.keys()))
        request = 'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (
            table, columns, placeholders, updateholders)
        self.execute(request, data.values() + updatedic.values())
        if not cache_keys:
            redis_key = dtools.get_redis_key(table, data, cache_keys)
            redis.Hash(redis_key).update(data)


class WechatStorage(Storage):
    def __init__(self, host, user, passwd):
        super(WechatStorage, self).__init__('wechat_platform', host, user, passwd)

    def add_user_info(self, user):
        self.replace('wechat_user_info', user, nonupdate=['utime'], cache_keys=['appid', 'openid'])

    def get_app_info(self, appid='', openid='', select_key='*'):
        return self.get('wechat_app_info', {'openid': openid, 'appid': appid}, select_key=select_key)

    def get_site_info(self, siteid, select_key='*'):
        return self.get('site_info', {'siteid': siteid}, select_key=select_key)