# -*- coding: utf-8 -*-

import base64
import hashlib
import random
from Crypto.Cipher import AES


block_size = AES.block_size
pad = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
unpad = lambda s: s[0:-ord(s[-1])]


def encrypt(plain, *args):
    return base64.b64encode(AES.new(pad((''.join(args) * 11)[::-3][:29])).encrypt(pad(plain)))


def decrypt(cipher, *args):
    return unpad(AES.new(pad((''.join(args) * 11)[::-3][:29])).decrypt(base64.b64decode(cipher)))


def nonce_str():
    return str(random.random())[2:]


def check_sign(data, apikey):
    sign = data.get('sign')
    if not 'nonce_str' in data:
        return False
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
