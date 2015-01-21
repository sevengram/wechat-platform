# -*- coding: utf-8 -*-

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
