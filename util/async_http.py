# -*- coding: utf-8 -*-

import json
import urllib

import tornado.gen
import tornado.httpclient

from util import dtools


type_methods = {
    'json': json.dumps,
    'xml': dtools.dict2xml,
    'form': urllib.urlencode
}


@tornado.gen.coroutine
def post_dict(url, data, data_type='form'):
    client = tornado.httpclient.AsyncHTTPClient()
    req = tornado.httpclient.HTTPRequest(
        url=url,
        method='POST',
        body=type_methods.get(data_type)(data)
    )
    resp = yield client.fetch(req)
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def get_dict(url, data):
    client = tornado.httpclient.AsyncHTTPClient()
    req = tornado.httpclient.HTTPRequest(
        url=url + '?' + urllib.urlencode(data),
        method='GET'
    )
    resp = yield client.fetch(req)
    raise tornado.gen.Return(resp)
