# -*- coding: utf-8 -*-

import hashlib

newbuy_apikey = hashlib.md5('niubai2014').hexdigest()  # TODO: apikey from db
magento_sitekey = hashlib.md5('newbuy_magento').hexdigest()  # TODO: sitekey from db