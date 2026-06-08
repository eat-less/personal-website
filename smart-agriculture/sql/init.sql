-- 智能农业管理系统 - 数据库初始化脚本
CREATE DATABASE IF NOT EXISTS smart_agriculture DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_agriculture;

-- 用户表
CREATE TABLE sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(256) NOT NULL COMMENT '密码',
    real_name VARCHAR(64) COMMENT '真实姓名',
    email VARCHAR(128) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    role TINYINT DEFAULT 0 COMMENT '角色: 0-普通用户, 1-管理员',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '用户表';

-- 农业大棚/区域表
CREATE TABLE agri_greenhouse (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '大棚名称',
    area DECIMAL(10,2) COMMENT '面积(平方米)',
    location VARCHAR(256) COMMENT '位置描述',
    crop_type VARCHAR(128) COMMENT '种植作物类型',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-停用, 1-运行',
    description TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '农业大棚表';

-- 传感器表
CREATE TABLE agri_sensor (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    greenhouse_id BIGINT NOT NULL COMMENT '所属大棚ID',
    name VARCHAR(128) NOT NULL COMMENT '传感器名称',
    sensor_type VARCHAR(32) NOT NULL COMMENT '类型: temperature/humidity/light/co2/soil_temp/soil_moisture',
    unit VARCHAR(16) COMMENT '单位',
    location VARCHAR(256) COMMENT '安装位置',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-离线, 1-在线',
    min_threshold DECIMAL(10,2) COMMENT '最低阈值',
    max_threshold DECIMAL(10,2) COMMENT '最高阈值',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (greenhouse_id) REFERENCES agri_greenhouse(id)
) ENGINE=InnoDB COMMENT '传感器表';

-- 传感器数据记录表
CREATE TABLE agri_sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id BIGINT NOT NULL COMMENT '传感器ID',
    greenhouse_id BIGINT NOT NULL COMMENT '大棚ID',
    value DECIMAL(10,2) NOT NULL COMMENT '采集值',
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
    FOREIGN KEY (sensor_id) REFERENCES agri_sensor(id)
) ENGINE=InnoDB COMMENT '传感器数据表';

-- 设备表
CREATE TABLE agri_device (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    greenhouse_id BIGINT NOT NULL COMMENT '所属大棚ID',
    name VARCHAR(128) NOT NULL COMMENT '设备名称',
    device_type VARCHAR(32) NOT NULL COMMENT '类型: water_pump/fan/light/curtain/heater/fertilizer',
    status TINYINT DEFAULT 0 COMMENT '开关状态: 0-关闭, 1-开启',
    online_status TINYINT DEFAULT 1 COMMENT '在线状态: 0-离线, 1-在线',
    location VARCHAR(256) COMMENT '安装位置',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (greenhouse_id) REFERENCES agri_greenhouse(id)
) ENGINE=InnoDB COMMENT '设备表';

-- 设备操作日志表
CREATE TABLE agri_device_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id BIGINT NOT NULL COMMENT '设备ID',
    action TINYINT NOT NULL COMMENT '操作: 0-关闭, 1-开启',
    operator_id BIGINT COMMENT '操作人ID',
    remark VARCHAR(256) COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES agri_device(id)
) ENGINE=InnoDB COMMENT '设备操作日志表';

-- 告警记录表
CREATE TABLE agri_alarm (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    greenhouse_id BIGINT COMMENT '大棚ID',
    sensor_id BIGINT COMMENT '传感器ID',
    alarm_type VARCHAR(32) NOT NULL COMMENT '告警类型: threshold/device_offline/system',
    level TINYINT DEFAULT 1 COMMENT '级别: 0-普通, 1-警告, 2-严重',
    title VARCHAR(256) NOT NULL COMMENT '告警标题',
    content TEXT COMMENT '告警详情',
    is_handled TINYINT DEFAULT 0 COMMENT '是否已处理: 0-未处理, 1-已处理',
    handled_by BIGINT COMMENT '处理人ID',
    handled_at DATETIME COMMENT '处理时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '告警记录表';

-- 摄像头表
CREATE TABLE agri_camera (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    greenhouse_id BIGINT NOT NULL COMMENT '所属大棚ID',
    name VARCHAR(128) NOT NULL COMMENT '摄像头名称',
    rtsp_url VARCHAR(512) COMMENT 'RTSP流地址',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-离线, 1-在线',
    location VARCHAR(256) COMMENT '安装位置',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (greenhouse_id) REFERENCES agri_greenhouse(id)
) ENGINE=InnoDB COMMENT '摄像头表';

-- 插入默认管理员 (密码: admin123)
INSERT INTO sys_user (username, password, real_name, role) VALUES
('admin', '$2b$12$LJ3m4ys3GZfQHLmzZ.HZtezZPHNh0kraFGF2RHmUN9FGTFQHNI4gy', '系统管理员', 1);

-- 插入示例大棚
INSERT INTO agri_greenhouse (name, area, location, crop_type) VALUES
('1号温室大棚', 500.00, '园区东区', '番茄'),
('2号温室大棚', 500.00, '园区西区', '黄瓜'),
('3号育苗温室', 200.00, '园区北区', '育苗');

-- 插入示例传感器
INSERT INTO agri_sensor (greenhouse_id, name, sensor_type, unit, min_threshold, max_threshold) VALUES
(1, '温度传感器-01', 'temperature', '°C', 18.0, 30.0),
(1, '湿度传感器-01', 'humidity', '%', 50.0, 85.0),
(1, '光照传感器-01', 'light', 'Lux', 5000.0, 60000.0),
(1, 'CO2传感器-01', 'co2', 'ppm', 300.0, 800.0),
(1, '土壤温度-01', 'soil_temp', '°C', 15.0, 28.0),
(1, '土壤湿度-01', 'soil_moisture', '%', 40.0, 80.0);

-- 插入示例设备
INSERT INTO agri_device (greenhouse_id, name, device_type, status) VALUES
(1, '灌溉水泵', 'water_pump', 0),
(1, '通风风机', 'fan', 0),
(1, '补光灯', 'light', 0),
(1, '电动卷帘', 'curtain', 0),
(1, '加热器', 'heater', 0);

-- 插入示例摄像头
INSERT INTO agri_camera (greenhouse_id, name, rtsp_url) VALUES
(1, '1号棚高清摄像头', 'rtsp://192.168.1.100:554/stream1'),
(1, '1号棚全景摄像头', 'rtsp://192.168.1.101:554/stream1');
