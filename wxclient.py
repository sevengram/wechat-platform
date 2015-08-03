# -*- coding: utf-8 -*-

import Cookie
import json
import random
import time
import urllib
import urlparse

from bs4 import BeautifulSoup
import tornado.gen
import tornado.httpclient

import url
import errinfo
from util import http
from wxstorage import wechat_storage


def check_same(timestamp, content, mtype, user):
    if mtype == 'text' and content:
        return user['date_time'] == timestamp and user['content'].strip(
            ' \t\r\n') == content.strip(' \t\r\n') and user['type'] == 1
    elif mtype == 'location':
        return user['date_time'] == timestamp and user['content'].startswith(
            'http://weixin.qq.com/cgi-bin/redirectforward') and user['type'] == 1
    elif mtype == 'image':
        return user['date_time'] == timestamp and user['type'] == 2
    else:
        return False


def _parse_wechat_resp(resp):
    if resp.code != 200:
        return {'err_code': 1001}
    resp_data = json.loads(resp.body)
    err_code = resp_data.get('errcode')
    if err_code:
        wechat_err = errinfo.wechat_map[int(err_code)]
        return {'err_code': wechat_err[0], 'err_msg': wechat_err[1]}
    return {'err_code': 0, 'data': resp_data}


def _parse_mp_resp(resp):
    if resp.code != 200:
        return {'err_code': 1001}
    resp_data = json.loads(resp.body)
    try:
        if resp_data and resp_data['base_resp']['ret'] == -3:
            return {'err_code': 7001}
        elif resp_data and resp_data['base_resp']['ret'] == 0:
            return {'err_code': 0, 'data': resp_data}
        else:
            return {'err_code': 7002}
    except (KeyError, AttributeError, TypeError):
        return {'err_code': 9003}


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
        app_info = wechat_storage.get_app_info(appid=appid)
        resp = yield http.get_dict(
            url=url.wechat_basic_access_token,
            data={
                'grant_type': 'client_credential',
                'appid': appid,
                'secret': app_info['secret']
            })
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})

    result = _parse_wechat_resp(resp)
    if result.get('err_code', 1) != 0:
        raise tornado.gen.Return(result)
    else:
        result_data = result.get('data')
        wechat_storage.add_access_token(app_info['id'], appid, result_data.get('access_token'),
                                        result_data.get('expires_in'))
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

    def _init_cookies(self, appid):
        appinfo = wechat_storage.get_app_info(appid)
        self.cookies[appid] = {
            'data_bizuin': appinfo['data_bizuin'],
            'slave_user': appinfo['openid'],
            'bizuin': appinfo['bizuin']
        }

    def _build_cookies(self, appid):
        if appid not in self.cookies:
            self._init_cookies(appid)
        return ';'.join(['%s=%s' % (key, value) for key, value in self.cookies[appid].iteritems()])

    def _set_cookies(self, appid, headers):
        if appid not in self.cookies:
            self._init_cookies(appid)
        for sc in headers.get_list("Set-Cookie"):
            c = Cookie.SimpleCookie(sc)
            for morsel in c.values():
                if morsel.key not in ['data_bizuin', 'slave_user', 'bizuin']:
                    if morsel.value and morsel.value != 'EXPIRED':
                        self.cookies[appid][morsel.key] = morsel.value
                    else:
                        self.cookies[appid].pop(morsel.key, None)

    @tornado.gen.coroutine
    def _post_form(self, appid, post_url, data, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self._build_cookies(appid),
            'Accept': kwargs.get('accept', 'application/json, text/javascript, */*; q=0.01'),
        })
        resp = yield http.post_dict(url=post_url, data=data, headers=headers)
        if resp.code == 200:
            self._set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)

    @tornado.gen.coroutine
    def _post_data(self, appid, post_url, data, content_type, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self._build_cookies(appid),
            'Content-Type': content_type,
        })
        resp = yield http.post_dict(url=post_url, data=data, data_type='raw', headers=headers)
        if resp.code == 200:
            self._set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)

    @tornado.gen.coroutine
    def _get(self, appid, get_url, data, **kwargs):
        headers = dict(_default_headers, **{
            'Referer': kwargs.get('referer', url.mp_base),
            'Cookie': self._build_cookies(appid),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        resp = yield http.get_dict(url=get_url, data=data, headers=headers)
        if resp.code == 200:
            self._set_cookies(appid, resp.headers)
        raise tornado.gen.Return(resp)

    def has_login(self, appid):
        return appid in self.tokens and appid in self.cookies and self.cookies[appid].get('slave_sid') and self.cookies[
            appid].get('data_ticket') and time.time() - self.tokens[appid].get('last_login', 0) < 60 * 20

    @tornado.gen.coroutine
    def login(self, appid):
        appinfo = wechat_storage.get_app_info(appid)
        username = appinfo['mp_username']
        pwd = appinfo['mp_pwd']
        try:
            resp = yield self._post_form(appid, url.mp_login, {
                'username': username,
                'pwd': pwd,
                'f': 'json'})
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 1001})
        result = _parse_mp_resp(resp)
        if result.get('err_code', 1) != 0:
            raise tornado.gen.Return(result)
        result_data = result.get('data')
        self.tokens[appid] = {
            'last_login': time.time(),
            'token': dict(urlparse.parse_qsl(result_data['redirect_url']))['token']
        }
        raise tornado.gen.Return({
            'err_code': 0,
            'data': {'token': self.tokens[appid]['token']}
        })

    @tornado.gen.coroutine
    def send_single_message(self, appid, fakeid, content):
        post_url = url.mp_singlesend + '?' + urllib.urlencode({
            't': 'ajax-response',
            'f': 'json',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        referer_url = url.mp_singlesend_page + '?' + urllib.urlencode({
            'tofakeid': fakeid,
            't': 'message/send',
            'action': 'index',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        try:
            resp = yield self._post_form(appid, post_url, {
                'token': self.tokens[appid]['token'],
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': 1,
                'type': 1,
                'content': content,
                'tofakeid': fakeid,
                'random': random.random()
            }, referer=referer_url)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 1001})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def find_user(self, appid, timestamp, content, mtype, count=30, offset=0):
        referer_url = url.mp_home + '?' + urllib.urlencode({
            't': 'home/index',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        try:
            resp = yield self._get(appid, url.mp_message, {
                'count': count,
                'offset': offset,
                'day': 7,
                'token': self.tokens[appid]['token']
            }, referer=referer_url)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 1001})
        if resp.code != 200:
            raise tornado.gen.Return({'err_code': 1001})

        raw = BeautifulSoup(resp.body)
        try:
            t = raw.find_all('script', {'type': 'text/javascript', 'src': ''})[-2].text  # TODO: Fix hardcode index
            users = json.loads(t[t.index('['):t.rindex(']') + 1], encoding='utf-8')
        except (ValueError, IndexError):
            users = None

        if not users:
            try:
                if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
                    raise tornado.gen.Return({'err_code': 7001})
            except AttributeError:
                pass
            raise tornado.gen.Return({'err_code': 7101})

        for i in range(0, len(users) - 1):
            if users[i]['date_time'] < timestamp:
                raise tornado.gen.Return({'err_code': 7101})
            elif check_same(timestamp, content, mtype, users[i]):
                if not check_same(timestamp, content, mtype, users[i + 1]):
                    raise tornado.gen.Return({'err_code': 0, 'data': users[i]})
                else:
                    raise tornado.gen.Return({'err_code': 7101})
        res = yield self.find_user(timestamp, content, mtype, count, count + offset - 1)
        raise tornado.gen.Return(res)

mock_browser = MockBrowser()

# class WechatConnector(object):
#
#     @tornado.gen.coroutine
#     def get_operation_seq(self):
#         referer = home_url + '?' + urllib.urlencode({
#             't': 'home/index',
#             'token': self.token,
#             'lang': 'zh_CN'})
#         result = yield self.get_request(multisend_page_url, {
#             't': 'mass/send',
#             'lang': 'zh_CN',
#             'token': self.token
#         }, referer=referer)
#         raw = BeautifulSoup(result)
#         try:
#             t = raw.find_all(
#                 'script', {'type': 'text/javascript', 'src': ''})[-2].text
#             s = t[t.find('operation_seq'):].split(',')[0]
#             seq = s[s.index('\"') + 1:s.rindex('\"')]
#         except (ValueError, IndexError):
#             seq = None
#
#         if not seq:
#             try:
#                 if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
#                     print 'get_operation_seq failed: login expired'
#                     sys.stdout.flush()
#                     raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
#             except AttributeError:
#                 pass
#             print 'get_operation_seq failed'
#             sys.stdout.flush()
#             raise tornado.gen.Return({'err': 10, 'msg': 'fail to get operation_seq'})
#
#         print 'get_operation_seq success: ', seq
#         sys.stdout.flush()
#         raise tornado.gen.Return({'err': 0, 'msg': seq})
#
#     @tornado.gen.coroutine
#     def get_ticket(self):
#         referer = appmsg_url + '?' + urllib.urlencode({
#             'begin': 0,
#             'count': 10,
#             't': 'media/appmsg_list',
#             'token': self.token,
#             'type': '10',
#             'action': 'list',
#             'lang': 'zh_CN'})
#         result = yield self.get_request(appmsg_url, {
#             't': 'media/appmsg_edit',
#             'action': 'edit',
#             'type': '10',
#             'isMul': 0,
#             'isNew': 1,
#             'lang': 'zh_CN',
#             'token': self.token
#         }, referer=referer)
#         ticket = None
#         raw = BeautifulSoup(result)
#         try:
#             ts = raw.find_all('script', {'type': 'text/javascript', 'src': ''})
#             for t in ts:
#                 if t.text.strip(' \t\r\n').startswith('window.wx'):
#                     i = t.text.find('ticket:')
#                     ticket = t.text[i + 8:i + 48]
#                     break
#         except (ValueError, IndexError):
#             ticket = None
#
#         if not ticket:
#             try:
#                 if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
#                     print 'get_ticket failed: login expired'
#                     sys.stdout.flush()
#                     raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
#             except AttributeError:
#                 pass
#             print 'get_ticket failed'
#             sys.stdout.flush()
#             raise tornado.gen.Return({'err': 7, 'msg': 'fail to get ticket'})
#
#         print 'get_ticket success: ', ticket
#         sys.stdout.flush()
#         raise tornado.gen.Return({'err': 0, 'msg': ticket})
#
#     @tornado.gen.coroutine
#     def get_lastest_material(self, count, title):
#         referer = home_url + '?' + urllib.urlencode({
#             't': 'home/index',
#             'token': self.token,
#             'lang': 'zh_CN'})
#         result = yield self.get_request(appmsg_url, {
#             'begin': 0,
#             'count': count,
#             't': 'media/appmsg_list',
#             'token': self.token,
#             'type': '10',
#             'action': 'list',
#             'lang': 'zh_CN'
#         }, referer=referer)
#         raw = BeautifulSoup(result)
#         itemid = None
#         try:
#             t = raw.find_all(
#                 'script', {'type': 'text/javascript', 'src': ''})[-2].text
#             items = json.loads(t[t.index('{'):t.rindex('}') + 1], encoding='utf-8')
#             for item in items['item']:
#                 if title == item['title']:
#                     itemid = item['app_id']
#                     break
#         except (ValueError, IndexError):
#             pass
#
#         if not itemid:
#             try:
#                 if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
#                     print 'get_lastest_material failed: login expired'
#                     sys.stdout.flush()
#                     raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
#             except AttributeError:
#                 pass
#             print 'get_lastest_material failed'
#             sys.stdout.flush()
#             raise tornado.gen.Return({'err': 9, 'msg': 'fail to match lastest material'})
#
#         print 'get_lastest_material success: ', itemid
#         sys.stdout.flush()
#         raise tornado.gen.Return({'err': 0, 'msg': itemid})
#
#     @tornado.gen.coroutine
#     def upload_image(self, ticket, filename):
#         url = upload_url + '?' + urllib.urlencode({
#             'ticket_id': 'sevengram',
#             'ticket': ticket,
#             'f': 'json',
#             'token': self.token,
#             'lang': 'zh_CN',
#             'action': 'upload_material'})
#         referer = appmsg_url + '?' + urllib.urlencode({
#             't': 'media/appmsg_edit',
#             'action': 'edit',
#             'type': '10',
#             'isMul': 0,
#             'isNew': 1,
#             'lang': 'zh_CN',
#             'token': self.token})
#         content_type, data = encode_multipart_formdata(
#             fields=[('Filename', filename.split('/')[-1]), (
#                 'folder', '/cgi-bin/uploads'), ('Upload', 'Submit Query')],
#             files=[('file', filename, open(filename, 'rb').read())])
#         result = yield self.post_formdata(url, content_type, data, referer=referer)
#         print 'upload_image response:', result
#         sys.stdout.flush()
#         try:
#             if result['base_resp']['ret'] == -3:
#                 raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
#             elif result['base_resp']['ret'] == 0:
#                 raise tornado.gen.Return({'err': 0, 'msg': result['content']})
#             else:
#                 raise tornado.gen.Return({'err': 5, 'msg': result['base_resp']['err_msg']})
#         except (KeyError, AttributeError, TypeError):
#             raise tornado.gen.Return({'err': 5, 'msg': 'fail to post image'})
#
#     @tornado.gen.coroutine
#     def save_material(self, title, content, digest, author, fileid, sourceurl):
#         url = save_material_url + '?' + urllib.urlencode({
#             't': 'ajax-response',
#             'sub': 'create',
#             'type': '10',
#             'token': self.token,
#             'lang': 'zh_CN'})
#         referer = appmsg_url + '?' + urllib.urlencode({
#             't': 'media/appmsg_edit',
#             'action': 'edit',
#             'type': '10',
#             'isMul': 0,
#             'isNew': 1,
#             'lang': 'zh_CN',
#             'token': self.token})
#         result = yield self.post_data(url, {
#             'token': self.token,
#             'lang': 'zh_CN',
#             'f': 'json',
#             'ajax': 1,
#             'type': 1,
#             'content0': content.encode('utf-8'),
#             'count': 1,
#             'random': random.random(),
#             'AppMsgId': '',
#             'vid': '',
#             'title0': title.encode('utf-8'),
#             'digest0': digest.encode('utf-8'),
#             'author0': author.encode('utf-8'),
#             'fileid0': fileid,
#             'show_cover_pic0': 1,
#             'sourceurl0': sourceurl
#         }, referer=referer, accept='text/html, */*; q=0.01')
#         print 'save_material response:', result
#         sys.stdout.flush()
#         if result and result.get('ret') == '0':
#             raise tornado.gen.Return({'err': 0, 'msg': 'ok'})
#         elif result:
#             raise tornado.gen.Return({'err': 8, 'msg': result.get('msg', 'fail to save material')})
#         else:
#             raise tornado.gen.Return({'err': 8, 'msg': 'fail to save material'})
#
#     @tornado.gen.coroutine
#     def multi_send_message(self, operation_seq, appmsgid, groupid):
#         url = multisend_url + '?' + urllib.urlencode({
#             't': 'ajax-response',
#             'token': self.token,
#             'lang': 'zh_CN'})
#         referer = multisend_page_url + '?' + urllib.urlencode({
#             't': 'mass/send',
#             'lang': 'zh_CN',
#             'token': self.token})
#         result = yield self.post_data(url, {
#             'token': self.token,
#             'lang': 'zh_CN',
#             'f': 'json',
#             'ajax': 1,
#             'type': 10,
#             'synctxweibo': 1,
#             'cardlimit': 1,
#             'sex': 0,
#             'random': random.random(),
#             'groupid': groupid,
#             'appmsgid': appmsgid,
#             'operation_seq': operation_seq,
#             'country': '',
#             'province': '',
#             'city': '',
#             'imgcode': ''
#         }, referer=referer)
#         print 'multi_send_message response:', result
#         sys.stdout.flush()
#         if result and result.get('ret') == '-20000':
#             raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
#         elif result and result.get('ret') == '64004':
#             raise tornado.gen.Return(
#                 {'err': 11, 'msg': result.get('msg', 'fail to send multi message')})
#         elif result and result.get('ret') == '0':
#             raise tornado.gen.Return({'err': 0, 'msg': 'ok'})
#         else:
#             raise tornado.gen.Return({'err': 12, 'msg': 'fail to send multi message'})
