# -*- coding:utf8 -*-

from collections import defaultdict

welcome_direction = u'''欢迎来到公众号! 在这里, 你可以/:?
如需详细帮助, 请回复对应数字.'''

default_format = u'''"%s"是神马?可以吃吗?/:,@@其实你想查
'''

default_response = u'''找不到相应的服务/:,@@其实你想查
'''

text_commands = {
    u'你好': '9',
    u'帮助': '9',
    u'怎么用': '9',
    'Help': '9',
    'help': '9',
    'hello': '9',
    'Hi': '9',
    'hi': '9',
}

command_dicts = defaultdict(lambda: u'找不到这个指令哦', {
    '1': u'Cmd1',
    '2': u'Cmd2',
    '3': u'Cmd3',
    '9': welcome_direction
})
