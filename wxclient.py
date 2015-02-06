# -*- coding: utf-8 -*-

import json

import tornado.gen
import tornado.httpclient

import settings

import errno
from wxstorage import wechat_storage
from util import http


def _parse_wechat_resp(resp):
    if resp.code != 200:
        return {'err_code': 1001, 'data': {}}
    resp_data = json.loads(resp.body)
    errcode = resp_data.get('errcode')
    if errcode:
        wechat_err = errno.wechat_map[int(errcode)]
        return {'err_code': wechat_err[0], 'err_msg': wechat_err[1], 'data': {}}
    return {'err_code': 0, 'data': resp_data}


@tornado.gen.coroutine
def _get_access_token(appid, refresh=False):
    if not refresh:
        token = wechat_storage.get_access_token(appid)
        if token:
            raise tornado.gen.Return({
                'err_code': 0,
                'data': {'access_token': token}
            })
    try:
        resp = yield http.get_dict(
            url=settings.wechat_url['basic_access_token'],
            data={
                'grant_type': 'client_credential',
                'appid': appid,
                'secret': wechat_storage.get_app_info(appid=appid, select_key='secret')
            })
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})

    result = _parse_wechat_resp(resp)
    if result.get('err_code', 1) != 0:
        raise tornado.gen.Return(result)
    else:
        result_data = result.get('data', {})
        wechat_storage.add_access_token(appid, result_data.get('access_token'), result_data.get('expires_in'))
        raise tornado.gen.Return(result)


@tornado.gen.coroutine
def get_user_info(appid, openid, retry=0):
    token_result = yield _get_access_token(appid, refresh=(retry != 0))
    if token_result.get('err_code', 1) != 0:
        raise tornado.gen.Return(token_result)
    token = token_result['data']['access_token']
    try:
        resp = yield http.get_dict(
            url=settings.wechat_url['basic_userinfo'],
            data={
                'access_token': token,
                'openid': openid,
                'lang': 'zh_CN'
            })
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})
    result = _parse_wechat_resp(resp)
    if result.get('err_code', 1) == 1004 and retry < 3:
        user_info = yield get_user_info(appid, openid, retry + 1)
        raise tornado.gen.Return(user_info)
    else:
        raise tornado.gen.Return(result)
