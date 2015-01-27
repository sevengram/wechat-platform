# -*- coding: utf-8 -*-
import json
import time

import tornado.gen
import tornado.httpclient

import storage
from consts import url
from consts import errno
from util import async_http as ahttp


_wechat_access_tokens = {
}


def _parse_wechat_resp(resp):
    if resp.code != 200:
        return {'err_code': 1001}
    resp_data = json.loads(resp.body)
    if resp_data.get('errcode'):
        wechat_err = errno.wechat_map[int(resp_data.get('errcode'))]
        return {'err_code': wechat_err[0], 'err_msg': wechat_err[1]}
    return {'err_code': 0}


@tornado.gen.coroutine
def _get_access_token(appid, refresh=False):
    if appid in _wechat_access_tokens and not refresh:
        wat = _wechat_access_tokens[appid]
        if int(time.time()) - int(wat['timestamp']) < int(wat['expires_in']):
            raise tornado.gen.Return({
                'err_code': 0,
                'data': {
                    'access_token': wat['access_token']
                }
            })
    try:
        resp = yield ahttp.get_dict(
            url=url.wechat_basic_access_token,
            data={
                'grant_type': 'client_credential',
                'appid': appid,
                'secret': storage.wechat_storage.get_app_info(appid=appid, select_key='secret')
            })
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})

    result = _parse_wechat_resp(resp)
    if result.get('err_code') != 0:
        raise tornado.gen.Return(result)

    resp_data = json.loads(resp.body)
    result['data'] = {
        'access_token': resp_data['access_token']
    }
    _wechat_access_tokens[appid] = {
        'access_token': resp_data['access_token'],
        'expires_in': resp_data['expires_in'],
        'timestamp': int(time.time())
    }
    raise tornado.gen.Return(result)


@tornado.gen.coroutine
def get_user_info(appid, openid, retry=0):
    token_result = yield _get_access_token(appid, refresh=(retry != 0))
    if token_result.get('err_code') != 0:
        raise tornado.gen.Return(token_result)

    token = token_result['access_token']
    try:
        resp = yield ahttp.get_dict(
            url=url.wechat_basic_userinfo,
            data={
                'access_token': token,
                'openid': openid,
                'lang': 'zh_CN'
            })
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})

    result = _parse_wechat_resp(resp)
    if result.get('err_code') == 1004:
        if retry < 3:
            user_info = yield get_user_info(appid, openid, retry + 1)
            raise tornado.gen.Return(user_info)
        else:
            raise tornado.gen.Return(result)
    elif result.get('err_code') != 0:
        raise tornado.gen.Return(result)