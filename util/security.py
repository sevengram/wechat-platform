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


def check_sign(data, key, method):
    if method == 'md5':
        sign = data.get('sign')
        nonce_key = 'nonce_str'
    elif method == 'sha1':
        sign = data.get('signature')
        nonce_key = 'nonce'
    else:
        return False
    if not sign or not nonce_key in data:
        return False
    return build_sign(data, key, method) == sign


def build_sign(data, key, method='md5'):
    if method == 'md5':
        p = [(k.decode('utf8'), v.decode('utf8')) if type(v) is str else
             (k.decode('utf8'), unicode(v))
             for k, v in sorted(data.items()) if v and k != 'sign']
        return hashlib.md5(
            '&'.join([(k + u'=' + v).encode('utf8') for k, v in p]) + '&key=' + key).hexdigest().upper()
    elif method == 'sha1':
        p = [key, data.get('timestamp', ''), data.get('nonce', '')]
        p.sort()
        return hashlib.sha1(''.join(p)).hexdigest()
    else:
        return ''

