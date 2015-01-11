# -*- coding: utf-8 -*-

import hashlib
import random


def nonce_str():
    return str(random.random())[2:]


def check_sign(data, apikey):
    sign = data.get('sign')
    if not sign:
        return False
    return build_sign(data, apikey) == sign


def build_sign(data, apikey):
    p = [(k.decode('utf8'), v.decode('utf8')) if type(v) is str else
         (k.decode('utf8'), unicode(v))
         for k, v in data.iteritems() if v and k != 'sign']
    p.sort()
    return hashlib.md5(
        '&'.join([(k + u'=' + v).encode('utf8') for k, v in p]) + '&key=' + apikey).hexdigest().upper()