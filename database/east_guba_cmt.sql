-- finance.east_guba_cmt definition

CREATE TABLE `east_guba_cmt` (
  `code` varchar(10) NOT NULL,
  `dtime` datetime NOT NULL,
  `title` varchar(100) NOT NULL,
  `author` varchar(20) NOT NULL,
  PRIMARY KEY (`code`,`dtime`,`title`,`author`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3 COMMENT='东财股吧评论';
