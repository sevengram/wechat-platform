# -*- coding:utf8 -*-

import sys
import hashlib
from collections import defaultdict

import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.curl_httpclient
import tornado.ioloop

from consts import reply
from util import xmltodict
from util import dtools


type_dict = defaultdict(lambda: ['default'], {
    'image': ['default'],
    'location': ['default'],
    'text': ['command', 'default'],
    'event': ['welcome']
})

#
# Process functions
#


@tornado.gen.coroutine
def process_default(request):
    content = request.get('Content')
    if content:
        message = reply.default_format % content
    else:
        message = reply.default_response
    raise tornado.gen.Return(
        dtools.text_response(request['FromUserName'], message, 'default'))


@tornado.gen.coroutine
def process_welcome(request):
    raise tornado.gen.Return(dtools.text_response(request['FromUserName'], reply.welcome_direction, 'welcome'))


@tornado.gen.coroutine
def process_command(request):
    cmd = request['Content']
    if cmd in reply.text_commands:
        cmd = reply.text_commands[cmd]
    if len(cmd) == 1 and '0' <= cmd <= '9':
        raise tornado.gen.Return(
            dtools.text_response(request['FromUserName'], reply.command_dicts[cmd], 'command'))
    else:
        raise tornado.gen.Return(None)


process_dict = {
    'command': process_command,
    'default': process_default,
    'welcome': process_welcome
}


class WechatMsgHandler(tornado.web.RequestHandler):
    def get(self):
        if self.check_signature():
            self.write(self.get_argument('echostr'))

    @tornado.gen.coroutine
    def post(self):
        req = xmltodict.parse(self.request.body)['xml']
        res = ''
        for p in type_dict.get(req.get('MsgType')):
            if p in process_dict:
                res = yield process_dict.get(p)(request=req)
                if res == 1:
                    self.finish()
                    sys.stdout.flush()
                    return
                elif res:
                    break
        sys.stdout.flush()
        self.write(res)
        self.finish()

    def check_signature(self):
        arr = ['ilovedeepsky', self.get_argument(
            'timestamp'), self.get_argument('nonce')]
        arr.sort()
        return hashlib.sha1(''.join(arr)).hexdigest() == self.get_argument('signature')
