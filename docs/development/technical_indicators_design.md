# 技术指标功能设计方案

## 一、方案选择：混合模式

### 1. 核心思路
- **常用指标**：导入数据库，提供快速查询
- **高级指标**：实时API调用，按需获取
- **缓存机制**：减少重复API调用

### 2. 具体实施方案

#### 2.1 数据库存储（高频使用）
建议创建新表 `tu_technical_indicators` 存储常用指标：

```sql
CREATE TABLE tu_technical_indicators (
    ts_code VARCHAR(20),
    trade_date VARCHAR(8),
    -- 均线指标
    ma_5 FLOAT,
    ma_10 FLOAT,
    ma_20 FLOAT,
    ma_60 FLOAT,
    ema_5 FLOAT,
    ema_20 FLOAT,
    -- MACD指标
    macd_dif FLOAT,
    macd_dea FLOAT,
    macd FLOAT,
    -- KDJ指标
    kdj_k FLOAT,
    kdj_d FLOAT,
    kdj_j FLOAT,
    -- RSI指标
    rsi_6 FLOAT,
    rsi_12 FLOAT,
    rsi_24 FLOAT,
    -- BOLL指标
    boll_upper FLOAT,
    boll_mid FLOAT,
    boll_lower FLOAT,
    -- 其他关键指标
    volume_ratio FLOAT,  -- 量比
    turnover_rate FLOAT, -- 换手率
    PRIMARY KEY (ts_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_code_date (ts_code, trade_date)
);
```

**存储策略**：
- 每日定时更新（建议凌晨3点）
- 只存储最近2年数据（减少存储压力）
- 使用前复权价格（_qfq后缀）

#### 2.2 实时API调用（低频/高级）
对于以下场景使用实时API：
- 历史数据回测（超过2年）
- 高级指标（CCI、DMI、ATR等）
- 用户自定义参数的指标
- 特殊时间段查询

#### 2.3 缓存策略
```python
# Redis缓存结构
cache_key = f"tech_indicators:{ts_code}:{trade_date}:{indicator_type}"
cache_ttl = 3600  # 1小时缓存
```

## 二、SQL Agent技术指标模板设计

### 1. 快速查询模板（数据库）

```python
# 新增SQL模板
TECHNICAL_MA = """
SELECT ts_code, trade_date, ma_5, ma_10, ma_20, ma_60
FROM tu_technical_indicators
WHERE ts_code = %(ts_code)s 
  AND trade_date = %(trade_date)s
"""

TECHNICAL_MACD = """
SELECT ts_code, trade_date, macd_dif, macd_dea, macd
FROM tu_technical_indicators
WHERE ts_code = %(ts_code)s
  AND trade_date BETWEEN %(start_date)s AND %(end_date)s
ORDER BY trade_date DESC
"""

TECHNICAL_CROSS = """
-- 金叉死叉查询
SELECT t1.trade_date, 
       CASE 
         WHEN t1.ma_5 > t1.ma_20 AND t2.ma_5 <= t2.ma_20 THEN '金叉'
         WHEN t1.ma_5 < t1.ma_20 AND t2.ma_5 >= t2.ma_20 THEN '死叉'
       END as cross_type
FROM tu_technical_indicators t1
JOIN tu_technical_indicators t2 
  ON t1.ts_code = t2.ts_code 
  AND t1.trade_date > t2.trade_date
WHERE t1.ts_code = %(ts_code)s
  AND cross_type IS NOT NULL
ORDER BY t1.trade_date DESC
LIMIT 10
"""
```

### 2. API调用模板（高级指标）

```python
class TechnicalIndicatorAPI:
    def get_advanced_indicators(self, ts_code, indicators=['cci', 'dmi']):
        """获取高级技术指标"""
        # 1. 检查缓存
        # 2. 调用stk_factor_pro接口
        # 3. 提取所需指标
        # 4. 缓存结果
        pass
```

## 三、实施步骤

### Phase 1：基础建设（2天）
1. 创建技术指标表结构
2. 开发数据导入脚本
3. 导入最近2年常用指标数据

### Phase 2：SQL模板开发（1天）
1. 实现5个基础技术指标查询模板
2. 实现金叉/死叉等衍生查询
3. 集成到SQL Agent

### Phase 3：API集成（2天）
1. 开发技术指标API调用模块
2. 实现缓存机制
3. 与SQL Agent集成

### Phase 4：优化与测试（1天）
1. 性能优化
2. 完整测试
3. 文档更新

## 四、查询示例

```
用户："贵州茅台的5日均线"
SQL Agent：快速查询tu_technical_indicators表

用户："贵州茅台最近的MACD金叉"
SQL Agent：查询MACD历史数据，计算交叉点

用户："贵州茅台的CCI指标"
SQL Agent：调用API获取高级指标

用户："比较茅台和五粮液的RSI"
SQL Agent：批量查询多股票技术指标
```

## 五、性能预期

- 数据库查询：<0.1秒
- API调用：1-3秒（含网络延迟）
- 缓存命中：<0.05秒

## 六、维护计划

1. **日常更新**：每日凌晨更新技术指标
2. **数据清理**：定期清理超过2年的数据
3. **监控告警**：API调用失败告警
4. **扩展计划**：根据用户使用频率调整存储策略

---
更新时间：2025-07-05