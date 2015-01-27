CREATE TABLE `site_info` (
  `siteid` char(32) NOT NULL,
  `sitekey` char(128) NOT NULL,
  `pay_notify_url` char(255) DEFAULT NULL,
  `msg_notify_url` char(255) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`siteid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `wechat_app_info` (
  `appid` char(32) NOT NULL,
  `appname` char(128) NOT NULL,
  `secret` char(128) NOT NULL,
  `wechat_no` char(64) NOT NULL,
  `openid` char(64) NOT NULL,
  `apptype` tinyint(4) NOT NULL,
  `is_verified` tinyint(1) NOT NULL DEFAULT '0',
  `is_merchant` tinyint(1) NOT NULL DEFAULT '0',
  `fakeid` char(32) DEFAULT NULL,
  `qrdecode` char(32) DEFAULT NULL,
  `mp_username` char(128) DEFAULT NULL,
  `mp_pwd` char(128) DEFAULT NULL,
  `bizuin` char(32) DEFAULT NULL,
  `data_bizuin` char(32) DEFAULT NULL,
  `mch_id` char(32) DEFAULT NULL,
  `apikey` char(128) DEFAULT NULL,
  `siteid` char(32) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`appid`),
  KEY `index_mchid` (`mch_id`),
  KEY `index_openid` (`openid`),
  KEY `wechat_no` (`wechat_no`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `wechat_user_info` (
  `uid` char(128) NOT NULL,
  `appid` char(32) NOT NULL,
  `openid` char(64) NOT NULL,
  `unionid` char(64) DEFAULT NULL,
  `fakeid` char(32) DEFAULT NULL,
  `nickname` char(128) DEFAULT NULL,
  `subscribe` tinyint(4) DEFAULT NULL,
  `sex` tinyint(4) DEFAULT NULL,
  `city` char(16) DEFAULT NULL,
  `province` char(16) DEFAULT NULL,
  `country` char(16) DEFAULT NULL,
  `lang` char(8) DEFAULT NULL,
  `headimgurl` char(255) DEFAULT NULL,
  `subscribe_time` bigint(20) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `index_appid_openid` (`appid`,`openid`),
  KEY `index_openid` (`openid`),
  KEY `index_unionid` (`unionid`),
  KEY `index_fakeid` (`fakeid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `wechat_app_token` (
  `appid` char(32) NOT NULL,
  `access_token` varchar(512) DEFAULT NULL,
  `expires_in` int(11) DEFAULT NULL,
  `access_token_utime` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`appid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;