# -*- coding: utf-8 -*-

code_map = {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR'),
    1001: ('WECHATERR', u'wechat通讯错误'),
    1002: ('NOTWECHAT', u'wechat签名错误'),
    3001: ('NOTENOUGH', u'用户余额不足'),
    3101: ('ORDERPAID', u'商户订单已支付'),
    3102: ('ORDERCLOSED', u'订单已关闭'),
    3103: ('OUT_TRADE_NO_USED', u'商户订单号重复'),
    3201: ('APPID_NOT_EXIST', u'APPID不存在'),
    8001: ('SIGNERROR', u'签名错误'),
    8002: ('NOSIGN', u'找不到授权签名'),
    9001: ('UNKNOWN', u'其他错误'),
    9002: ('NETWORKERROR', u'网络请求失败')
}

simple_map = {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR')
}

alias_map = {
    'SUCCESS': 0,
    'FAIL': 1,
    'NOTENOUGH': 3001,
    'ORDERPAID': 3101,
    'ORDERCLOSED': 3102,
    'SYSTEMERROR': 1001,
    'APPID_NOT_EXIST': 3201,
    'OUT_TRADE_NO_USED': 3103
}
