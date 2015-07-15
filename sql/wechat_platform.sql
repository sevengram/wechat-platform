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

insert into `wechat_app_info`(`id`,`appid`,`appname`,`secret`,`wechat_no`,`openid`,`apptype`,`is_verified`,`is_merchant`,`fakeid`,`qrdecode`,`mp_username`,`mp_pwd`,`bizuin`,`data_bizuin`,`mch_id`,`apikey`,`siteid`,`ctime`,`status`) values
(1,'wx7394ce44a23b3225','牛掰服务号','7beb21d84d4505815eb6165568b7a328','newbuy88','gh_a8ea1622fe55','2','1','1','3016030242','9EgkPB7EBUN6rVpf9x3m','maywang@newbuy.cn','fc014b5f9e6ba45e06d4d60f1e2d48cc','3016030242','2392508399','10010984','fc014b5f9e6ba45e06d4d60f1e2d48cc','newbuy','2015-01-14 10:18:34','1'),
(2,'wx3a62f5a28273adb1','牛掰订阅号','d464b949fd9c827e4e0e7a28489bd1eb','newbuy2014','gh_3e853803e6f5','1','1','0','2399397968','hnQ0LNnES4Q0rZ1P9yGU','2952168026@qq.com','fc014b5f9e6ba45e06d4d60f1e2d48cc','2399397968','3010027364',null,null,'newbuy','2015-01-22 12:47:09','1'),
(3,'wx50f1fdd1dddebf1e','彩象彩票','eca55557b39337d364814456a8f28e91','xiangyatou888','gh_c008a36d9e93','2','1','0','3082785204','YkxNVWXElzjorSE29xlw','1516354524@qq.com','5416d7cd6ef195a0f7622a9c56b55e84','3082785204','3078782002',null,null,'lottery','2015-01-22 17:35:13','1'),
(4,'wx8cabe7121f5369a3','米嘟嘟','6066d7e2e03fbb351a9a4602f07a3a94','iMidudu','gh_e558d76a7783','2','1','1','3017206179','dUg1LQzEhFH7rUhO9x1n','meduo@meduo.com.cn','3bd17e86f8aaddc2f7168dfaae4c22fd','3017206179','3002205880','1230283802',null,'meduo','2015-02-05 21:46:24','1'),
(5,'wxfc87c2547449c2c6','邻家天文馆','58dd710662bbd6b559374a234c67266e','sevengram','gh_d188e2888313','1','0','0','2391209664','FnUqMlzE2gGlrRhR9yAE','sevengram@163.com','cbe34b794cc95deb3e5b5d390efb74d7','2391209664','2393201154',null,null,'deepsky','2015-02-05 21:55:55','1');

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

insert into `wechat_user_info`(`uid`,`appid`,`openid`,`unionid`,`fakeid`,`nickname`,`subscribe`,`sex`,`city`,`province`,`country`,`lang`,`headimgurl`,`subscribe_time`,`ctime`) values
('1','wx8cabe7121f5369a3','oo-nWs9iARHWVo1Y8uECVwWFGjyw','orKOtuEXjD-sYfLPwZvf0cxMm9vw',null,'fjx','1','1','杨浦','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/oj991s4Obibog8HEliaxTt0mqjm5j1vicWNMXibo3GcLbwZjXuJQpNjAaZXV0szcCYw4M31t7YeHJWg1Hp75Gmm1Mx6QLCYBF7Bo/0','1425114970','2015-02-09 00:52:02'),
('2','wx8cabe7121f5369a3','oo-nWs8dK0uff_AGNQRApXyCbmwc',null,null,'沈越♋️','1','0','','','埃及','zh_CN','http://wx.qlogo.cn/mmopen/PiajxSqBRaELS0WGcX4MZF7VR0fgLMmTyNJmmO94SMLvtesV27HicGsa9571jLZLTsVYRYXwDb8O5aFic9MWjibhkA/0','1423406134','2015-02-08 22:24:55'),
('3','wx8cabe7121f5369a3','oo-nWs3qHnggJojc3hnnc6b24iEY','orKOtuOH0pTFVfFzeKw30EgOeAt0',null,'zenk','1','1','','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/oj991s4ObibqN701ZozRqdnd2nksm8bsxC0NqvQEDQmVVLdoWJDXquq3H4eqs5sZicSN9WFwKrqk1hS6IxJNSkjw/0','1425025895','2015-02-09 11:08:29'),
('4','wx8cabe7121f5369a3','oo-nWsyjl9NS-lFmA4hVa3wDExFQ','orKOtuFQ2WIbtFM3VC4NkjQK0G2U',null,'胡晓阳','1','1','西雅图','华盛顿','美国','en','http://wx.qlogo.cn/mmopen/8KTOLqTvvB4katVQQMj43x0oALMKmZnsYpwWTiaxH9eib1VxEgFASvPw69qianZkBA8ossAQTbhxgNFQfe4ffGXMdouzaNwhaXF/0','1423995434','2015-02-09 11:52:07'),
('5','wx8cabe7121f5369a3','oo-nWs4yl5C_P_7mNyvAdft71Fck',null,null,'倪晅','1','1','浦东新区','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/LPLYlyQ5GArglT5DMCTLFC7K2qGLSc7GABicicicrqs39WYEALLlYY45QcPkqc1R4sYHCZ6HGv39G8Cl8q0jWv3Cw/0','1423464299','2015-02-09 14:44:49'),
('6','wx8cabe7121f5369a3','oo-nWs8BdPXDWSKODck-1TtlMa3c','orKOtuBXHKfbk45KmXKuOTx_8ah8',null,'大猫',null,'1','静安','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/PiajxSqBRaEJEe2nukapRSDWP9bKOlcBibIWhAIMVYLbOKeIJ2aA61zVmoalLqQMLbtniaQ8icGyLiaCfnqDfVpUiaQg/0',null,'2015-02-09 17:40:53'),
('7','wx8cabe7121f5369a3','oo-nWs8z_1vP0gyZdbSC3QqzA_5o',null,null,'忆舒Kiki','1','2','普陀','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/PiajxSqBRaELDKMJVDeUAEO9xVLy1oAsiaN04SzxwoP5RcYIXyE2sd5ubcM1hh6LAM80uL1p9uiaJT074Muc8raww/0','1423796114','2015-02-13 10:55:15'),
('8','wx8cabe7121f5369a3','oo-nWs25aPLgc5pI0iN6SNuQLFN4',null,null,'查王平','1','1','浦东新区','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/LPLYlyQ5GApvpH9lkZMSMISyUoic9YyGwS6P9iaWaYUr6l69BLAkRibbnYDMElia8mV2sQNcQzg0Nrqmlv3LBCGAjnEsJZwY55Vc/0','1423796201','2015-02-13 10:56:41'),
('9','wx8cabe7121f5369a3','oo-nWs3meUO4Bu_zEWKoZYvpcr2g',null,null,'张波','1','1','伯尼港','塔斯马尼亚','澳大利亚','zh_CN','http://wx.qlogo.cn/mmopen/8KTOLqTvvB6ReDPOF2JzANOEreHwb0eMf3Zn3cGC2AEL8UU1c2RG7a2OYe1jSsTUAfzHU3CTklpt4vWqXTrVphCeFbnMI5eD/0','1423821115','2015-02-13 17:51:56'),
('10','wx8cabe7121f5369a3','oo-nWs7-AJqOMZfmX_K2dL6ayHwE','orKOtuDlExEan8GeYSD3gPr2GgvI',null,'',null,'2','','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/ajNVdqHZLLDQiaHunG9Tj6MUnmYKSz1gQLfrleXxEkXcb7NbII1CmJBIbrZDpUkZWhdot5g1VftKT5cuz6aZpnA/0',null,'2015-02-16 09:51:38'),
('11','wx8cabe7121f5369a3','oo-nWs1PXLiFOdgmOI9A7PeB1qkI','orKOtuG-bZatmLdCClKP6uZv1loo',null,'安',null,'2','','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/ajNVdqHZLLAzRFuATOsdMdHP51xgLWQeAX8Gic0lS9KmN74oJM3YrHH1R4ibokVGjUMjUJnpIuyzGJthDpqyBh6w/0',null,'2015-02-16 11:22:32'),
('12','wx8cabe7121f5369a3','oo-nWsxMW5LCDPiwccn8m8JMdFNM','orKOtuJaOnD7c0msUfM4bwR44z1c',null,'GARY WU',null,'1','静安','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/ajNVdqHZLLBc9n8N8GbysWCtGGN6zibTuQ7ZygDibm8gV2XvyBnwuR18QtETCxbSkzTxztjJbgw975rnu7hpnrMg/0',null,'2015-02-16 16:41:03'),
('13','wx8cabe7121f5369a3','oo-nWswKZBcoPQ41Ci93KqYPD2yM','orKOtuA8O3qNvRDqvY8ye8F9lrBw',null,'徐小云',null,'2','静安','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/oj991s4Obibog8HEliaxTt0u6LI2aIqXjcMChy6atXHvibsAqme8ZbVustP08dUibGcEOM3U2WyIvg8FIu2CTyGH8E5cL8GsxErq/0',null,'2015-02-16 16:45:56'),
('14','wx8cabe7121f5369a3','oo-nWs66L9j692wcHodYFq45YF0Y','orKOtuLeCKo0mqqoMLPSlR5J1XCI',null,'Faye Shen',null,'2','静安','上海','中国','zh_CN','http://wx.qlogo.cn/mmopen/ajNVdqHZLLBvSiao3Sbz9EP47icNNp7iaA8adibKYmic8NIiaYdAwpapLh6Wom1FZ3hnHvSiaNaKrxMj9gJjpgeaWsTGQ/0',null,'2015-02-18 02:10:38'),
('15','wx8cabe7121f5369a3','oo-nWsweTfEAQhnswk8hvL87yXpc','orKOtuIGBk-YdIj2nkCx75criFKU',null,'采蘑菇的马里奥','1','2','西城','北京','中国','zh_CN','http://wx.qlogo.cn/mmopen/oj991s4Obibog8HEliaxTt0sqn4tubhysotUY6mVsLOeA8kna6wjP84GkKCrkdnvlAH0Q3NPPqTQVGQ5pOpICYbjsAI58Bq5lg/0','1424666315','2015-02-23 12:38:36');

SET FOREIGN_KEY_CHECKS = 1;
