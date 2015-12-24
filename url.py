# -*- coding: utf-8 -*-

# mch api
mch_api_base = "https://api.mch.weixin.qq.com"

mch_order_add = mch_api_base + "/pay/unifiedorder"

mch_order_query = mch_api_base + "/pay/orderquery"

# wechat api
wechat_api_base = "https://api.weixin.qq.com"

wechat_basic_access_token = wechat_api_base + "/cgi-bin/token"

wechat_basic_userinfo = wechat_api_base + "/cgi-bin/user/info"

wechat_oauth_access_token = wechat_api_base + "/sns/oauth2/access_token"

wechat_oauth_userinfo = wechat_api_base + "/sns/userinfo"

# mp website
mp_base = 'https://mp.weixin.qq.com'

mp_home = mp_base + '/cgi-bin/home'

mp_login = mp_base + '/cgi-bin/login'

mp_singlesend = mp_base + '/cgi-bin/singlesend'

mp_singlesend_page = mp_base + '/cgi-bin/singlesendpage'

mp_multisend = mp_base + '/cgi-bin/masssend'

mp_multisend_page = mp_base + '/cgi-bin/masssendpage'

mp_appmsg = mp_base + '/cgi-bin/appmsg'

mp_upload = mp_base + '/cgi-bin/filetransfer'

mp_save_news = mp_base + '/cgi-bin/operate_appmsg'

mp_message = mp_base + '/cgi-bin/message'

mp_contact_info = mp_base + '/cgi-bin/getcontactinfo'
