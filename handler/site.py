# -*- coding: utf-8 -*-

from consts.key import magento_sitekey
from handler.base import BaseHandler


class SiteHandler(BaseHandler):
    def get_check_key(self, refer_dict):
        return magento_sitekey  # TODO: from db