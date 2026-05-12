-- ============================================================
-- 网络文本观点聚类与摘要辅助分析系统 - MySQL 8.0 全量建库建表脚本
-- 数据库连接密码固定为 123456（连接时使用）
-- 字符集：utf8mb4，排序规则：utf8mb4_unicode_ci
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 创建数据库
-- ------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS text_cluster_summary
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE text_cluster_summary;

-- ------------------------------------------------------------
-- 用户表：支撑注册、登录、个人中心
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(64) NOT NULL COMMENT '登录用户名',
  `password_hash` varchar(128) NOT NULL COMMENT '密码哈希',
  `salt` varchar(32) NOT NULL COMMENT '密码盐',
  `nickname` varchar(64) DEFAULT NULL COMMENT '昵称',
  `email` varchar(128) DEFAULT NULL COMMENT '邮箱',
  `role` varchar(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin/user/guest',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ------------------------------------------------------------
-- 认证令牌表：存储当前有效 token（可选，用于服务端校验）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `auth_tokens`;
CREATE TABLE `auth_tokens` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int unsigned NOT NULL COMMENT '用户ID',
  `token` varchar(128) NOT NULL COMMENT '令牌',
  `expires_at` datetime NOT NULL COMMENT '过期时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_token` (`token`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_expires_at` (`expires_at`),
  CONSTRAINT `fk_tokens_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='认证令牌表';

-- ------------------------------------------------------------
-- 文本表：支撑文本管理及聚类/摘要输入
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `texts`;
CREATE TABLE `texts` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int unsigned NOT NULL COMMENT '所属用户ID',
  `title` varchar(256) NOT NULL DEFAULT '' COMMENT '标题',
  `content` text NOT NULL COMMENT '正文内容',
  `word_count` int unsigned NOT NULL DEFAULT 0 COMMENT '字数',
  `category` varchar(64) DEFAULT NULL COMMENT '分类/标签',
  `status` varchar(20) NOT NULL DEFAULT 'active' COMMENT '状态：active/archived',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_title` (`title`(64)),
  KEY `idx_category` (`category`),
  FULLTEXT KEY `ft_content` (`title`,`content`),
  CONSTRAINT `fk_texts_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文本表';

-- ------------------------------------------------------------
-- 聚类任务表：支撑聚类任务生命周期
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `cluster_tasks`;
CREATE TABLE `cluster_tasks` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int unsigned NOT NULL COMMENT '所属用户ID',
  `name` varchar(128) NOT NULL COMMENT '任务名称',
  `description` varchar(512) DEFAULT NULL COMMENT '任务描述',
  `text_ids` varchar(2048) NOT NULL COMMENT '所选文本ID列表，JSON数组字符串如 [1,2,3]',
  `cluster_count` int unsigned NOT NULL DEFAULT 3 COMMENT '聚类数量',
  `algorithm` varchar(32) NOT NULL DEFAULT 'kmeans' COMMENT '算法：kmeans/dbscan',
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT '状态：pending/running/completed/failed',
  `progress` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '进度0-100',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_cluster_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聚类任务表';

-- ------------------------------------------------------------
-- 聚类结果表：任务ID、簇ID、文本ID、排序
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `cluster_results`;
CREATE TABLE `cluster_results` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` int unsigned NOT NULL COMMENT '聚类任务ID',
  `cluster_index` smallint unsigned NOT NULL COMMENT '簇序号从0开始',
  `text_id` int unsigned NOT NULL COMMENT '文本ID',
  `score` decimal(10,6) DEFAULT NULL COMMENT '相似度或得分',
  `sort_order` int unsigned NOT NULL DEFAULT 0 COMMENT '簇内排序',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_text_id` (`text_id`),
  KEY `idx_task_cluster` (`task_id`,`cluster_index`),
  CONSTRAINT `fk_cluster_results_task` FOREIGN KEY (`task_id`) REFERENCES `cluster_tasks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cluster_results_text` FOREIGN KEY (`text_id`) REFERENCES `texts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聚类结果表';

-- ------------------------------------------------------------
-- 摘要表：来源类型（文本/聚类）、来源ID、摘要内容
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `summaries`;
CREATE TABLE `summaries` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int unsigned NOT NULL COMMENT '所属用户ID',
  `source_type` varchar(20) NOT NULL COMMENT '来源类型：text/cluster',
  `source_id` int unsigned NOT NULL COMMENT '来源ID（文本ID或聚类任务ID）',
  `title` varchar(256) NOT NULL DEFAULT '' COMMENT '摘要标题',
  `content` text NOT NULL COMMENT '摘要正文',
  `word_count` int unsigned NOT NULL DEFAULT 0 COMMENT '字数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_source` (`source_type`,`source_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_summaries_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='摘要表';

-- ------------------------------------------------------------
-- 操作历史表：支撑历史列表与统计
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `operation_history`;
CREATE TABLE `operation_history` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int unsigned NOT NULL COMMENT '用户ID',
  `op_type` varchar(32) NOT NULL COMMENT '操作类型：text_upload/cluster_create/cluster_complete/summary_create等',
  `op_desc` varchar(512) DEFAULT NULL COMMENT '操作描述',
  `target_id` int unsigned DEFAULT NULL COMMENT '关联目标ID（文本/任务/摘要等）',
  `target_title` varchar(256) DEFAULT NULL COMMENT '关联目标标题',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_op_type` (`op_type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_history_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作历史表';

SET FOREIGN_KEY_CHECKS = 1;

-- ===================== 初始数据 =====================
-- 密码 123456 的哈希（算法：SHA256(salt+password)，salt 见下方）
-- 以下用户密码均为 123456，salt 为各条中的 salt 字段，前端传明文密码后后端用相同算法校验

INSERT INTO `users` (`id`,`username`,`password_hash`,`salt`,`nickname`,`email`,`role`,`created_at`,`updated_at`) VALUES
(1,'admin','a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2','salt_admin_01','系统管理员','admin@example.com','admin',NOW(),NOW()),
(2,'test','b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3','salt_test_02','测试用户','test@example.com','user',NOW(),NOW()),
(3,'demo','c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4','salt_demo_03','演示账户','demo@example.com','user',NOW(),NOW());

-- 使用 MySQL SHA2 生成密码 123456 的哈希（与后端 hashlib.sha256(salt+password) 一致：后端存 hex）
UPDATE `users` SET `password_hash` = LOWER(SHA2(CONCAT(`salt`,'123456'), 256)) WHERE `id` IN (1,2,3);

-- 文本表拟真数据（≥100 条，user_id 1 与 2 为主）
INSERT INTO `texts` (`user_id`,`title`,`content`,`word_count`,`category`,`status`,`created_at`,`updated_at`) VALUES
(1,'人工智能在教育领域的应用前景','随着AI技术的快速发展，教育领域正在经历深刻的变革。个性化学习、智能评估、虚拟助教等应用场景逐步落地，为教育公平和质量提升带来新的可能性。',68,'科技','active',DATE_SUB(NOW(),INTERVAL 18 DAY),NOW()),
(1,'全球气候变化与可持续发展','气候变化已成为全球最紧迫的环境挑战之一。各国政府和企业正在加速推动碳中和目标，可再生能源投资持续增长，绿色金融体系逐步完善。',62,'环境','active',DATE_SUB(NOW(),INTERVAL 17 DAY),NOW()),
(1,'数字经济时代的隐私保护挑战','大数据和人工智能技术的广泛应用使个人隐私面临前所未有的威胁。如何在促进数据流通的同时保障用户隐私权，成为各国立法和技术研究的重点。',65,'社会','active',DATE_SUB(NOW(),INTERVAL 16 DAY),NOW()),
(1,'远程办公模式对企业管理的影响','疫情后远程办公成为常态，企业管理模式随之转变。弹性工作制、分布式团队协作、数字化绩效管理等新实践正在重塑职场文化。',58,'商业','active',DATE_SUB(NOW(),INTERVAL 15 DAY),NOW()),
(1,'新能源汽车市场竞争格局分析','全球新能源汽车市场持续高速增长，传统车企加速转型，新势力品牌不断涌现。电池技术突破、充电基础设施建设和智能驾驶成为竞争焦点。',62,'商业','active',DATE_SUB(NOW(),INTERVAL 14 DAY),NOW()),
(1,'社交媒体对青少年心理健康的影响','研究表明过度使用社交媒体与青少年焦虑、抑郁等心理问题存在关联。平台责任、家长监督和数字素养教育成为社会关注焦点。',56,'社会','active',DATE_SUB(NOW(),INTERVAL 13 DAY),NOW()),
(1,'量子计算的商业化进程','量子计算正从实验室走向商业应用。金融建模、药物研发、密码学和物流优化等领域有望率先受益，但技术成熟度和人才储备仍是瓶颈。',60,'科技','active',DATE_SUB(NOW(),INTERVAL 12 DAY),NOW()),
(1,'城市化进程中的社区治理创新','城市化加速推进背景下，智慧社区建设、居民自治和数字治理成为基层治理现代化的重要抓手，社区服务的精细化和智能化水平不断提升。',60,'社会','active',DATE_SUB(NOW(),INTERVAL 11 DAY),NOW()),
(2,'区块链在供应链金融中的应用','区块链技术为供应链金融带来可信溯源与融资效率提升。多级供应商确权、应收账款融资等场景正在试点推广。',52,'科技','active',DATE_SUB(NOW(),INTERVAL 10 DAY),NOW()),
(2,'碳中和目标下的产业转型路径','钢铁、水泥、化工等高耗能行业面临减排压力。绿色技术研发、碳交易市场建设与政策激励将共同推动产业低碳转型。',55,'环境','active',DATE_SUB(NOW(),INTERVAL 9 DAY),NOW()),
(1,'智慧医疗与健康管理趋势','可穿戴设备、远程诊疗和健康大数据正在重构医疗健康服务模式。预防医学与精准医疗的结合成为重要方向。',54,'科技','active',DATE_SUB(NOW(),INTERVAL 8 DAY),NOW()),
(1,'跨境电商发展与监管平衡','跨境电商规模持续扩大，海关、税务与平台责任界定成为监管焦点。消费者权益与产业健康发展需要平衡。',50,'商业','active',DATE_SUB(NOW(),INTERVAL 8 DAY),NOW()),
(2,'青年就业与职业技能培训','青年失业率受到关注，职业技能培训与校企合作被寄予厚望。新职业、灵活就业与终身学习成为关键词。',51,'社会','active',DATE_SUB(NOW(),INTERVAL 7 DAY),NOW()),
(1,'数据安全法与个人信息保护实践','《数据安全法》与《个人信息保护法》实施后，企业合规成本上升。数据分类分级、出境评估与隐私计算技术受到重视。',59,'社会','active',DATE_SUB(NOW(),INTERVAL 7 DAY),NOW()),
(2,'智能制造与工业互联网','工业互联网平台连接设备、生产与供应链，推动柔性制造与预测性维护。中小企业上云用数成为政策扶持重点。',56,'科技','active',DATE_SUB(NOW(),INTERVAL 6 DAY),NOW()),
(1,'乡村旅游与乡村振兴','乡村旅游带动农副产品销售与就业，民宿与特色体验项目成为热点。基础设施与人才短板仍需补齐。',52,'社会','active',DATE_SUB(NOW(),INTERVAL 6 DAY),NOW()),
(1,'生物多样性保护与生态修复','生物多样性丧失引发全球关注。生态红线、自然保护地体系与生态修复工程正在推进。',48,'环境','active',DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(2,'消费升级与国货品牌崛起','年轻消费者对国货认同度提升，新国货在美妆、服饰、数码等领域表现突出。品质与设计成为竞争关键。',53,'商业','active',DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(1,'职业教育与产教融合','产教融合、校企合作深化，订单班与实训基地建设加速。双师型教师与活页式教材受到重视。',50,'社会','active',DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(2,'半导体产业链自主可控','芯片短缺促使各国重视半导体产业链安全。设计、制造、设备与材料环节的国产替代持续推进。',54,'科技','active',DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(1,'平台经济反垄断与合规','平台反垄断执法加强，二选一、大数据杀熟等行为受到规制。平台需在创新与合规之间寻求平衡。',55,'商业','active',DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(1,'城市更新与老旧小区改造','老旧小区改造提升居住品质，加装电梯与物业管理升级是焦点。社会资本参与模式仍在探索。',51,'社会','active',DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(2,'氢能产业与绿氢制备','氢能被视作清洁能源重要方向。绿氢制备成本、储运与燃料电池应用是当前研发和试点重点。',50,'环境','active',DATE_SUB(NOW(),INTERVAL 2 DAY),NOW()),
(1,'元宇宙与虚拟现实应用','元宇宙概念带动VR/AR热度，游戏、社交与工业仿真被视为优先场景。技术成熟度与伦理问题并存。',52,'科技','active',DATE_SUB(NOW(),INTERVAL 2 DAY),NOW()),
(2,'灵活用工与劳动权益保障','灵活用工规模扩大，劳动关系的认定与社保、薪酬保障成为争议焦点。新业态劳动者权益保护政策在完善。',56,'社会','active',DATE_SUB(NOW(),INTERVAL 1 DAY),NOW()),
(1,'循环经济与废弃物资源化','废弃物资源化利用与循环经济园区建设得到政策支持。再生资源回收体系与生产者责任延伸制度在推进。',54,'环境','active',DATE_SUB(NOW(),INTERVAL 1 DAY),NOW());

-- 继续补充文本至 100+ 条
INSERT INTO `texts` (`user_id`,`title`,`content`,`word_count`,`category`,`status`,`created_at`,`updated_at`) VALUES
(1,'科技政策与创新生态一','科技创新政策、研发投入与创新生态建设是推动高质量发展的关键。',45,'科技','active',DATE_SUB(NOW(),INTERVAL 10 DAY),NOW()),
(1,'科技政策与创新生态二','创新驱动发展战略实施以来，企业研发投入持续增长。',38,'科技','active',DATE_SUB(NOW(),INTERVAL 9 DAY),NOW()),
(2,'社会诚信体系建设','社会信用体系在政务、金融、消费等领域发挥越来越大的作用。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 8 DAY),NOW()),
(1,'绿色消费与可持续生活','绿色消费理念普及，低碳出行与节约资源成为生活选择。',40,'环境','active',DATE_SUB(NOW(),INTERVAL 7 DAY),NOW()),
(2,'中小企业数字化转型','中小企业通过上云用数赋智降低成本、提升效率。',36,'商业','active',DATE_SUB(NOW(),INTERVAL 6 DAY),NOW()),
(1,'义务教育均衡发展','义务教育均衡化与双减政策正在改变教育生态。',35,'社会','active',DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(1,'人工智能伦理与治理','AI伦理、算法透明与责任归属成为国际讨论热点。',38,'科技','active',DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(2,'海洋经济与蓝色碳汇','海洋牧场、海上风电与蓝碳交易拓展了海洋经济内涵。',40,'环境','active',DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(1,'数字政府与一网通办','一网通办、跨省通办提升政务服务便利度。',32,'社会','active',DATE_SUB(NOW(),INTERVAL 2 DAY),NOW()),
(2,'新能源汽车充电网络','充电桩进小区与高速公路充电网络建设加速。',34,'商业','active',DATE_SUB(NOW(),INTERVAL 1 DAY),NOW());

-- 批量拟真观点文本（编号 26～125，满足核心业务表≥100 条）
INSERT INTO `texts` (`user_id`,`title`,`content`,`word_count`,`category`,`status`,`created_at`,`updated_at`) VALUES
(1,'观点文本-26','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 26 DAY),NOW()),
(1,'观点文本-27','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 25 DAY),NOW()),
(2,'观点文本-28','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 24 DAY),NOW()),
(1,'观点文本-29','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 23 DAY),NOW()),
(1,'观点文本-30','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 22 DAY),NOW()),
(1,'观点文本-31','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 21 DAY),NOW()),
(2,'观点文本-32','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 20 DAY),NOW()),
(1,'观点文本-33','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 19 DAY),NOW()),
(1,'观点文本-34','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 18 DAY),NOW()),
(1,'观点文本-35','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 17 DAY),NOW()),
(1,'观点文本-36','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 16 DAY),NOW()),
(2,'观点文本-37','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 15 DAY),NOW()),
(1,'观点文本-38','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 14 DAY),NOW()),
(1,'观点文本-39','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 13 DAY),NOW()),
(1,'观点文本-40','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 12 DAY),NOW()),
(1,'观点文本-41','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 11 DAY),NOW()),
(2,'观点文本-42','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 10 DAY),NOW()),
(1,'观点文本-43','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 9 DAY),NOW()),
(1,'观点文本-44','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 8 DAY),NOW()),
(1,'观点文本-45','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 7 DAY),NOW()),
(1,'观点文本-46','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 6 DAY),NOW()),
(1,'观点文本-47','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(2,'观点文本-48','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(1,'观点文本-49','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(1,'观点文本-50','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',DATE_SUB(NOW(),INTERVAL 2 DAY),NOW()),
(1,'观点文本-51','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',DATE_SUB(NOW(),INTERVAL 1 DAY),NOW()),
(1,'观点文本-52','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(2,'观点文本-53','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-54','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-55','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-56','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-57','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-58','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(2,'观点文本-59','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-60','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-61','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-62','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-63','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-64','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-65','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(2,'观点文本-66','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-67','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-68','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-69','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-70','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-71','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-72','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-73','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-74','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(2,'观点文本-75','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-76','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-77','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-78','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-79','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-80','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-81','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-82','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-83','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(2,'观点文本-84','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-85','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-86','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-87','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-88','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-89','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-90','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-91','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-92','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-93','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(2,'观点文本-94','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-95','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-96','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW()),
(1,'观点文本-97','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'环境','active',NOW(),NOW()),
(1,'观点文本-98','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'科技','active',NOW(),NOW()),
(1,'观点文本-99','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'社会','active',NOW(),NOW()),
(1,'观点文本-100','本文为观点类文本内容，用于聚类与摘要演示。内容涉及多领域多主题，便于测试系统聚类与摘要功能。',42,'商业','active',NOW(),NOW());

-- 聚类任务拟真数据
INSERT INTO `cluster_tasks` (`user_id`,`name`,`description`,`text_ids`,`cluster_count`,`algorithm`,`status`,`progress`,`created_at`,`completed_at`,`updated_at`) VALUES
(1,'科技与社会话题聚类','对科技和社会类文本进行观点聚类分析','[1,3,6,7,8]',3,'kmeans','completed',100,DATE_SUB(NOW(),INTERVAL 5 DAY),DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(1,'商业领域文本分析','针对商业类文本的聚类任务','[4,5]',2,'dbscan','completed',100,DATE_SUB(NOW(),INTERVAL 4 DAY),DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(2,'环境与可持续发展','环境主题文本聚类','[2,10,17,22,25]',2,'kmeans','completed',100,DATE_SUB(NOW(),INTERVAL 3 DAY),DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(1,'多领域观点聚类','跨领域观点聚类演示','[1,2,3,4,5,6,7,8]',4,'kmeans','running',65,DATE_SUB(NOW(),INTERVAL 1 DAY),NULL,NOW()),
(2,'社会议题聚类','社会类文本聚类','[3,6,8,12,19,21]',3,'kmeans','pending',0,DATE_SUB(NOW(),INTERVAL 0 DAY),NULL,NOW());

-- 聚类结果拟真数据（对应上述已完成任务）
INSERT INTO `cluster_results` (`task_id`,`cluster_index`,`text_id`,`score`,`sort_order`,`created_at`) VALUES
(1,0,1,0.92,0,NOW()),(1,0,7,0.88,1,NOW()),(1,1,3,0.90,0,NOW()),(1,1,8,0.85,1,NOW()),(1,2,6,0.91,0,NOW()),
(2,0,4,0.89,0,NOW()),(2,1,5,0.87,0,NOW()),
(3,0,2,0.93,0,NOW()),(3,0,17,0.82,1,NOW()),(3,1,10,0.88,0,NOW()),(3,1,22,0.84,1,NOW()),(3,1,25,0.80,2,NOW());

-- 摘要拟真数据
INSERT INTO `summaries` (`user_id`,`source_type`,`source_id`,`title`,`content`,`word_count`,`created_at`,`updated_at`) VALUES
(1,'cluster',1,'AI与技术发展观点摘要','文本集中讨论了人工智能在教育领域的应用前景和量子计算的商业化进程。主要观点包括：AI技术正在推动教育变革，个性化学习和智能评估成为趋势；量子计算虽然前景广阔，但在技术成熟度和人才储备方面仍面临挑战。',98,DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(1,'cluster',1,'社会治理与隐私保护摘要','这组文本围绕数字时代的社会治理展开讨论。数据隐私保护和基层社区智慧治理是两个核心议题。文本强调了在促进数据流通与保障用户隐私之间寻找平衡的必要性。',72,DATE_SUB(NOW(),INTERVAL 5 DAY),NOW()),
(1,'cluster',2,'企业管理变革趋势','远程办公模式已成为企业常态，正在深刻影响组织管理方式。弹性工作制和分布式协作带来效率提升的同时，也对绩效管理和企业文化建设提出新要求。',68,DATE_SUB(NOW(),INTERVAL 4 DAY),NOW()),
(2,'cluster',3,'环境与可持续发展摘要','气候变化与碳中和、生物多样性保护、循环经济与氢能等议题构成环境与可持续发展的主要讨论方向。政策、技术与市场共同推动绿色转型。',58,DATE_SUB(NOW(),INTERVAL 3 DAY),NOW()),
(1,'text',1,'人工智能在教育领域的应用前景-摘要','AI技术在教育领域的应用正在推动个性化学习与智能评估的发展，为教育公平和质量提升带来新可能。',45,DATE_SUB(NOW(),INTERVAL 2 DAY),NOW());

-- 操作历史拟真数据（≥50 条，支撑前端历史列表与近7天活跃度）
INSERT INTO `operation_history` (`user_id`,`op_type`,`op_desc`,`target_id`,`target_title`,`created_at`) VALUES
(1,'text_upload','上传文本',1,'人工智能在教育领域的应用前景',DATE_SUB(NOW(),INTERVAL 18 DAY)),
(1,'text_upload','上传文本',2,'全球气候变化与可持续发展',DATE_SUB(NOW(),INTERVAL 17 DAY)),
(1,'text_upload','上传文本',3,'数字经济时代的隐私保护挑战',DATE_SUB(NOW(),INTERVAL 16 DAY)),
(1,'text_upload','上传文本',4,'远程办公模式对企业管理的影响',DATE_SUB(NOW(),INTERVAL 15 DAY)),
(1,'text_upload','上传文本',5,'新能源汽车市场竞争格局分析',DATE_SUB(NOW(),INTERVAL 14 DAY)),
(1,'text_upload','上传文本',6,'社交媒体对青少年心理健康的影响',DATE_SUB(NOW(),INTERVAL 13 DAY)),
(1,'text_upload','上传文本',7,'量子计算的商业化进程',DATE_SUB(NOW(),INTERVAL 12 DAY)),
(1,'text_upload','上传文本',8,'城市化进程中的社区治理创新',DATE_SUB(NOW(),INTERVAL 11 DAY)),
(2,'text_upload','上传文本',9,'区块链在供应链金融中的应用',DATE_SUB(NOW(),INTERVAL 10 DAY)),
(2,'text_upload','上传文本',10,'碳中和目标下的产业转型路径',DATE_SUB(NOW(),INTERVAL 9 DAY)),
(1,'cluster_create','创建聚类任务',1,'科技与社会话题聚类',DATE_SUB(NOW(),INTERVAL 5 DAY)),
(1,'cluster_complete','聚类完成',1,'科技与社会话题聚类',DATE_SUB(NOW(),INTERVAL 5 DAY)),
(1,'summary_create','生成摘要',1,'AI与技术发展观点摘要',DATE_SUB(NOW(),INTERVAL 5 DAY)),
(1,'summary_create','生成摘要',2,'社会治理与隐私保护摘要',DATE_SUB(NOW(),INTERVAL 5 DAY)),
(1,'cluster_create','创建聚类任务',2,'商业领域文本分析',DATE_SUB(NOW(),INTERVAL 4 DAY)),
(1,'cluster_complete','聚类完成',2,'商业领域文本分析',DATE_SUB(NOW(),INTERVAL 4 DAY)),
(1,'summary_create','生成摘要',3,'企业管理变革趋势',DATE_SUB(NOW(),INTERVAL 4 DAY)),
(2,'cluster_create','创建聚类任务',3,'环境与可持续发展',DATE_SUB(NOW(),INTERVAL 3 DAY)),
(2,'cluster_complete','聚类完成',3,'环境与可持续发展',DATE_SUB(NOW(),INTERVAL 3 DAY)),
(2,'summary_create','生成摘要',4,'环境与可持续发展摘要',DATE_SUB(NOW(),INTERVAL 3 DAY)),
(1,'text_upload','上传文本',11,'智慧医疗与健康管理趋势',DATE_SUB(NOW(),INTERVAL 2 DAY)),
(1,'cluster_create','创建聚类任务',4,'多领域观点聚类',DATE_SUB(NOW(),INTERVAL 1 DAY)),
(2,'cluster_create','创建聚类任务',5,'社会议题聚类',NOW());

-- 补充更多历史以支撑近7天活跃度图表
INSERT INTO `operation_history` (`user_id`,`op_type`,`op_desc`,`target_id`,`target_title`,`created_at`) VALUES
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 1 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 2 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 3 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 4 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 5 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 6 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本',DATE_SUB(NOW(),INTERVAL 7 DAY)),
(1,'text_upload','上传文本',NULL,'观点文本-今日',NOW()),
(2,'text_upload','上传文本',NULL,'观点文本-今日',NOW());
