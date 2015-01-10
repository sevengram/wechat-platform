# -*- coding: utf-8 -*-
import time
from util import xmltodict


def transfer(src, copys, renames=None):
    r1 = {key: src[key] for key in copys}
    r2 = {new_key: src[key] for key, new_key in renames} if renames else {}
    return dict(r1, **r2)


def special_decode(text):
    return text.replace('\x00', '<').replace('\x01', '>').replace('\x02', '&')


def special_encode(text):
    return text.replace('<', '\x00').replace('>', '\x01').replace('&', '\x02')


def cdata(text):
    return special_encode('<![CDATA[%s]]>' % text if not text is None else '<![CDATA[]]>')


def dict2xml(dic):
    result = xmltodict.unparse({'xml': dic})
    return special_decode(result[result.index('\n') + 1:])


def xml2dict(xml):
    return xmltodict.parse(xml)['xml']


def text_response(touser, text, tag):
    response = {'ToUserName': cdata(touser), 'FromUserName': cdata('gh_c008a36d9e93'), 'CreateTime': int(
        time.time()), 'MsgType': cdata('text'), 'Content': cdata(text), 'Tag': tag}
    result = xmltodict.unparse({'xml': response})
    return special_decode(result[result.index('\n') + 1:])
