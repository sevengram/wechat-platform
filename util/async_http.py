# -*- coding: utf-8 -*-

from collections import defaultdict
import json
import urllib

import tornado.gen
import tornado.httpclient

from util import dtools


type_methods = defaultdict(lambda: urllib.urlencode, {
    'json': json.dumps,
    'xml': dtools.dict2xml,
    'form': urllib.urlencode
})


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