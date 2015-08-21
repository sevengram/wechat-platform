# -*- coding: utf-8 -*-

from collections import defaultdict

err_map = defaultdict(lambda: ('FAIL', 'ERROR'), {
    0: ('SUCCESS', 'OK'),
    1: ('FAIL', 'ERROR'),
    1001: ('SYSTEMERROR', u'wechat通讯错误'),
    1002: ('NOTWECHAT', u'wechat签名错误'),
    1003: ('ACCESS_ERROR', u'获取access_token时AppSecret错误，或者access_token无效'),
    1004: ('TOKEN_ERROR', u'不合法的access_token'),
    1101: ('API_NOT_AUTH', u'api功能未授权'),
    2001: ('INVALIDCODE', u'不合法的oauth_code'),
    2002: ('USERNOTEXIST', u'用户不存在'),
    3001: ('NOTENOUGH', u'用户余额不足'),
    3101: ('ORDERPAID', u'商户订单已支付'),
    3102: ('ORDERCLOSED', u'订单已关闭'),
    3103: ('OUT_TRADE_NO_USED', u'商户订单号重复'),
    3104: ('ORDERNOTEXIST', u'此交易订单号不存在'),
    3201: ('APPID_NOT_EXIST', u'APPID不存在'),
    3301: ('TRANSACTION_ID_INVALID', u'订单号非法'),
    4101: ('INVALID_MSG_TYPE', u'msg_type不合法'),
    7000: ('MOCK_HTTP_ERROR', u'wechat模拟访问错误'),
    7001: ('MOCK_LOGIN_EXPIRED', u'wechat模拟登录超时'),
    7002: ('MOCK_LOGIN_ERROR', u'wechat模拟登录请求错误'),
    7101: ('MOCK_USER_NOTFOUND', u'wechat模拟访问无法找到用户'),
    7102: ('MOCK_FAKEID_NOT_FOUND', u'wechat模拟访问fakeid未找到'),
    7103: ('MOCK_TICKET_NOTFOUND', u'wechat模拟访问ticket未找到'),
    8001: ('SIGNERROR', u'签名错误'),
    8002: ('NOSIGN', u'找不到授权签名'),
    9001: ('OTHERS', u'其他错误'),
    9002: ('NETWORK_ERROR', u'网络请求失败'),
    9003: ('NETWORK_DATA_ERROR', u'网络数据错误'),
    9101: ('JSON_ERROR', u'JSON数据格式错误')
})

alias_map = {v1: k for k, (v1, v2) in err_map.iteritems()}

wechat_map = defaultdict(lambda: (9001, '请求失败'), {
    -1: (1001, '系统繁忙，此时请开发者稍候再试'),
    0: (0, '请求成功'),
    40001: (1003, '获取access_token时AppSecret错误, 或者access_token无效'),
    40002: (9001, '不合法的凭证类型'),
    40003: (9001, '不合法的OpenID，请开发者确认OpenID(该用户)是否已关注公众号, 或是否是其他公众号的OpenID'),
    40004: (9001, '不合法的媒体文件类型'),
    40005: (9001, '不合法的文件类型'),
    40006: (9001, '不合法的文件大小'),
    40007: (9001, '不合法的媒体文件id'),
    40008: (9001, '不合法的消息类型'),
    40009: (9001, '不合法的图片文件大小'),
    40010: (9001, '不合法的语音文件大小'),
    40011: (9001, '不合法的视频文件大小'),
    40012: (9001, '不合法的缩略图文件大小'),
    40013: (9001, '不合法的AppID'),
    40014: (1004, '不合法的access_token, 请开发者认真比对access_token的有效性, 或查看是否正在为恰当的公众号调用接口'),
    40015: (9001, '不合法的菜单类型'),
    40016: (9001, '不合法的按钮个数'),
    40017: (9001, '不合法的按钮个数'),
    40018: (9001, '不合法的按钮名字长度'),
    40019: (9001, '不合法的按钮KEY长度'),
    40020: (9001, '不合法的按钮URL长度'),
    40021: (9001, '不合法的菜单版本号'),
    40022: (9001, '不合法的子菜单级数'),
    40023: (9001, '不合法的子菜单按钮个数'),
    40024: (9001, '不合法的子菜单按钮类型'),
    40025: (9001, '不合法的子菜单按钮名字长度'),
    40026: (9001, '不合法的子菜单按钮KEY长度'),
    40027: (9001, '不合法的子菜单按钮URL长度'),
    40028: (9001, '不合法的自定义菜单使用用户'),
    40029: (2001, '不合法的oauth_code'),
    40030: (9001, '不合法的refresh_token'),
    40031: (9001, '不合法的openid列表'),
    40032: (9001, '不合法的openid列表长度'),
    40033: (9001, '不合法的请求字符, 不能包含\uxxxx格式的字符'),
    40035: (9001, '不合法的参数'),
    40038: (9001, '不合法的请求格式'),
    40039: (9001, '不合法的URL长度'),
    40050: (9001, '不合法的分组id'),
    40051: (9001, '分组名字不合法'),
    40125: (1003, '获取access_token时AppSecret错误, 或者access_token无效'),
    41001: (9001, '缺少access_token参数'),
    41002: (9001, '缺少appid参数'),
    41003: (9001, '缺少refresh_token参数'),
    41004: (9001, '缺少secret参数'),
    41005: (9001, '缺少多媒体文件数据'),
    41006: (9001, '缺少media_id参数'),
    41007: (9001, '缺少子菜单数据'),
    41008: (9001, '缺少oauth code'),
    41009: (9001, '缺少openid'),
    42001: (1004, 'access_token超时, 请检查access_token的有效期'),
    42002: (9001, 'refresh_token超时'),
    42003: (9001, 'oauth_code超时'),
    43001: (9001, '需要GET请求'),
    43002: (9001, '需要POST请求'),
    43003: (9001, '需要HTTPS请求'),
    43004: (9001, '需要接收者关注'),
    43005: (9001, '需要好友关系'),
    44001: (9001, '多媒体文件为空'),
    44002: (9001, 'POST的数据包为空'),
    44003: (9001, '图文消息内容为空'),
    44004: (9001, '文本消息内容为空'),
    45001: (9001, '多媒体文件大小超过限制'),
    45002: (9001, '消息内容超过限制'),
    45003: (9001, '标题字段超过限制'),
    45004: (9001, '描述字段超过限制'),
    45005: (9001, '链接字段超过限制'),
    45006: (9001, '图片链接字段超过限制'),
    45007: (9001, '语音播放时间超过限制'),
    45008: (9001, '图文消息超过限制'),
    45009: (9001, '接口调用超过限制'),
    45010: (9001, '创建菜单个数超过限制'),
    45015: (9001, '回复时间超过限制'),
    45016: (9001, '系统分组, 不允许修改'),
    45017: (9001, '分组名字过长'),
    45018: (9001, '分组数量超过上限'),
    46001: (9001, '不存在媒体数据'),
    46002: (9001, '不存在的菜单版本'),
    46003: (9001, '不存在的菜单数据'),
    46004: (9001, '不存在的用户'),
    47001: (9001, '解析JSON/XML内容错误'),
    48001: (1101, 'api功能未授权, 请确认公众号已获得该接口'),
    50001: (9001, '用户未授权该api'),
    61451: (9001, '参数错误(invalid parameter)'),
    61452: (9001, '无效客服账号(invalid kf_account)'),
    61453: (9001, '客服帐号已存在(kf_account exsited)'),
    61454: (9001, '客服帐号名长度超过限制(仅允许10个英文字符, 不包括@及@后的公众号的微信号)(invalid kf_acount length)'),
    61455: (9001, '客服帐号名包含非法字符(仅允许英文+数字)(illegal character in kf_account)'),
    61456: (9001, '客服帐号个数超过限制(10个客服账号)(kf_account count exceeded)'),
    61457: (9001, '无效头像文件类型(invalid file type)'),
    61450: (9001, '系统错误(system error)')
})
