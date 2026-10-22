-- ============================================================
-- 充值活动业务 - 表结构定义
-- 数据库: yplay_act
-- ============================================================

-- 1. 活动配置表
CREATE TABLE `app_act_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_code` varchar(32) DEFAULT NULL COMMENT '活动编码',
  `activity_name` varchar(128) DEFAULT NULL COMMENT '活动名称',
  `begin_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `status` int DEFAULT NULL COMMENT '活动状态',
  `while_list` varchar(255) DEFAULT NULL COMMENT '用户白名单',
  `region` int DEFAULT NULL COMMENT '区域: 0-英语区 2-中东区',
  `award_distribute_type` int DEFAULT NULL COMMENT '奖励发放方式',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='活动相关配置';

-- 2. 活动奖励配置表
CREATE TABLE `app_act_award_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_code` varchar(32) DEFAULT NULL COMMENT '活动编码',
  `region` int DEFAULT NULL COMMENT '奖励区域 0-英语区 2-中东区',
  `type` int DEFAULT NULL COMMENT '奖励类型',
  `tier` int DEFAULT '0' COMMENT '档位(充值金额)',
  `prize_type` int DEFAULT NULL COMMENT '奖品类型',
  `prize_id` int DEFAULT NULL COMMENT '奖品id',
  `amount` int DEFAULT NULL COMMENT '奖品数量',
  `status` int DEFAULT '1' COMMENT '0-无效 1-有效',
  `distribute_type` int DEFAULT NULL COMMENT '发放方式 0-自动 1-手动',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`id`),
  KEY `idx_region_type` (`type`,`tier`,`region`) USING BTREE,
  KEY `idx_activity` (`activity_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='活动奖励配置';

-- 3. 用户活动奖励记录表
CREATE TABLE `app_act_user_award_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `activity_code` varchar(32) COMMENT '活动编码',
  `user_id` bigint DEFAULT NULL COMMENT '用户id',
  `award_type` int DEFAULT NULL COMMENT '奖励类型',
  `tier` int DEFAULT NULL COMMENT '档位值',
  `region` int DEFAULT NULL COMMENT '地区',
  `award_date` varchar(255) DEFAULT NULL COMMENT '奖励日期',
  `distribute_type` int DEFAULT NULL COMMENT '发放方式',
  `receive_status` int DEFAULT NULL COMMENT '领取状态',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime DEFAULT NULL COMMENT '发放时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '操作人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user_reward` (`user_id`,`award_type`,`tier`,`award_date`,`region`),
  KEY `idx_activity` (`activity_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户活动奖励记录';

-- 4. 用户活动奖励详情表
CREATE TABLE `app_act_user_award_record_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `activity_code` varchar(32) COMMENT '活动编码',
  `user_id` bigint DEFAULT NULL COMMENT '用户id',
  `award_type` int DEFAULT NULL COMMENT '奖励类型',
  `award_date` varchar(255) DEFAULT NULL COMMENT '奖励周期',
  `tier` int DEFAULT NULL COMMENT '档位值',
  `region` int DEFAULT NULL COMMENT '地区',
  `prize_type` int DEFAULT NULL COMMENT '奖品类型',
  `prize_id` int DEFAULT NULL COMMENT '奖励id',
  `amount` int DEFAULT NULL COMMENT '奖励数量',
  `distribute_type` int DEFAULT NULL COMMENT '发放方式',
  `receive_status` int DEFAULT NULL COMMENT '领取状态',
  `create_time` datetime DEFAULT NULL COMMENT '领取时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_activity_user_reward` (`activity_code`,`user_id`,`award_type`,`award_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户活动奖励详情';

-- 5. 榜单数据表
CREATE TABLE `app_act_rank_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `activity_code` varchar(32) DEFAULT NULL COMMENT '活动编码',
  `rank_type` int DEFAULT NULL COMMENT '榜单类型',
  `user_id` bigint DEFAULT NULL COMMENT '用户id',
  `region` int DEFAULT NULL COMMENT '地区',
  `score` double DEFAULT NULL COMMENT '榜单分数',
  `source_type` varchar(32) DEFAULT NULL COMMENT '分数来源',
  `create_time` datetime DEFAULT NULL COMMENT '时间',
  PRIMARY KEY (`id`),
  KEY `idx_activity_user_rank` (`activity_code`,`user_id`,`rank_type`,`region`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='榜单数据';
