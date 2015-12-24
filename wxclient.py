# -*- coding: utf-8 -*-

import Cookie
import urllib
import io
import json
import random
import time
import os
import logging
import urlparse
from PIL import Image

from bs4 import BeautifulSoup
import tornado.gen
import tornado.httpclient
import tornado.ioloop

import url
import errinfo
from util import http, dtools, security
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
        return {'err_code': 7000}
    resp_data = json.loads(resp.body)
    logging.info('mp response:%s', resp_data)
    try:
        if resp_data:
            ret = resp_data['base_resp']['ret']
            if ret == -3:
                return {'err_code': 7001}
            elif ret == 64004:
                return {'err_code': 7201}
            elif ret in {0, 154011, 154009}:
                del resp_data['base_resp']
                return {'err_code': 0, 'data': resp_data}
            else:
                logging.error('unknow mp error code: %s', resp_data['base_resp']['ret'])
                return {'err_code': 7000}
        else:
            return {'err_code': 9003}
    except (KeyError, AttributeError, TypeError):
        return {'err_code': 9003}


@tornado.gen.coroutine
def _get_access_token(appid, refresh=False):
    if not refresh:
        token = wechat_storage.get_access_token(appid)  # TODO: move this to redis
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
    if resp['err_code'] != 0:
        raise tornado.gen.Return(result)
    else:
        result_data = result.get('data')
        wechat_storage.add_access_token(app_info['id'], appid, result_data.get('access_token'),
                                        result_data.get('expires_in'))
        raise tornado.gen.Return(result)


@tornado.gen.coroutine
def _wechat_api_call(appid, fn, fn_url, fn_data, retry=0):
    token_result = yield _get_access_token(appid, refresh=(retry != 0))
    if token_result['err_code'] != 0:
        raise tornado.gen.Return(token_result)
    try:
        resp = yield fn(
            url=fn_url,
            data=dict(fn_data, access_token=token_result['data']['access_token'])
        )
    except tornado.httpclient.HTTPError:
        raise tornado.gen.Return({'err_code': 1001})
    result = _parse_wechat_resp(resp)
    if result['err_code'] == 1004 and retry < 3:
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


@tornado.gen.coroutine
def update_user_info(appid, openid):
    resp = yield get_user_info(appid, openid)
    if resp['err_code'] != 0:
        raise tornado.gen.Return({'err_code': resp['err_code']})
    else:
        resp['data']['appid'] = appid
        user_info = dtools.transfer(
            resp['data'], copys=[
                'uid',
                'appid',
                'openid',
                'unionid',
                'nickname',
                'subscribe',
                'sex',
                'city',
                'province',
                'country',
                'language',
                'headimgurl',
                'subscribe_time'
            ], allow_empty=False)
        wechat_storage.add_user_info(user_info)
        raise tornado.gen.Return({'err_code': 0, 'data': user_info})


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
        self.tokens = {}  # TODO: move this to redis
        self.cookies = {}  # TODO: move this to redis

    def _init_cookies(self, appid):
        appinfo = wechat_storage.get_app_info(appid)
        self.cookies[appid] = {
            'data_bizuin': appinfo['data_bizuin'],
            'slave_user': appinfo['openid'],
            'bizuin': appinfo['fakeid']
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

    @tornado.gen.coroutine
    def _mock_api_call(self, fn, appid, retry_limit=1, retry_count=0, timeout=0, **kwargs):
        if not self.has_login(appid):
            yield self.login(appid)
        res = yield fn(appid, **kwargs)
        if res.get('err_code') != 0 and retry_count < retry_limit:
            if timeout != 0:
                yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + timeout)
            self.clear_login(appid)
            res = yield self._mock_api_call(fn, appid, retry_limit, retry_count + 1, **kwargs)
        raise tornado.gen.Return(res)

    def has_login(self, appid):
        return appid in self.tokens and appid in self.cookies and self.cookies[appid].get('slave_sid') and self.cookies[
            appid].get('data_ticket') and time.time() - self.tokens[appid].get('last_login', 0) < 60 * 20

    def clear_login(self, appid):
        logging.info('clear login: %s', appid)
        if appid in self.tokens:
            del self.tokens[appid]
        if appid in self.cookies:
            del self.cookies[appid]

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
            logging.warning('login failed: %s', appid)
            raise tornado.gen.Return({'err_code': 7000})
        result = _parse_mp_resp(resp)
        if result['err_code'] != 0:
            logging.warning('login failed: %s %s', appid, result)
            raise tornado.gen.Return(result)
        result_data = result.get('data')
        self.tokens[appid] = {
            'last_login': time.time(),
            'token': dict(urlparse.parse_qsl(result_data['redirect_url']))['token']
        }
        logging.info('login success: %s', appid)
        raise tornado.gen.Return({
            'err_code': 0,
            'data': {'token': self.tokens[appid]['token']}
        })

    @tornado.gen.coroutine
    def _send_single_message(self, appid, fakeid, content):
        post_url = http.build_url(url.mp_singlesend, {
            't': 'ajax-response',
            'f': 'json',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        referer_url = http.build_url(url.mp_singlesend_page, {
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
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def _find_user(self, appid, timestamp, mtype, content, count=50, offset=0):
        referer_url = http.build_url(url.mp_home, {
            't': 'home/index',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        try:
            resp = yield self._get(appid, url.mp_message, {
                't': 'message/list',
                'count': count,
                'offset': offset,
                'day': 7,
                'token': self.tokens[appid]['token']
            }, referer=referer_url)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        if resp.code != 200:
            raise tornado.gen.Return({'err_code': 7000})
        users = None
        try:
            ts = BeautifulSoup(resp.body).find_all('script', {'type': 'text/javascript', 'src': ''})
            for t in ts:
                te = t.text
                if te.strip(' \t\r\n').startswith('wx.cgiData'):
                    users = json.loads(te[te.index('['):te.rindex(']') + 1], encoding='utf-8')
                    break
        except (ValueError, IndexError):
            pass
        if not users:
            logging.warning('fail to catch user list: %s', appid)
            raise tornado.gen.Return({'err_code': 7101})
        for i in range(0, len(users) - 1):
            if users[i]['date_time'] < timestamp:
                logging.warning('fail to find user: %s', appid)
                raise tornado.gen.Return({'err_code': 7101})
            elif check_same(timestamp, content, mtype, users[i]):
                logging.warning('user found: %s', users[i])
                raise tornado.gen.Return({'err_code': 0, 'data': users[i]})
        res = yield self._find_user(appid, timestamp, mtype, content, count, count + offset - 1)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def _get_contact_info(self, appid, fakeid, msg_id):
        post_url = http.build_url(url.mp_contact_info, {
            't': 'ajax-getcontactinfo',
            'fakeid': fakeid,
            'msg_id': msg_id,
            'lang': 'zh_CN'})
        referer_url = http.build_url(url.mp_message, {
            't': 'message/list',
            'count': 30,
            'offset': 0,
            'day': 7,
            'token': self.tokens[appid]['token']
        })
        try:
            resp = yield self._post_form(appid, post_url, {
                'token': self.tokens[appid]['token'],
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': 1,
                'random': random.random()
            }, referer=referer_url)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def _get_ticket(self, appid):
        referer = http.build_url(url.mp_appmsg, {
            'begin': 0,
            'count': 10,
            't': 'media/appmsg_list',
            'token': self.tokens[appid]['token'],
            'type': '10',
            'action': 'list',
            'lang': 'zh_CN'})
        try:
            resp = yield self._get(appid, url.mp_appmsg, {
                't': 'media/appmsg_edit',
                'action': 'edit',
                'type': '10',
                'isMul': 0,
                'isNew': 1,
                'lang': 'zh_CN',
                'token': self.tokens[appid]['token']
            }, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        if resp.code != 200:
            raise tornado.gen.Return({'err_code': 7000})
        ticket = None
        try:
            ts = BeautifulSoup(resp.body).find_all('script', {'type': 'text/javascript', 'src': ''})
            for t in ts:
                i = t.text.find('ticket:\"')
                if i != -1:
                    s = t.text.find('\"', i) + 1
                    e = t.text.find('\"', s)
                    ticket = t.text[s:e]
                    break
        except (ValueError, IndexError):
            pass
        if not ticket:
            logging.warning('get_ticket failed: %s', appid)
            raise tornado.gen.Return({'err_code': 7103})
        else:
            logging.info('get_ticket success: %s - %s', appid, ticket)
            raise tornado.gen.Return({'err_code': 0, 'data': {'ticket': ticket}})

    @tornado.gen.coroutine
    def _upload_image(self, appid, ticket, picurl, filename, width=0):
        img = Image.open(io.BytesIO(urllib.urlopen(picurl).read()))
        w, h = img.size
        nw = min(width, w) if width != 0 else w
        nh = int(float(nw * h) / w)
        tmp_file = '/tmp/' + security.nonce_str()
        fd = open(tmp_file, 'w')
        img.resize((nw, nh)).convert('RGB').save(fd, 'JPEG', quality=85)
        fd.close()
        fd = open(tmp_file, 'rb')
        filename = filename.encode('utf8')
        post_url = http.build_url(url.mp_upload, {
            'ticket_id': 'sevengram',
            'ticket': ticket,
            'f': 'json',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN',
            'writetype': 'doublewrite',
            'group_id': 1,
            'action': 'upload_material'})
        referer = http.build_url(url.mp_appmsg, {
            't': 'media/appmsg_edit',
            'action': 'edit',
            'type': '10',
            'isMul': 0,
            'isNew': 1,
            'lang': 'zh_CN',
            'token': self.tokens[appid]['token']})
        content_type, data = http.encode_multipart_formdata(
            fields=[('Filename', filename), ('folder', '/cgi-bin/uploads'), ('Upload', 'Submit Query')],
            files=[('file', filename, fd.read())])
        fd.close()
        os.remove(tmp_file)
        try:
            resp = yield self._post_data(appid, post_url, data, content_type, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def _save_news(self, appid, title, content, digest, author, fileid, sourceurl):
        post_url = http.build_url(url.mp_save_news, {
            't': 'ajax-response',
            'sub': 'create',
            'type': '10',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        referer = http.build_url(url.mp_appmsg, {
            't': 'media/appmsg_edit',
            'action': 'edit',
            'type': '10',
            'isMul': 0,
            'isNew': 1,
            'lang': 'zh_CN',
            'token': self.tokens[appid]['token']})
        try:
            resp = yield self._post_form(appid, post_url, {
                'token': self.tokens[appid]['token'],
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': 1,
                'type': 1,
                'content0': content.encode('utf-8'),
                'count': 1,
                'random': random.random(),
                'AppMsgId': '',
                'vid': '',
                'title0': title.encode('utf-8'),
                'digest0': digest.encode('utf-8'),
                'author0': author.encode('utf-8'),
                'fileid0': fileid,
                'show_cover_pic0': 1,
                'sourceurl0': sourceurl
            }, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def _get_operation_seq(self, appid):
        referer = http.build_url(url.mp_home, {
            't': 'home/index',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        try:
            resp = yield self._get(appid, url.mp_multisend_page, {
                't': 'mass/send',
                'lang': 'zh_CN',
                'token': self.tokens[appid]['token'],
            }, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        if resp.code != 200:
            raise tornado.gen.Return({'err_code': 7000})
        seq = None
        try:
            ts = BeautifulSoup(resp.body).find_all('script', {'type': 'text/javascript', 'src': ''})
            for t in ts:
                i = t.text.find('operation_seq:')
                if i != -1:
                    s = t.text.find('\"', i) + 1
                    e = t.text.find('\"', s)
                    seq = t.text[s:e]
                    break
        except (ValueError, IndexError):
            pass
        if not seq:
            logging.warning('get_seq failed: %s', appid)
            raise tornado.gen.Return({'err_code': 7104})
        else:
            logging.info('get_seq success: %s - %s', appid, seq)
            raise tornado.gen.Return({'err_code': 0, 'data': {'seq': seq}})

    @tornado.gen.coroutine
    def _get_latest_news(self, appid):
        referer = http.build_url(url.mp_home, {
            't': 'home/index',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        try:
            resp = yield self._get(appid, url.mp_appmsg, {
                'begin': 0,
                'count': 1,
                't': 'media/appmsg_list',
                'token': self.tokens[appid]['token'],
                'type': '10',
                'action': 'list',
                'lang': 'zh_CN'}, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        if resp.code != 200:
            raise tornado.gen.Return({'err_code': 7000})
        item = None
        try:
            ts = BeautifulSoup(resp.body).find_all('script', {'type': 'text/javascript', 'src': ''})
            for t in ts:
                te = t.text
                if te.strip(' \t\r\n').startswith('wx.cgiData'):
                    item = json.loads(te[te.index('{'):te.rindex('}') + 1], encoding='utf-8')['item'][0]
                    del item['multi_item']
                    break
        except (ValueError, IndexError):
            pass
        if not item:
            logging.warning('get_latest_news failed: %s', appid)
            raise tornado.gen.Return({'err_code': 7105})
        else:
            logging.info('get_latest_news success: %s', item)
            raise tornado.gen.Return({'err_code': 0, 'data': item})

    @tornado.gen.coroutine
    def _presend_multi_message(self, appid, appmsgid, times):
        post_url = http.build_url(url.mp_multisend, {
            'action': 'get_appmsg_copyright_stat',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        referer = http.build_url(url.mp_multisend_page, {
            't': 'mass/send',
            'lang': 'zh_CN',
            'token': self.tokens[appid]['token']})
        try:
            resp = yield self._post_form(appid, post_url, {
                'token': self.tokens[appid]['token'],
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': 1,
                'type': 10,
                'first_check': times,
                'random': random.random(),
                'appmsgid': appmsgid
            }, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def _send_multi_message(self, appid, appmsgid, operation_seq, groupid):
        post_url = http.build_url(url.mp_multisend, {
            't': 'ajax-response',
            'token': self.tokens[appid]['token'],
            'lang': 'zh_CN'})
        referer = http.build_url(url.mp_multisend_page, {
            't': 'mass/send',
            'lang': 'zh_CN',
            'token': self.tokens[appid]['token']})
        try:
            resp = yield self._post_form(appid, post_url, {
                'token': self.tokens[appid]['token'],
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': 1,
                'type': 10,
                'synctxweibo': 1,
                'cardlimit': 1,
                'sex': 0,
                'random': random.random(),
                'groupid': groupid,
                'appmsgid': appmsgid,
                'operation_seq': operation_seq,
                'country': '',
                'province': '',
                'city': '',
                'imgcode': '',
                'direct_send': 1
            }, referer=referer)
        except tornado.httpclient.HTTPError:
            raise tornado.gen.Return({'err_code': 7000})
        raise tornado.gen.Return(_parse_mp_resp(resp))

    @tornado.gen.coroutine
    def send_single_message(self, appid, fakeid, content):
        res = yield self._mock_api_call(self._send_single_message, appid, fakeid=fakeid, content=content)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def find_user(self, appid, timestamp, mtype, content):
        res = yield self._mock_api_call(self._find_user, appid, timestamp=timestamp, mtype=mtype, content=content,
                                        retry_limit=2, timeout=10)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def get_contact_info(self, appid, fakeid, msg_id):
        res = yield self._mock_api_call(self._get_contact_info, appid, fakeid=fakeid, msg_id=msg_id)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def get_ticket(self, appid):
        res = yield self._mock_api_call(self._get_ticket, appid)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def upload_image(self, appid, ticket, picurl, filename, width=0):
        res = yield self._mock_api_call(self._upload_image, appid, ticket=ticket, picurl=picurl, filename=filename,
                                        width=width)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def save_news(self, appid, title, content, digest, author, fileid, sourceurl):
        res = yield self._mock_api_call(self._save_news, appid=appid, title=title, content=content, digest=digest,
                                        author=author, fileid=fileid, sourceurl=sourceurl)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def get_operation_seq(self, appid):
        res = yield self._mock_api_call(self._get_operation_seq, appid)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def presend_multi_message(self, appid, appmsgid, times):
        res = yield self._mock_api_call(self._presend_multi_message, appid, appmsgid=appmsgid, times=times)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def send_multi_message(self, appid, appmsgid, operation_seq, groupid):
        res = yield self._mock_api_call(self._send_multi_message, appid, appmsgid=appmsgid, operation_seq=operation_seq,
                                        groupid=groupid)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def get_latest_news(self, appid):
        res = yield self._mock_api_call(self._get_latest_news, appid)
        raise tornado.gen.Return(res)

mock_browser = MockBrowser()
