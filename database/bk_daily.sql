CREATE TABLE `bk_daily` (
  `bk_code` varchar(10) NOT NULL COMMENT '板块代码',
  `trade_date` varchar(8) NOT NULL COMMENT '交易日期',
  `open` float DEFAULT NULL COMMENT '开盘价',
  `high` float DEFAULT NULL COMMENT '最高价',
  `low` float DEFAULT NULL COMMENT '最低价',
  `close` float DEFAULT NULL COMMENT '收盘价',
  `vol` float DEFAULT NULL COMMENT '成交量 （股）',
  `amount` float DEFAULT NULL COMMENT '成交额 （元）',
  PRIMARY KEY (`bk_code`,`trade_date`),
  KEY `bk_code_idx` (`bk_code`),
  KEY `trade_date_idx` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COMMENT='板块日线行情';
