# tu_moneyflow_ind_dc 表结构说明

## 概述

`tu_moneyflow_ind_dc` 是板块资金流向数据表，记录了不同板块（行业、概念、地域）的每日资金流向情况。该表包含了主力资金、超大单、大单、中单、小单等多维度的资金流向数据。

## 表结构详情

| 字段名 | 数据类型 | 说明 | 备注 |
|--------|----------|------|------|
| id | bigint | 主键ID | 自增主键 |
| trade_date | date | 交易日期 | 格式：YYYY-MM-DD |
| content_type | varchar | 板块分类 | 取值：行业、概念、地域 |
| ts_code | varchar | 板块代码 | 格式：BKxxxx.DC |
| name | varchar | 板块名称 | 如：光伏设备、半导体等 |
| pct_change | decimal | 板块涨跌幅（%） | 当日涨跌幅百分比 |
| close | decimal | 板块最新指数 | 板块指数收盘值 |
| net_amount | decimal | 今日主力净流入净额（元） | 超大单+大单净流入金额 |
| net_amount_rate | decimal | 今日主力净流入净占比% | 主力净流入占总成交额比例 |
| buy_elg_amount | decimal | 今日超大单净流入净额（元） | 单笔≥100万元 |
| buy_elg_amount_rate | decimal | 今日超大单净流入净占比% | 超大单净流入占比 |
| buy_lg_amount | decimal | 今日大单净流入净额（元） | 单笔20-100万元 |
| buy_lg_amount_rate | decimal | 今日大单净流入净占比% | 大单净流入占比 |
| buy_md_amount | decimal | 今日中单净流入净额（元） | 单笔4-20万元 |
| buy_md_amount_rate | decimal | 今日中单净流入净占比% | 中单净流入占比 |
| buy_sm_amount | decimal | 今日小单净流入净额（元） | 单笔<4万元 |
| buy_sm_amount_rate | decimal | 今日小单净流入净占比% | 小单净流入占比 |
| buy_sm_amount_stock | varchar | 今日主力净流入最大股 | 该板块中主力净流入最大的个股名称 |
| rank | int | 分类排名 | 按主力净流入倒序排列的排名 |

## 数据特征

### 1. 板块类型（content_type）

- **行业板块**：约31,046条记录，涵盖各类行业分类
- **概念板块**：约37,838条记录，包含各种概念主题
- **地域板块**：约2,666条记录，按地理区域划分

### 2. 板块代码格式（ts_code）

所有板块代码统一使用 `BKxxxx.DC` 格式：
- 前缀：BK
- 编号：4位数字
- 后缀：.DC

示例：
- BK1036.DC - 半导体（行业）
- BK0588.DC - 太阳能（概念）
- BK0150.DC - 北京板块（地域）

### 3. 资金流向分类

资金按照单笔成交金额分为四个等级：
- **超大单**：单笔成交额 ≥ 100万元
- **大单**：单笔成交额 20-100万元
- **中单**：单笔成交额 4-20万元
- **小单**：单笔成交额 < 4万元

**主力资金** = 超大单 + 大单

### 4. 数据时间范围

- 最早日期：2024-01-02
- 最新日期：2025-07-02（持续更新）
- 交易日数：361天

### 5. 数据范围示例（2025-07-02）

- 主力净流入范围：-374.40亿 ~ 44.91亿
- 主力净流入均值：-15.61亿
- 超大单净流入范围：-196.34亿 ~ 32.56亿
- 大单净流入范围：-178.06亿 ~ 12.35亿

## 使用示例

### 1. 查询某日资金流入TOP板块

```sql
SELECT 
    content_type,
    ts_code,
    name,
    net_amount/100000000 as net_amount_yi,
    pct_change,
    buy_sm_amount_stock
FROM tu_moneyflow_ind_dc
WHERE trade_date = '2025-07-02'
    AND `rank` <= 10
ORDER BY content_type, `rank`;
```

### 2. 查询特定板块的历史资金流向

```sql
SELECT 
    trade_date,
    name,
    net_amount/100000000 as net_amount_yi,
    buy_elg_amount/100000000 as elg_amount_yi,
    pct_change
FROM tu_moneyflow_ind_dc
WHERE ts_code = 'BK1031.DC'  -- 光伏设备
ORDER BY trade_date DESC
LIMIT 30;
```

### 3. 分析板块资金流向与涨跌幅关系

```sql
SELECT 
    content_type,
    AVG(pct_change) as avg_pct_change,
    AVG(net_amount_rate) as avg_net_rate,
    COUNT(*) as count
FROM tu_moneyflow_ind_dc
WHERE trade_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY content_type;
```

## 注意事项

1. **rank字段是MySQL保留字**，查询时需要使用反引号 \`rank\`
2. **金额单位为元**，通常需要转换为亿元显示（除以100000000）
3. **buy_sm_amount_stock字段**记录的是该板块中主力净流入最大的个股，可用于识别板块龙头
4. **数据更新频率**：每个交易日收盘后更新

## 相关表

- `tu_moneyflow_dc`：个股资金流向表
- `tu_stock_basic`：股票基本信息表（包含所属行业）
- `tu_daily_detail`：股票日线行情表