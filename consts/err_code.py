# -*- coding: utf-8 -*-
from collections import defaultdict

code_map = defaultdict(lambda: ('FAIL', 'ERROR'), {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR'),
    1001: ('SYSTEMERROR', u'wechat通讯错误'),
    1002: ('NOTWECHAT', u'wechat签名错误'),
    3001: ('NOTENOUGH', u'用户余额不足'),
    3101: ('ORDERPAID', u'商户订单已支付'),
    3102: ('ORDERCLOSED', u'订单已关闭'),
    3103: ('OUT_TRADE_NO_USED', u'商户订单号重复'),
    3104: ('ORDERNOTEXIST', u'此交易订单号不存在'),
    3201: ('APPID_NOT_EXIST', u'APPID不存在'),
    3301: ('TRANSACTION_ID_INVALID', u'订单号非法'),
    8001: ('SIGNERROR', u'签名错误'),
    8002: ('NOSIGN', u'找不到授权签名'),
    9001: ('OTHERS', u'其他错误'),
    9002: ('NETWORKERROR', u'网络请求失败')
})

simple_map = defaultdict(lambda: ('FAIL', 'ERROR'), {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR')
})

alias_map = {v1: k for k, (v1, v2) in code_map.iteritems()}