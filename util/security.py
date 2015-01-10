# -*- coding: utf-8 -*-

import hashlib
import random

from tornado.web import HTTPError


def nonce_str():
    return str(random.random())[2:]


def check_signature(data, apikey):
    sign = data.get('sign')
    if not sign:
        raise HTTPError(400)
    if type(sign) is list and sign:
        sign = sign[0]
    return build_signature(data, apikey) == sign


def build_signature(data, apikey):
    p = [(k, v[0]) if type(v) is list else (k, v) for k, v in data.iteritems() if v and k != 'sign']
    p = [(k, v.decode('utf8')) if type(v) is str else (k, unicode(v)) for k, v in p]
    p.sort()
    return hashlib.md5(
        '&'.join([(k.decode('utf8') + u'=' + v).encode('utf8') for k, v in p]) + '&key=' + apikey).hexdigest().upper()