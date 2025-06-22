# Tushare数据库分析报告

生成时间: 2025-06-22 23:08:20

数据库: Tushare

总表数: 14

## 数据表概览

| 表名 | 表说明 | 记录数 | 列数 | 数据范围 |
|------|--------|--------|------|----------|
| tu_anns_d |  | 2,097,794 | 7 | 2023-01-01 ~ 2025-06-21 |
| tu_balancesheet |  | 126,652 | 161 | 20190408 ~ 20250523 |
| tu_cashflow |  | 121,840 | 100 | 20190408 ~ 20250430 |
| tu_daily_basic |  | 6,308,521 | 20 | 20200102 ~ 20250616 |
| tu_daily_detail |  | 15,643,471 | 13 | 2000-01-04 ~ 2025-06-20 |
| tu_fina_indicator |  | 137,888 | 59 | 20190408 ~ 20250613 |
| tu_forecast |  | 37,349 | 15 | 20190115 ~ 20250612 |
| tu_income |  | 128,932 | 83 | 20190408 ~ 20250524 |
| tu_irm_qa_sh |  | 200,261 | 7 | 2023-06-07 ~ 2025-06-20 |
| tu_irm_qa_sz |  | 497,656 | 8 | 2023-01-01 ~ 2025-06-20 |
| tu_moneyflow_dc |  | 2,411,419 | 16 | 2023-09-11 ~ 2025-06-20 |
| tu_moneyflow_ind_dc |  | 67,134 | 19 | 2024-01-02 ~ 2025-06-20 |
| tu_stock_basic |  | 5,418 | 20 | 19901219 ~ 20250612 |
| tu_suspend_d |  | 5,878 | 7 | 20240102 ~ 20250613 |

## 中文注释覆盖率
- 表注释覆盖率: 0.0%
- 字段注释覆盖率: 96.07%
- 总字段数: 535
- 已注释字段数: 514

### 注释覆盖率最低的表

| 表名 | 总字段数 | 已注释 | 覆盖率 |
|------|----------|--------|--------|
| tu_moneyflow_ind_dc | 19 | 0 | 0.0% |
| tu_daily_detail | 13 | 11 | 84.62% |
| tu_anns_d | 7 | 7 | 100.0% |
| tu_balancesheet | 161 | 161 | 100.0% |
| tu_cashflow | 100 | 100 | 100.0% |
| tu_daily_basic | 20 | 20 | 100.0% |
| tu_fina_indicator | 59 | 59 | 100.0% |
| tu_forecast | 15 | 15 | 100.0% |
| tu_income | 83 | 83 | 100.0% |
| tu_irm_qa_sh | 7 | 7 | 100.0% |

## 数据完整性检查

### 日线数据
- 平均每日股票数: 5,392
- 平均每日基础数据: 4,311

## 重要表详细信息

### tu_stock_basic

**主要字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT | 主键ID |
| ts_code | VARCHAR(10) | TS代码 |
| symbol | VARCHAR(10) | 股票代码 |
| name | VARCHAR(50) | 股票名称 |
| area | VARCHAR(50) | 地域 |
| industry | VARCHAR(50) | 所属行业 |
| fullname | VARCHAR(100) | 股票全称 |
| enname | VARCHAR(200) | 英文全称 |
| cnspell | VARCHAR(50) | 拼音缩写 |
| market | VARCHAR(20) | 市场类型（主板/创业板/科创板/CDR/北交所） |

*... 还有 10 个字段*

### tu_daily_basic

**主要字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT | 自增主键 |
| ts_code | VARCHAR(10) | TS股票代码 |
| trade_date | VARCHAR(8) | 交易日期 |
| close | FLOAT | 当日收盘价 |
| turnover_rate | FLOAT | 换手率（%） |
| turnover_rate_f | FLOAT | 换手率（自由流通股） |
| volume_ratio | FLOAT | 量比 |
| pe | FLOAT | 市盈率（总市值/净利润） |
| pe_ttm | FLOAT | 市盈率（TTM） |
| pb | FLOAT | 市净率（总市值/净资产） |

*... 还有 10 个字段*

### tu_income

**主要字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT | 自增主键 |
| ts_code | VARCHAR(10) | TS代码 |
| ann_date | VARCHAR(8) | 公告日期 |
| f_ann_date | VARCHAR(8) | 实际公告日期 |
| end_date | VARCHAR(8) | 报告期 |
| report_type | VARCHAR(2) | 报告类型 |
| comp_type | VARCHAR(1) | 公司类型(1一般工商业2银行3保险4证券) |
| end_type | VARCHAR(10) | 报告期类型 |
| basic_eps | FLOAT | 基本每股收益 |
| diluted_eps | FLOAT | 稀释每股收益 |

*... 还有 73 个字段*

### tu_fina_indicator

**主要字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT | 自增主键 |
| ts_code | VARCHAR(10) | TS代码 |
| ann_date | VARCHAR(8) | 公告日期 |
| end_date | VARCHAR(8) | 报告期 |
| eps | FLOAT | 基本每股收益 |
| dt_eps | FLOAT | 稀释每股收益 |
| bps | FLOAT | 每股净资产 |
| ocfps | FLOAT | 每股经营活动产生的现金流量净额 |
| cfps | FLOAT | 每股现金流量净额 |
| roe | FLOAT | 净资产收益率 |

*... 还有 49 个字段*

## 改进建议
1. tu_daily_basic 的数据已经 6 天未更新
2. tu_daily_basic 的数据已经 6 天未更新
3. tu_daily_detail 的数据已经 2 天未更新
4. tu_moneyflow_ind_dc 表的字段注释覆盖率仅 0.0%