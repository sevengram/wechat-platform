# -*- coding: utf-8 -*-

import hashlib

import MySQLdb
import MySQLdb.cursors


def get_redis_key(table, data, keys):
    p = [(k.decode('utf8'), v.decode('utf8')) if type(v) is str else
         (k.decode('utf8'), unicode(v))
         for k, v in sorted(data.items()) if v and k in keys]
    return hashlib.md5(
        table + ':' + '&'.join([(k + u'=' + v).encode('utf8') for k, v in p])).hexdigest().upper()


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
        placeholders = ', '.join(map(lambda n: n + ' = %s', queries.keys()))
        request = 'SELECT %s FROM %s WHERE %s' % (select_key, table, placeholders)
        records = self.execute(request, queries.values())
        if not records:
            return None
        else:
            if select_key == '*':
                return {k: v.decode('utf8') if type(v) is str else v for k, v in records.iteritems()}
            else:
                result = records.get(select_key)
                return result.decode('utf8') if type(result) is str else result

    def set(self, table, data, noninsert=None):
        noninsert = noninsert or []
        insert_dict = {k: v for k, v in data.iteritems() if k not in noninsert}
        columns = ', '.join(insert_dict.keys())
        insert_holders = ', '.join(['%s'] * len(insert_dict))
        request = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, insert_holders)
        self.execute(request, insert_dict.values())

    def replace(self, table, data, noninsert=None, nonupdate=None):
        nonupdate = nonupdate or []
        noninsert = noninsert or []
        insert_dict = {k: v for k, v in data.iteritems() if k not in noninsert}
        columns = ', '.join(insert_dict.keys())
        insert_holders = ', '.join(['%s'] * len(insert_dict))
        update_dict = {k: v for k, v in insert_dict.iteritems() if k not in nonupdate}
        update_holders = ', '.join(map(lambda n: n + ' = %s', update_dict.keys()))
        request = 'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (
            table, columns, insert_holders, update_holders)
        self.execute(request, insert_dict.values() + update_dict.values())


class WechatStorage(Storage):
    def __init__(self, host, user, passwd):
        super(WechatStorage, self).__init__('wechat_platform', host, user, passwd)

    def add_user_info(self, user, noninsert=None):
        self.replace('wechat_user_info', user,
                     noninsert=noninsert)

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


wechat_storage = WechatStorage(host='newbuy01.mysql.rds.aliyuncs.com',
                               user='wechat_admin',
                               passwd='_WecAd456')

# wechat_storage = WechatStorage(host='127.0.0.1',
#                                user='root',
#                                passwd='eboue')
