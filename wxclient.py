# -*- coding: utf-8 -*-

import Cookie
import json
import time

import tornado.gen
import tornado.httpclient

import url
import errinfo
from util import http
from wxstorage import wechat_storage


def _parse_wechat_resp(resp):
    if resp.code != 200:
        return {'err_code': 1001, 'data': {}}
    resp_data = json.loads(resp.body)
    err_code = resp_data.get('errcode')
    if err_code:
        wechat_err = errinfo.wechat_map[int(err_code)]
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
            url=url.wechat_basic_access_token,
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
def _wechat_api_call(appid, fn, fn_url, fn_data, retry=0):
    token_result = yield _get_access_token(appid, refresh=(retry != 0))
    if token_result.get('err_code', 1) != 0:
        raise tornado.gen.Return(token_result)
    try:
        resp = yield fn(
            url=fn_url,
            data=dict(fn_data, access_token=token_result['data']['access_token'])
        )
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})
    result = _parse_wechat_resp(resp)
    if result.get('err_code', 1) == 1004 and retry < 3:
        result = yield _wechat_api_call(appid, fn, fn_url, fn_data, retry + 1)
        raise tornado.gen.Return(result)
    else:
        raise tornado.gen.Return(result)


@tornado.gen.coroutine
def get_user_info(appid, openid):
    resp = yield _wechat_api_call(
        appid=appid,
        fn=http.get_dict,
        fn_url=url.wechat_basic_userinfo,
        fn_data={
            'openid': openid,
            'lang': 'zh_CN'
        })
    raise tornado.gen.Return(resp)


_default_headers = {
    'Connection': 'keep-alive',
    'Origin': url.mp_base,
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': http.user_agent,
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


class MockBrowser(object):
    def __init__(self):
        self.tokens = {}
        self.cookies = {}

    def init_cookies(self, appid):
        appinfo = wechat_storage.get_app_info(appid)
        self.cookies[appid] = {
            'data_bizuin': appinfo['data_bizuin'],
            'slave_user': appinfo['openid'],
            'bizuin': appinfo['bizuin']
        }

    def build_cookies(self, appid):
        if appid not in self.cookies:
            self.init_cookies(appid)
        return ';'.join(['%s=%s' % (key, value) for key, value in self.cookies[appid].iteritems()])

    def set_cookies(self, appid, headers):
        if appid not in self.cookies:
            self.init_cookies(appid)
        for sc in headers.get_list("Set-Cookie"):
            c = Cookie.SimpleCookie(sc)
            for morsel in c.values():
                if morsel.key not in ['data_bizuin', 'slave_user', 'bizuin']:
                    if morsel.value and morsel.value != 'EXPIRED':
                        self.cookies[appid][morsel.key] = morsel.value
                    else:
                        self.cookies[appid].pop(morsel.key, None)

    def has_login(self, appid):
        return appid in self.tokens and appid in self.cookies and self.cookies[appid].get('slave_sid') and self.cookies[
            appid].get('data_ticket') and time.time() - self.tokens[appid].get('last_login', 0) < 60 * 20

    @tornado.gen.coroutine
    def post_form(self, appid, post_url, data, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self.build_cookies(appid),
            'Accept': kwargs.get('accept', 'application/json, text/javascript, */*; q=0.01'),
        })
        resp = yield http.post_dict(url=post_url, data=data, headers=headers)
        if resp.code == 200:
            self.set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)

    @tornado.gen.coroutine
    def post_data(self, appid, post_url, data, content_type, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self.build_cookies(appid),
            'Content-Type': content_type,
        })
        resp = yield http.post_dict(url=post_url, data=data, data_type='raw', headers=headers)
        if resp.code == 200:
            self.set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)

    @tornado.gen.coroutine
    def get(self, appid, get_url, data, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self.build_cookies(appid),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        resp = yield http.get_dict(url=get_url, data=data, headers=headers)
        if resp.code == 200:
            self.set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)