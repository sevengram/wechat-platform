# -*- coding:utf8 -*-

import urlparse
import urllib
import tornado.gen
import tornado.httpclient
import tornado.httputil
import json
import Cookie
import time
import sys
import random
import mimetypes

from bs4 import BeautifulSoup

base_url = 'https://mp.weixin.qq.com/'

home_url = base_url + 'cgi-bin/home'

login_url = base_url + 'cgi-bin/login'

send_url = base_url + 'cgi-bin/singlesend'

message_url = base_url + 'cgi-bin/message'

send_page_url = base_url + 'cgi-bin/singlesendpage'

appmsg_url = base_url + 'cgi-bin/appmsg'

upload_url = base_url + 'cgi-bin/filetransfer'

save_material_url = base_url + 'cgi-bin/operate_appmsg'

multisend_page_url = base_url + 'cgi-bin/masssendpage'

multisend_url = base_url + 'cgi-bin/masssend'

common_headers = tornado.httputil.HTTPHeaders(
    {
        "Connection": "keep-alive",
        "Origin": base_url,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/36.0.1985.143 Safari/537.36",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "zh-CN,zh;q=0.8"
    })


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def encode_multipart_formdata(fields, files):
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    crlf = '\r\n'
    l = []
    for (key, value) in fields:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % key)
        l.append('')
        l.append(value)
    for (key, filename, value) in files:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"; filename="%s"' %
                 (key, filename.split('/')[-1]))
        l.append('Content-Type: %s' % get_content_type(filename))
        l.append('')
        l.append(value)
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body


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


class CookieManager(object):
    def __init__(self):
        self.cookie = None
        self.clear()

    def is_empty(self):
        return self.cookie.get('slave_sid', '') == '' or self.cookie.get('data_ticket', '') == ''

    def clear(self):
        self.cookie = {'data_bizuin': '2393201154', 'slave_user': 'gh_d188e2888313',
                       'bizuin': '2391209664'}

    def build(self):
        return ';'.join(['%s=%s' % (key, value) for key, value in self.cookie.items()])

    def set_cookie(self, headers):
        for sc in headers.get_list("Set-Cookie"):
            c = Cookie.SimpleCookie(sc)
            for morsel in c.values():
                if morsel.key not in ['data_bizuin', 'slave_user', 'bizuin']:
                    if morsel.value and morsel.value != 'EXPIRED':
                        self.cookie[morsel.key] = morsel.value
                    else:
                        self.cookie.pop(morsel.key, None)
        print 'Cookie updated:', self.cookie


class WechatConnector(object):
    def __init__(self):
        self.token = ''
        self.last_login = 0
        self.cookie_manager = CookieManager()

    def has_login(self):
        return self.token and not self.cookie_manager.is_empty() and time.time() - self.last_login < 60 * 20

    @tornado.gen.coroutine
    def post_request(self, url, headers, data):
        client = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(
            url=url, method='POST', headers=headers, body=data, connect_timeout=60, request_timeout=60)
        res = yield client.fetch(req)
        if res.code == 200:
            self.cookie_manager.set_cookie(res.headers)
            data = json.loads(res.body, encoding='utf-8')
            raise tornado.gen.Return(data)
        else:
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def post_data(self, url, data, **kwargs):
        headers = common_headers.copy()
        headers.add('Cookie', self.cookie_manager.build())
        headers.add('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        headers.add('Accept', kwargs.get(
            'accept', 'application/json, text/javascript, */*; q=0.01'))
        headers.add('Referer', kwargs.get('referer', base_url))
        print 'Weixin POST url: %s\nheaders: %s\ndata: %s' % (url, headers, data)
        result = yield self.post_request(url, headers, urllib.urlencode(data))
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def post_formdata(self, url, content_type, data, **kwargs):
        headers = common_headers.copy()
        headers.add('Cookie', self.cookie_manager.build())
        headers.add('Accept', '*/*')
        headers.add('Accept-Encoding', 'gzip,deflate')
        headers.add('Content-Type', content_type)
        headers.add('Referer', kwargs.get('referer', base_url))
        print 'Weixin POST formdata url: %s\nheaders: %s' % (url, headers)
        result = yield self.post_request(url, headers, data)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get_request(self, url, data, **kwargs):
        headers = common_headers.copy()
        headers.add('Cookie', self.cookie_manager.build())
        headers.add(
            'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        headers.add('Referer', kwargs.get('referer', base_url))

        client = tornado.httpclient.AsyncHTTPClient()
        url += '?' + urllib.urlencode(data)
        print 'Wexin GET url: %s\nheaders: %s' % (url, headers)

        req = tornado.httpclient.HTTPRequest(
            url=url, method='GET', headers=headers, connect_timeout=60, request_timeout=60)
        res = yield client.fetch(req)
        if res.code == 200:
            self.cookie_manager.set_cookie(res.headers)
            raise tornado.gen.Return(res.body)
        else:
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def login(self, username, pwd):
        print 'try login...'
        result = yield self.post_data(login_url, {
            'username': username,
            'pwd': pwd,
            'f': 'json'})
        if result and result['base_resp']['ret'] == 0:
            self.last_login = time.time()
            self.token = dict(
                urlparse.parse_qsl(result['redirect_url']))['token']
            print 'login success, new token:', self.token
            raise tornado.gen.Return(self.token)
        else:
            print 'login failed'
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def find_user(self, timestamp, content, mtype, count, offset):
        referer = home_url + '?' + urllib.urlencode({
            't': 'home/index',
            'token': self.token,
            'lang': 'zh_CN'})
        result = yield self.get_request(message_url, {
            'count': count,
            'offset': offset,
            'day': 7,
            'token': self.token
        }, referer=referer)
        raw = BeautifulSoup(result)
        try:
            t = raw.find_all(
                'script', {'type': 'text/javascript', 'src': ''})[-1].text
            users = json.loads(
                t[t.index('['):t.rindex(']') + 1], encoding='utf-8')
        except (ValueError, IndexError):
            users = None

        if not users:
            try:
                if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
                    print 'find_user failed: login expired'
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            except AttributeError:
                pass
            print 'find_user failed'
            sys.stdout.flush()
            raise tornado.gen.Return({'err': 4, 'msg': 'fail to find user'})

        for i in range(0, len(users) - 1):
            if users[i]['date_time'] < timestamp:
                print 'find_user failed: no match 1'
                sys.stdout.flush()
                raise tornado.gen.Return({'err': 4, 'msg': 'fail to find user'})
            elif check_same(timestamp, content, mtype, users[i]):
                if not check_same(timestamp, content, mtype, users[i + 1]):
                    print 'find_user success: ', users[i]
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 0, 'msg': users[i]})
                else:
                    print 'find_user failed: no match 2'
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 4, 'msg': 'fail to find user'})
        res = yield self.find_user(timestamp, content, mtype, count, count + offset - 1)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def get_operation_seq(self):
        referer = home_url + '?' + urllib.urlencode({
            't': 'home/index',
            'token': self.token,
            'lang': 'zh_CN'})
        result = yield self.get_request(multisend_page_url, {
            't': 'mass/send',
            'lang': 'zh_CN',
            'token': self.token
        }, referer=referer)
        raw = BeautifulSoup(result)
        try:
            t = raw.find_all(
                'script', {'type': 'text/javascript', 'src': ''})[-1].text
            s = t[t.find('operation_seq'):].split(',')[0]
            seq = s[s.index('\"') + 1:s.rindex('\"')]
        except (ValueError, IndexError):
            seq = None

        if not seq:
            try:
                if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
                    print 'get_operation_seq failed: login expired'
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            except AttributeError:
                pass
            print 'get_operation_seq failed'
            sys.stdout.flush()
            raise tornado.gen.Return({'err': 10, 'msg': 'fail to get operation_seq'})

        print 'get_operation_seq success: ', seq
        sys.stdout.flush()
        raise tornado.gen.Return({'err': 0, 'msg': seq})

    @tornado.gen.coroutine
    def get_ticket(self):
        referer = appmsg_url + '?' + urllib.urlencode({
            'begin': 0,
            'count': 10,
            't': 'media/appmsg_list',
            'token': self.token,
            'type': '10',
            'action': 'list',
            'lang': 'zh_CN'})
        result = yield self.get_request(appmsg_url, {
            't': 'media/appmsg_edit',
            'action': 'edit',
            'type': '10',
            'isMul': 0,
            'isNew': 1,
            'lang': 'zh_CN',
            'token': self.token
        }, referer=referer)
        ticket = None
        raw = BeautifulSoup(result)
        try:
            ts = raw.find_all('script', {'type': 'text/javascript', 'src': ''})
            for t in ts:
                if t.text.strip(' \t\r\n').startswith('window.wx'):
                    i = t.text.find('ticket:')
                    ticket = t.text[i + 8:i + 48]
                    break
        except (ValueError, IndexError):
            ticket = None

        if not ticket:
            try:
                if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
                    print 'get_ticket failed: login expired'
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            except AttributeError:
                pass
            print 'get_ticket failed'
            sys.stdout.flush()
            raise tornado.gen.Return({'err': 7, 'msg': 'fail to get ticket'})

        print 'get_ticket success: ', ticket
        sys.stdout.flush()
        raise tornado.gen.Return({'err': 0, 'msg': ticket})

    @tornado.gen.coroutine
    def get_lastest_material(self, count, title):
        referer = home_url + '?' + urllib.urlencode({
            't': 'home/index',
            'token': self.token,
            'lang': 'zh_CN'})
        result = yield self.get_request(appmsg_url, {
            'begin': 0,
            'count': count,
            't': 'media/appmsg_list',
            'token': self.token,
            'type': '10',
            'action': 'list',
            'lang': 'zh_CN'
        }, referer=referer)
        raw = BeautifulSoup(result)
        itemid = None
        try:
            t = raw.find_all(
                'script', {'type': 'text/javascript', 'src': ''})[-1].text
            items = json.loads(t[t.index('{'):t.rindex('}') + 1], encoding='utf-8')
            for item in items['item']:
                if title == item['title']:
                    itemid = item['app_id']
                    break
        except (ValueError, IndexError):
            pass

        if not itemid:
            try:
                if raw.find('div', {'class': 'msg_content'}).text.strip().startswith(u'\u767b'):
                    print 'get_lastest_material failed: login expired'
                    sys.stdout.flush()
                    raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            except AttributeError:
                pass
            print 'get_lastest_material failed'
            sys.stdout.flush()
            raise tornado.gen.Return({'err': 9, 'msg': 'fail to match lastest material'})

        print 'get_lastest_material success: ', itemid
        sys.stdout.flush()
        raise tornado.gen.Return({'err': 0, 'msg': itemid})

    @tornado.gen.coroutine
    def upload_image(self, ticket, filename):
        url = upload_url + '?' + urllib.urlencode({
            'ticket_id': 'sevengram',
            'ticket': ticket,
            'f': 'json',
            'token': self.token,
            'lang': 'zh_CN',
            'action': 'upload_material'})
        referer = appmsg_url + '?' + urllib.urlencode({
            't': 'media/appmsg_edit',
            'action': 'edit',
            'type': '10',
            'isMul': 0,
            'isNew': 1,
            'lang': 'zh_CN',
            'token': self.token})
        content_type, data = encode_multipart_formdata(
            fields=[('Filename', filename.split('/')[-1]), (
                'folder', '/cgi-bin/uploads'), ('Upload', 'Submit Query')],
            files=[('file', filename, open(filename, 'rb').read())])
        result = yield self.post_formdata(url, content_type, data, referer=referer)
        print 'upload_image response:', result
        sys.stdout.flush()
        try:
            if result['base_resp']['ret'] == -3:
                raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            elif result['base_resp']['ret'] == 0:
                raise tornado.gen.Return({'err': 0, 'msg': result['content']})
            else:
                raise tornado.gen.Return({'err': 5, 'msg': result['base_resp']['err_msg']})
        except (KeyError, AttributeError, TypeError):
            raise tornado.gen.Return({'err': 5, 'msg': 'fail to post image'})

    @tornado.gen.coroutine
    def save_material(self, title, content, digest, author, fileid, sourceurl):
        url = save_material_url + '?' + urllib.urlencode({
            't': 'ajax-response',
            'sub': 'create',
            'type': '10',
            'token': self.token,
            'lang': 'zh_CN'})
        referer = appmsg_url + '?' + urllib.urlencode({
            't': 'media/appmsg_edit',
            'action': 'edit',
            'type': '10',
            'isMul': 0,
            'isNew': 1,
            'lang': 'zh_CN',
            'token': self.token})
        result = yield self.post_data(url, {
            'token': self.token,
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
        }, referer=referer, accept='text/html, */*; q=0.01')
        print 'save_material response:', result
        sys.stdout.flush()
        if result and result.get('ret') == '0':
            raise tornado.gen.Return({'err': 0, 'msg': 'ok'})
        elif result:
            raise tornado.gen.Return({'err': 8, 'msg': result.get('msg', 'fail to save material')})
        else:
            raise tornado.gen.Return({'err': 8, 'msg': 'fail to save material'})

    @tornado.gen.coroutine
    def send_text_message(self, fakeid, content):
        url = send_url + '?' + urllib.urlencode({
            't': 'ajax-response',
            'f': 'json',
            'token': self.token,
            'lang': 'zh_CN'})
        referer = send_page_url + '?' + urllib.urlencode({
            'tofakeid': fakeid,
            't': 'message/send',
            'action': 'index',
            'token': self.token,
            'lang': 'zh_CN'})
        result = yield self.post_data(url, {
            'token': self.token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': 1,
            'type': 1,
            'content': content.encode('utf-8'),
            'tofakeid': fakeid,
            'random': random.random()
        }, referer=referer)
        print 'send_text_message response:', result
        sys.stdout.flush()
        try:
            if result and result['base_resp']['ret'] == -3:
                raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
            elif result and result['base_resp']['ret'] == 0:
                raise tornado.gen.Return({'err': 0, 'msg': result['base_resp']['err_msg']})
            else:
                raise tornado.gen.Return({'err': 5, 'msg': result['base_resp']['err_msg']})
        except (KeyError, AttributeError, TypeError):
            raise tornado.gen.Return({'err': 5, 'msg': 'fail to send message'})

    @tornado.gen.coroutine
    def multi_send_message(self, operation_seq, appmsgid, groupid):
        url = multisend_url + '?' + urllib.urlencode({
            't': 'ajax-response',
            'token': self.token,
            'lang': 'zh_CN'})
        referer = multisend_page_url + '?' + urllib.urlencode({
            't': 'mass/send',
            'lang': 'zh_CN',
            'token': self.token})
        result = yield self.post_data(url, {
            'token': self.token,
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
            'imgcode': ''
        }, referer=referer)
        print 'multi_send_message response:', result
        sys.stdout.flush()
        if result and result.get('ret') == '-20000':
            raise tornado.gen.Return({'err': 6, 'msg': 'login expired'})
        elif result and result.get('ret') == '64004':
            raise tornado.gen.Return(
                {'err': 11, 'msg': result.get('msg', 'fail to send multi message')})
        elif result and result.get('ret') == '0':
            raise tornado.gen.Return({'err': 0, 'msg': 'ok'})
        else:
            raise tornado.gen.Return({'err': 12, 'msg': 'fail to send multi message'})
