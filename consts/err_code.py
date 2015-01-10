# -*- coding: utf-8 -*-

code_map = {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR'),
    1001: ('WECHATERR', 'wechat通讯错误'),
    1002: ('NOTWECHAT', 'wechat签名错误'),
    3001: ('NOTENOUGH', '用户余额不足'),
    3101: ('ORDERPAID', '商户订单已支付'),
    3102: ('ORDERCLOSED', '订单已关闭'),
    3103: ('OUT_TRADE_NO_USED', '商户订单号重复'),
    3201: ('APPID_NOT_EXIST', 'APPID不存在'),
    8001: ('SIGNERROR', '签名错误'),
    9001: ('UNKNOWN', '其他错误')
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
