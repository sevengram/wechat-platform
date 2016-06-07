SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS  `site_info`;
CREATE TABLE `site_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `siteid` char(32) NOT NULL,
  `sitekey` char(128) NOT NULL,
  `pay_notify_url` char(255) DEFAULT NULL,
  `msg_notify_url` char(255) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_SITE_INFO_SITEID` (`siteid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into `site_info`(`id`,`siteid`,`sitekey`,`pay_notify_url`,`msg_notify_url`,`ctime`,`status`) values
(1, 'newbuy','ff3b65b3fc87e887b705c5f78ee00469','http://m.newbuy.cn/newbuy/newbuy_order/index/wechatPayment','http://wechat.newbuy.cn/plugin/newbuy','2015-01-14 10:05:40','1'),
(2, 'meduo','ecf42d7f40480dffd3b9cc8f911552c9',null,'http://qr.meduo.com.cn/meduo/notify/messages','2015-02-04 10:40:10','1');

DROP TABLE IF EXISTS  `wechat_app_info`;
CREATE TABLE `wechat_app_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_WECHAT_APP_INFO_APPID` (`appid`),
  KEY `IDX_WECHAT_APP_INFO_MCH_ID` (`mch_id`),
  KEY `IDX_WECHAT_APP_INFO_OPENID` (`openid`),
  KEY `IDX_WECHAT_APP_INFO_WECHAT_NO` (`wechat_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS  `wechat_app_token`;
CREATE TABLE `wechat_app_token` (
  `id` int(11) NOT NULL,
  `appid` char(32) NOT NULL,
  `access_token` varchar(512) DEFAULT NULL,
  `expires_in` int(11) DEFAULT NULL,
  `access_token_utime` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_WECHAT_APP_TOKEN_APP_INFO_ID` FOREIGN KEY (`id`) REFERENCES `wechat_app_info` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY `UK_WECHAT_APP_TOKEN_APPID` (`appid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS  `wechat_user_info`;
CREATE TABLE `wechat_user_info` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
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
  UNIQUE KEY `UK_WECHAT_USER_INFO_APPID_OPENID` (`appid`,`openid`),
  KEY `IDX_WECHAT_USER_INFO_OPENID` (`openid`),
  KEY `IDX_WECHAT_USER_INFO_UNIONID` (`unionid`),
  KEY `IDX_WECHAT_USER_INFO_FAKEID` (`fakeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `wechat_app_info`
    ADD `is_encrypted` tinyint(4) DEFAULT 0;

ALTER TABLE `wechat_app_info`
    ADD `is_protected` tinyint(4) DEFAULT 0;

ALTER TABLE `wechat_app_info`
    ADD `encoding_key` char(128) DEFAULT NULL;

SET FOREIGN_KEY_CHECKS = 1;
