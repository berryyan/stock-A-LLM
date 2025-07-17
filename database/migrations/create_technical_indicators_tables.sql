-- Technical Analysis Agent 数据库表创建脚本
-- 版本：v1.0
-- 创建时间：2025-07-13
-- 说明：用于存储技术指标数据和形态识别结果

-- 使用Tushare数据库
USE Tushare;

-- ========================================
-- 1. 技术指标主表
-- ========================================
DROP TABLE IF EXISTS tu_technical_indicators;

CREATE TABLE tu_technical_indicators (
    -- 主键
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date VARCHAR(8) NOT NULL COMMENT '交易日期',
    
    -- 价格数据（冗余存储以提高查询效率）
    close_price DECIMAL(10,2) COMMENT '收盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    pre_close DECIMAL(10,2) COMMENT '前收盘价',
    
    -- 均线指标
    ma_5 DECIMAL(10,2) COMMENT '5日均线',
    ma_10 DECIMAL(10,2) COMMENT '10日均线',
    ma_20 DECIMAL(10,2) COMMENT '20日均线',
    ma_30 DECIMAL(10,2) COMMENT '30日均线',
    ma_60 DECIMAL(10,2) COMMENT '60日均线',
    ma_120 DECIMAL(10,2) COMMENT '120日均线',
    ma_250 DECIMAL(10,2) COMMENT '250日均线',
    
    -- 指数移动平均线
    ema_12 DECIMAL(10,2) COMMENT '12日EMA',
    ema_26 DECIMAL(10,2) COMMENT '26日EMA',
    
    -- MACD指标
    macd_dif DECIMAL(10,4) COMMENT 'MACD DIF值',
    macd_dea DECIMAL(10,4) COMMENT 'MACD DEA值',
    macd_histogram DECIMAL(10,4) COMMENT 'MACD柱状图',
    
    -- KDJ指标
    kdj_k DECIMAL(10,2) COMMENT 'KDJ-K值',
    kdj_d DECIMAL(10,2) COMMENT 'KDJ-D值',
    kdj_j DECIMAL(10,2) COMMENT 'KDJ-J值',
    
    -- RSI指标
    rsi_6 DECIMAL(10,2) COMMENT '6日RSI',
    rsi_12 DECIMAL(10,2) COMMENT '12日RSI',
    rsi_24 DECIMAL(10,2) COMMENT '24日RSI',
    
    -- 布林带
    boll_upper DECIMAL(10,2) COMMENT '布林带上轨',
    boll_middle DECIMAL(10,2) COMMENT '布林带中轨',
    boll_lower DECIMAL(10,2) COMMENT '布林带下轨',
    boll_width DECIMAL(10,4) COMMENT '布林带宽度',
    
    -- 成交量指标
    volume BIGINT COMMENT '成交量',
    volume_ratio DECIMAL(10,2) COMMENT '量比',
    volume_ma_5 BIGINT COMMENT '5日成交量均值',
    volume_ma_10 BIGINT COMMENT '10日成交量均值',
    
    -- 其他指标
    turnover_rate DECIMAL(10,2) COMMENT '换手率',
    amplitude DECIMAL(10,2) COMMENT '振幅',
    change_rate DECIMAL(10,2) COMMENT '涨跌幅',
    
    -- 信号标记
    ma_cross_signal VARCHAR(20) COMMENT '均线交叉信号',
    macd_cross_signal VARCHAR(20) COMMENT 'MACD交叉信号',
    kdj_signal VARCHAR(20) COMMENT 'KDJ信号（超买/超卖）',
    rsi_signal VARCHAR(20) COMMENT 'RSI信号（超买/超卖）',
    boll_signal VARCHAR(20) COMMENT '布林带信号（突破）',
    
    -- 综合评分
    technical_score INT COMMENT '技术面综合评分(0-100)',
    trend_strength VARCHAR(20) COMMENT '趋势强度（强势/中性/弱势）',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    UNIQUE KEY idx_code_date (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_ma_cross (ts_code, ma_cross_signal),
    INDEX idx_macd_cross (ts_code, macd_cross_signal),
    INDEX idx_technical_score (ts_code, technical_score),
    INDEX idx_update_time (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标数据表';

-- ========================================
-- 2. K线形态识别结果表
-- ========================================
DROP TABLE IF EXISTS tu_pattern_recognition;

CREATE TABLE tu_pattern_recognition (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    pattern_type VARCHAR(50) NOT NULL COMMENT '形态类型',
    pattern_name_cn VARCHAR(100) COMMENT '形态中文名',
    start_date VARCHAR(8) NOT NULL COMMENT '形态开始日期',
    end_date VARCHAR(8) NOT NULL COMMENT '形态结束日期',
    key_price DECIMAL(10,2) COMMENT '关键价位',
    target_price DECIMAL(10,2) COMMENT '目标价位',
    stop_loss_price DECIMAL(10,2) COMMENT '止损价位',
    confidence DECIMAL(5,2) COMMENT '置信度(0-100)',
    status VARCHAR(20) COMMENT '状态（形成中/已确认/已失效）',
    description TEXT COMMENT '形态描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_code_type (ts_code, pattern_type),
    INDEX idx_date_range (start_date, end_date),
    INDEX idx_status (status),
    INDEX idx_confidence (confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='K线形态识别结果表';

-- ========================================
-- 3. 技术指标实时计算缓存表
-- ========================================
DROP TABLE IF EXISTS tu_technical_cache;

CREATE TABLE tu_technical_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL COMMENT '缓存键',
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    indicator_type VARCHAR(50) NOT NULL COMMENT '指标类型',
    params JSON COMMENT '计算参数',
    result JSON COMMENT '计算结果',
    expired_at TIMESTAMP NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY idx_cache_key (cache_key),
    INDEX idx_expired (expired_at),
    INDEX idx_code_type (ts_code, indicator_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标计算缓存表';

-- ========================================
-- 4. 技术指标计算任务表
-- ========================================
DROP TABLE IF EXISTS tu_technical_tasks;

CREATE TABLE tu_technical_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL COMMENT '任务ID',
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
    ts_code VARCHAR(20) COMMENT '股票代码（NULL表示全市场）',
    trade_date VARCHAR(8) COMMENT '交易日期',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态',
    priority INT DEFAULT 0 COMMENT '优先级',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    error_message TEXT COMMENT '错误信息',
    started_at TIMESTAMP NULL COMMENT '开始时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY idx_task_id (task_id),
    INDEX idx_status_priority (status, priority),
    INDEX idx_code_date (ts_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标计算任务表';

-- ========================================
-- 5. 创建存储过程：获取最新技术指标
-- ========================================
DELIMITER //

CREATE PROCEDURE get_latest_technical_indicators(
    IN p_ts_code VARCHAR(20),
    IN p_days INT
)
BEGIN
    SELECT 
        t.*,
        CASE 
            WHEN t.rsi_6 > 70 THEN '超买'
            WHEN t.rsi_6 < 30 THEN '超卖'
            ELSE '正常'
        END as rsi_status,
        CASE
            WHEN t.close_price > t.boll_upper THEN '突破上轨'
            WHEN t.close_price < t.boll_lower THEN '突破下轨'
            ELSE '轨道内'
        END as boll_status,
        CASE
            WHEN t.kdj_j > 100 THEN '超买'
            WHEN t.kdj_j < 0 THEN '超卖'
            ELSE '正常'
        END as kdj_status
    FROM tu_technical_indicators t
    WHERE t.ts_code = p_ts_code
    ORDER BY t.trade_date DESC
    LIMIT p_days;
END//

-- ========================================
-- 6. 创建存储过程：查找金叉死叉
-- ========================================
CREATE PROCEDURE find_cross_signals(
    IN p_ts_code VARCHAR(20),
    IN p_signal_type VARCHAR(20),
    IN p_days INT
)
BEGIN
    IF p_signal_type = 'MA' THEN
        SELECT 
            trade_date,
            close_price,
            ma_5,
            ma_10,
            ma_20,
            ma_cross_signal
        FROM tu_technical_indicators
        WHERE ts_code = p_ts_code
          AND ma_cross_signal IS NOT NULL
        ORDER BY trade_date DESC
        LIMIT p_days;
    ELSEIF p_signal_type = 'MACD' THEN
        SELECT 
            trade_date,
            close_price,
            macd_dif,
            macd_dea,
            macd_histogram,
            macd_cross_signal
        FROM tu_technical_indicators
        WHERE ts_code = p_ts_code
          AND macd_cross_signal IS NOT NULL
        ORDER BY trade_date DESC
        LIMIT p_days;
    ELSE
        SELECT 
            trade_date,
            close_price,
            ma_cross_signal,
            macd_cross_signal
        FROM tu_technical_indicators
        WHERE ts_code = p_ts_code
          AND (ma_cross_signal IS NOT NULL OR macd_cross_signal IS NOT NULL)
        ORDER BY trade_date DESC
        LIMIT p_days;
    END IF;
END//

DELIMITER ;

-- ========================================
-- 7. 创建触发器：自动更新信号
-- ========================================
DELIMITER //

CREATE TRIGGER update_technical_signals
BEFORE INSERT ON tu_technical_indicators
FOR EACH ROW
BEGIN
    -- 检测均线金叉死叉
    IF NEW.ma_5 IS NOT NULL AND NEW.ma_20 IS NOT NULL THEN
        SET @prev_ma5 = (
            SELECT ma_5 FROM tu_technical_indicators 
            WHERE ts_code = NEW.ts_code 
              AND trade_date < NEW.trade_date 
            ORDER BY trade_date DESC 
            LIMIT 1
        );
        
        SET @prev_ma20 = (
            SELECT ma_20 FROM tu_technical_indicators 
            WHERE ts_code = NEW.ts_code 
              AND trade_date < NEW.trade_date 
            ORDER BY trade_date DESC 
            LIMIT 1
        );
        
        IF @prev_ma5 IS NOT NULL AND @prev_ma20 IS NOT NULL THEN
            IF NEW.ma_5 > NEW.ma_20 AND @prev_ma5 <= @prev_ma20 THEN
                SET NEW.ma_cross_signal = '金叉';
            ELSEIF NEW.ma_5 < NEW.ma_20 AND @prev_ma5 >= @prev_ma20 THEN
                SET NEW.ma_cross_signal = '死叉';
            END IF;
        END IF;
    END IF;
    
    -- 检测RSI超买超卖
    IF NEW.rsi_6 IS NOT NULL THEN
        IF NEW.rsi_6 > 70 THEN
            SET NEW.rsi_signal = '超买';
        ELSEIF NEW.rsi_6 < 30 THEN
            SET NEW.rsi_signal = '超卖';
        END IF;
    END IF;
    
    -- 检测KDJ超买超卖
    IF NEW.kdj_j IS NOT NULL THEN
        IF NEW.kdj_j > 100 THEN
            SET NEW.kdj_signal = '超买';
        ELSEIF NEW.kdj_j < 0 THEN
            SET NEW.kdj_signal = '超卖';
        END IF;
    END IF;
END//

DELIMITER ;

-- ========================================
-- 8. 插入测试数据（可选）
-- ========================================
-- INSERT INTO tu_technical_indicators (ts_code, trade_date, close_price, ma_5, ma_10, ma_20)
-- VALUES 
-- ('600519.SH', '20250713', 1850.00, 1840.00, 1835.00, 1830.00),
-- ('600519.SH', '20250712', 1845.00, 1838.00, 1833.00, 1828.00);

-- ========================================
-- 9. 权限设置
-- ========================================
-- GRANT SELECT, INSERT, UPDATE ON Tushare.tu_technical_indicators TO 'readonly_user'@'%';
-- GRANT SELECT ON Tushare.tu_pattern_recognition TO 'readonly_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON Tushare.tu_technical_cache TO 'readonly_user'@'%';
-- GRANT EXECUTE ON PROCEDURE Tushare.get_latest_technical_indicators TO 'readonly_user'@'%';
-- GRANT EXECUTE ON PROCEDURE Tushare.find_cross_signals TO 'readonly_user'@'%';

-- 执行完成
SELECT 'Technical indicators tables created successfully!' as message;