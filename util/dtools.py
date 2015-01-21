# -*- coding: utf-8 -*-

import hashlib
import time

from util import xmltodict


def transfer(src, copys=None, renames=None):
    r1 = {key: src.get(key, '') for key in copys} if copys else {}
    r2 = {new_key: src.get(key, '') for key, new_key in renames} if renames else {}
    return dict(r1, **r2)


def special_decode(text):
    return text.replace('\x00', '<').replace('\x01', '>').replace('\x02', '&')


def special_encode(text):
    return text.replace('<', '\x00').replace('>', '\x01').replace('&', '\x02')


def dict2xml(dic):
    result = xmltodict.unparse({'xml': dic})
    return special_decode(result[result.index('\n') + 1:])


def xml2dict(xml):
    return xmltodict.parse(xml)['xml']


def get_redis_key(table, data, keys):
    p = [(k.decode('utf8'), v.decode('utf8')) if type(v) is str else
         (k.decode('utf8'), unicode(v))
         for k, v in sorted(data.items()) if v and k in keys]
    return hashlib.md5(
        table + ':' + '&'.join([(k + u'=' + v).encode('utf8') for k, v in p])).hexdigest().upper()


def text_response(touser, text, tag):
    response = {'ToUserName': touser, 'FromUserName': 'gh_c008a36d9e93', 'CreateTime': int(
        time.time()), 'MsgType': 'text', 'Content': text, 'Tag': tag}  # TODO: hardcode
    return dict2xml(response)
