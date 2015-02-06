# -*- coding: utf-8 -*-

import hashlib

import MySQLdb
import MySQLdb.cursors


def get_redis_key(table, data, keys):
    p = [(k, v.decode('utf8')) if type(v) is str else
         (k, unicode(v))
         for k, v in sorted(data.items()) if v and k in keys]
    return hashlib.md5(
        table + ':' + '&'.join([(k + u'=' + v).encode('utf8') for k, v in p])).hexdigest().upper()


class Storage(object):
    def __init__(self, db_name, db_host, db_user, db_pwd):
        self.db_usr = db_user
        self.db_pwd = db_pwd
        self.db_name = db_name
        self.db_host = db_host
        self.connect()

    def connect(self):
        self.connection = MySQLdb.connect(
            user=self.db_usr, passwd=self.db_pwd, host=self.db_host, db=self.db_name, charset='utf8')

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
        placeholders = ' and '.join(map(lambda n: n + '=%s', queries.keys()))
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
        update_holders = ', '.join(map(lambda n: n + '=%s', update_dict.keys()))
        request = 'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (
            table, columns, insert_holders, update_holders)
        self.execute(request, insert_dict.values() + update_dict.values())
