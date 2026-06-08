-- 个人介绍网站数据库
CREATE DATABASE IF NOT EXISTS personal_website DEFAULT CHARACTER SET utf8mb4;
USE personal_website;

-- 个人信息表
CREATE TABLE user_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '姓名',
    title VARCHAR(128) COMMENT '职位/头衔',
    avatar_url VARCHAR(512) COMMENT '头像URL',
    bio TEXT COMMENT '个人简介',
    email VARCHAR(128) COMMENT '邮箱',
    phone VARCHAR(32) COMMENT '电话',
    github VARCHAR(256) COMMENT 'GitHub',
    linkedin VARCHAR(256) COMMENT 'LinkedIn',
    location VARCHAR(128) COMMENT '所在地',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '个人信息表';

-- 技能表
CREATE TABLE skill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(64) NOT NULL COMMENT '分类: 前端/后端/数据库/工具',
    name VARCHAR(64) NOT NULL COMMENT '技能名称',
    level INT DEFAULT 80 COMMENT '熟练度 0-100',
    icon VARCHAR(64) COMMENT '图标标识',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '技能表';

-- 项目经历表
CREATE TABLE project (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '项目名称',
    description TEXT COMMENT '项目描述',
    cover_url VARCHAR(512) COMMENT '封面图URL',
    tech_stack VARCHAR(256) COMMENT '技术栈 JSON数组',
    github_url VARCHAR(256) COMMENT 'GitHub地址',
    demo_url VARCHAR(256) COMMENT '演示地址',
    highlights TEXT COMMENT '项目亮点 JSON数组',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '项目经历表';

-- 联系方式留言表
CREATE TABLE contact_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '访客姓名',
    email VARCHAR(128) NOT NULL COMMENT '访客邮箱',
    subject VARCHAR(256) COMMENT '主题',
    content TEXT NOT NULL COMMENT '留言内容',
    is_read TINYINT DEFAULT 0 COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '留言表';

-- 默认数据
INSERT INTO user_info (name, title, bio, email, phone, github, linkedin, location) VALUES
('张三', '全栈开发工程师', '热爱技术，专注于Web全栈开发，有5年后端与前端开发经验，擅长Python和Vue技术栈。', 'zhangsan@example.com', '13800138000', 'https://github.com/zhangsan', 'https://linkedin.com/in/zhangsan', '北京');

INSERT INTO skill (category, name, level, icon, sort_order) VALUES
('前端', 'Vue.js', 90, 'vuejs', 1),
('前端', 'React', 75, 'react', 2),
('前端', 'JavaScript', 88, 'javascript', 3),
('前端', 'HTML/CSS', 92, 'html5', 4),
('后端', 'Python', 95, 'python', 5),
('后端', 'FastAPI', 90, 'fastapi', 6),
('后端', 'Node.js', 78, 'nodejs', 7),
('数据库', 'MySQL', 85, 'mysql', 8),
('数据库', 'Redis', 80, 'redis', 9),
('工具', 'Docker', 82, 'docker', 10),
('工具', 'Git', 90, 'git', 11);

INSERT INTO project (name, description, tech_stack, github_url, demo_url, highlights, sort_order) VALUES
('智能农业管理平台', '基于IoT的农业大棚监控系统，实时采集温湿度、光照等数据，支持远程设备控制和视频监控', '["Vue3","FastAPI","MySQL","MQTT","ECharts"]', 'https://github.com/zhangsan/agri-platform', 'https://agri.example.com', '["支持MQTT协议实时数据推送","WebSocket实现设备远程控制","大屏数据可视化展示","支持多棚区管理"]', 1),
('电商微服务系统', '基于Spring Cloud的电商平台，包含商品、订单、用户等微服务模块', '["Spring Cloud","Vue2","MySQL","Redis","RabbitMQ"]', 'https://github.com/zhangsan/ecommerce', 'https://shop.example.com', '["微服务架构设计","高并发秒杀方案","分布式事务处理","ELK日志收集"]', 2),
('数据可视化大屏', '企业级数据大屏展示系统，支持多数据源接入和实时刷新', '["Vue3","ECharts","WebSocket","Python","Flask"]', 'https://github.com/zhangsan/datav', 'https://datav.example.com', '["多图表联动筛选","实时数据刷新","自适应分辨率","主题切换"]', 3);
