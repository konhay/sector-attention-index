CREATE TABLE `bk_info` (
  `bk_code` varchar(10) NOT NULL,
  `bk_name` varchar(20) DEFAULT NULL,
  `bk_source` varchar(10) DEFAULT NULL,
  `bk_type` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `use_flag` int NOT NULL,
  `data_date` varchar(8) NOT NULL,
  PRIMARY KEY (`bk_code`,`data_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COMMENT='板块列表';
