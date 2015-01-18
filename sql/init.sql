CREATE TABLE `site_info` (
  `siteid` char(32) NOT NULL PRIMARY KEY,
  `sitekey` char(128) NOT NULL,
  `pay_notify_url` char(255),
  `msg_notify_url` char(255),
  `utime` bigint NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint NOT NULL DEFAULT 1
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `wechat_app_info` (
  `appid` char(32) NOT NULL NOT NULL PRIMARY KEY,
  `appname` char(128) NOT NULL,
  `secret` char(128) NOT NULL,
  `wechat_no` char(64) NOT NULL,
  `openid` char(64) NOT NULL,
  `apptype` tinyint NOT NULL,
  `is_verified` bool NOT NULL DEFAULT 0,
  `is_merchant` bool NOT NULL DEFAULT 0,
  `fakeid` char(32),
  `qrdecode` char(32),
  `mp_username` char(128),
  `mp_pwd` char(128),
  `bizuin` char(32),
  `data_bizuin` char(32),
  `mch_id` char(32),
  `apikey` char(128),
  `pay_username` char(128),
  `pay_pwd` char(128),
  `utime` bigint NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint NOT NULL DEFAULT 1,
  KEY `index_mchid` (`mchid`),
  KEY `index_openid` (`openid`),
  KEY `wechat_no` (`wechat_no`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `site_app_hooks` (
  `appid` char(32) NOT NULL,
  `siteid` char(32) NOT NULL,
  `utime` bigint NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint NOT NULL DEFAULT 1,
  PRIMARY KEY  (`appid`,`siteid`),
  KEY `index_siteid` (`siteid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `wechat_user_info` (
  `uid` char(128) NOT NULL PRIMARY KEY,
  `appid` char(32) NOT NULL,
  `openid` char(64) NOT NULL,
  `unionid` char(64),
  `fakeid` char(32),
  `nickname` char(128),
  `subscribe` tinyint,
  `sex` tinyint,
  `city` char(16),
  `province` char(16),
  `country` char(16),
  `lang` char(8),
  `headimgurl` char(255),
  `subscribe_time` bigint,
  `utime` bigint NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `index_appid_openid` (`appid`,`openid`),
  KEY `index_openid` (`openid`),
  KEY `index_unionid` (`unionid`),
  KEY `index_fakeid` (`fakeid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
