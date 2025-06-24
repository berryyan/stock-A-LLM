# MySQL数据库结构详细分析报告

**分析日期**: 2025-06-22  
**数据库**: Tushare  
**分析表数**: 14个核心表  
**总记录数**: 28,000,000+ 条  

## 📊 数据库整体概况

### 数据规模统计
- **总记录数**: 28,098,646 条
- **总字段数**: 517 个字段
- **平均每表记录数**: 2,007,046 条
- **平均每表字段数**: 37 个字段

### 表规模排序
1. **tu_daily_detail** (日线行情): 15,643,471 条 (13字段)
2. **tu_daily_basic** (每日基本面): 6,308,521 条 (20字段)
3. **tu_moneyflow_dc** (资金流向): 2,411,419 条 (16字段)
4. **tu_anns_d** (公告数据): 2,097,794 条 (7字段)
5. **tu_irm_qa_sz** (深交所互动): 497,656 条 (9字段)
6. **tu_irm_qa_sh** (上交所互动): 200,261 条 (9字段)
7. **tu_fina_indicator** (财务指标): 137,888 条 (143字段)
8. **tu_income** (利润表): 128,932 条 (83字段)
9. **tu_balancesheet** (资产负债表): 126,652 条 (161字段)
10. **tu_cashflow** (现金流量表): 121,840 条 (73字段)

## 🏗️ 详细表结构分析

### 1. 基础信息表 (tu_stock_basic)
**记录数**: 5,418 条  
**字段数**: 20 个  
**用途**: 股票基本信息维表

#### 关键字段分析
- **ts_code** (TS代码): 主要股票标识符，格式如000001.SZ
- **symbol** (股票代码): 6位数字代码
- **name** (股票名称): 中文股票名称
- **area** (地域): 公司注册地域
- **industry** (所属行业): 行业分类信息
- **market** (市场类型): 主板/创业板/科创板/CDR/北交所
- **exchange** (交易所代码): 交易所标识
- **list_status** (上市状态): L上市 D退市 P暂停上市
- **list_date** (上市日期): YYYYMMDD格式
- **is_hs** (沪深港通): N否 H沪股通 S深股通

#### 数据特点
- 覆盖5,418只股票
- 上市日期范围: 1990-12-19 至 2025-06-12
- 支持多个交易所和市场板块

### 2. 交易数据表

#### 2.1 日线行情表 (tu_daily_detail)
**记录数**: 15,643,471 条  
**字段数**: 13 个  
**用途**: 每日价格和成交数据

**核心字段**:
- **ts_code**: 股票代码
- **trade_date**: 交易日期 (2000-01-04 至 2025-06-20)
- **open/high/low/close**: 开高低收价格
- **pre_close**: 昨收价（前复权）
- **change**: 涨跌额
- **pct_chg**: 涨跌幅（基于除权后计算）
- **vol**: 成交量（手）
- **amount**: 成交额（千元）
- **vwap**: 成交加权平均价

#### 2.2 每日基本面表 (tu_daily_basic)
**记录数**: 6,308,521 条  
**字段数**: 20 个  
**用途**: 每日估值和基本面指标

**核心字段**:
- **turnover_rate**: 换手率（%）
- **turnover_rate_f**: 换手率（自由流通股）
- **volume_ratio**: 量比
- **pe**: 市盈率（总市值/净利润）
- **pe_ttm**: 市盈率（TTM）
- **pb**: 市净率（总市值/净资产）
- **ps/ps_ttm**: 市销率
- **dv_ratio/dv_ttm**: 股息率
- **total_share**: 总股本（万股）
- **float_share**: 流通股本（万股）
- **free_share**: 自由流通股本（万股）
- **total_mv**: 总市值（万元）
- **circ_mv**: 流通市值（万元）

### 3. 财务报表数据

#### 3.1 利润表 (tu_income)
**记录数**: 128,932 条  
**字段数**: 83 个  
**用途**: 损益表完整数据

**关键收入字段**:
- **total_revenue**: 营业总收入
- **revenue**: 营业收入
- **int_income**: 利息收入
- **comm_income**: 手续费及佣金收入
- **invest_income**: 投资净收益
- **oth_b_income**: 其他业务净收益

**关键成本费用字段**:
- **total_cogs**: 营业总成本
- **oper_cost**: 营业成本
- **sell_exp**: 销售费用
- **admin_exp**: 管理费用
- **fin_exp**: 财务费用
- **rd_exp**: 研发费用

**关键利润字段**:
- **operate_profit**: 营业利润
- **total_profit**: 利润总额
- **n_income**: 净利润（含少数股东损益）
- **n_income_attr_p**: 净利润（不含少数股东损益）
- **basic_eps**: 基本每股收益
- **diluted_eps**: 稀释每股收益

#### 3.2 资产负债表 (tu_balancesheet)
**记录数**: 126,652 条  
**字段数**: 161 个  
**用途**: 资产负债表完整数据

**资产类字段**:
- **money_cap**: 货币资金
- **accounts_receiv**: 应收账款
- **inventories**: 存货
- **total_cur_assets**: 流动资产合计
- **fix_assets**: 固定资产
- **total_assets**: 资产总计

**负债类字段**:
- **st_borr**: 短期借款
- **accounts_pay**: 应付账款
- **total_cur_liab**: 流动负债合计
- **lt_borr**: 长期借款
- **total_liab**: 负债合计

**权益类字段**:
- **total_share**: 期末总股本
- **cap_rese**: 资本公积金
- **surplus_rese**: 盈余公积金
- **undistr_porfit**: 未分配利润
- **total_hldr_eqy_inc_min_int**: 股东权益合计

#### 3.3 现金流量表 (tu_cashflow)
**记录数**: 121,840 条  
**字段数**: 73 个  
**用途**: 现金流量表完整数据

**经营活动现金流**:
- **c_fr_sale_sg**: 销售商品、提供劳务收到的现金
- **c_paid_goods_s**: 购买商品、接受劳务支付的现金
- **c_paid_to_for_empl**: 支付给职工以及为职工支付的现金
- **n_cashflow_act**: 经营活动产生的现金流量净额

**投资活动现金流**:
- **c_disp_withdrwl_invest**: 收回投资收到的现金
- **c_recp_return_invest**: 取得投资收益收到的现金
- **c_pay_acq_const_fiolta**: 购建固定资产、无形资产和其他长期资产支付的现金
- **n_cashflow_inv_act**: 投资活动产生的现金流量净额

**筹资活动现金流**:
- **c_proc_borrow**: 取得借款收到的现金
- **c_prepay_amt_borr**: 偿还债务支付的现金
- **c_pay_dist_dpcp_int_exp**: 分配股利、利润或偿付利息支付的现金
- **n_cash_flows_fnc_act**: 筹资活动产生的现金流量净额

#### 3.4 财务指标表 (tu_fina_indicator)
**记录数**: 137,888 条  
**字段数**: 143 个  
**用途**: 计算好的财务指标

**盈利能力指标**:
- **roe**: 净资产收益率
- **roe_waa**: 加权平均净资产收益率
- **roe_dt**: 净资产收益率(扣除非经常损益)
- **roa**: 总资产报酬率
- **roa2**: 总资产净利润率

**运营能力指标**:
- **turn_days**: 营业周期
- **rece_turn_days**: 应收账款周转天数
- **inv_turn_days**: 存货周转天数
- **ar_turn**: 应收账款周转率
- **inv_turn**: 存货周转率

**偿债能力指标**:
- **debt_to_assets**: 资产负债率
- **assets_to_eqt**: 权益乘数
- **dp_assets_to_eqt**: 权益乘数(杜邦分析)
- **current_ratio**: 流动比率
- **quick_ratio**: 速动比率

### 4. 公告和互动数据

#### 4.1 公告数据表 (tu_anns_d)
**记录数**: 2,097,794 条  
**字段数**: 7 个  

**关键字段**:
- **ann_date**: 公告日期
- **ts_code**: 股票代码
- **name**: 公司名称
- **title**: 公告标题
- **url**: 公告链接
- **rec_time**: 录入时间

#### 4.2 资金流向表 (tu_moneyflow_dc)
**记录数**: 2,411,419 条  
**字段数**: 16 个  

**关键字段**:
- **trade_date**: 交易日期
- **ts_code**: 股票代码
- **buy_sm_amount**: 小单买入金额（万元）
- **buy_md_amount**: 中单买入金额（万元）
- **buy_lg_amount**: 大单买入金额（万元）
- **buy_elg_amount**: 特大单买入金额（万元）
- **net_mf_amount**: 净流入金额（万元）

## 🔗 业务关系分析

### 核心关联字段
1. **ts_code**: 13个表包含，是主要的股票标识符
2. **trade_date**: 3个表包含，用于交易数据关联
3. **ann_date**: 4个表包含，用于公告和财务数据关联
4. **end_date**: 4个表包含，用于财务报告期关联

### 业务分类统计
- **基础信息**: 1个表，5,418条记录
- **交易数据**: 4个表，24,470,225条记录
- **财务数据**: 4个表，515,312条记录
- **公告信息**: 2个表，2,135,143条记录
- **互动数据**: 2个表，697,917条记录

## 🎯 数据库能力评估

### 数据完整性
✅ **股票覆盖**: 5,400+只股票，覆盖全市场  
✅ **时间跨度**: 2000年至今，支持长期历史分析  
✅ **数据频率**: 日级别数据，满足大部分分析需求  
✅ **财务完整性**: 三大报表+财务指标，支持全面基本面分析  

### 查询能力支持

#### 1. 技术面分析能力 (⭐⭐⭐⭐⭐)
- **价格数据**: 完整的OHLC数据，支持K线分析
- **成交数据**: 成交量、成交额、成交加权价
- **基本面指标**: PE、PB、PS等估值指标
- **资金流向**: 大中小单资金流向数据
- **时间跨度**: 25年历史数据，支持长期技术分析

#### 2. 基本面分析能力 (⭐⭐⭐⭐⭐)
- **三大报表**: 利润表、资产负债表、现金流量表完整数据
- **财务指标**: 143个计算好的财务指标
- **多期对比**: 支持同比、环比、多年趋势分析
- **行业对比**: 有行业分类，支持同行业对比
- **数据质量**: 字段注释完整，含义明确

#### 3. 事件驱动分析能力 (⭐⭐⭐⭐)
- **公告数据**: 200万+公告记录
- **互动数据**: 投资者关系互动平台数据
- **时效性**: 公告数据及时更新
- **内容丰富**: 包含公告标题和链接

#### 4. 综合分析能力 (⭐⭐⭐⭐⭐)
- **多维关联**: 通过ts_code可关联所有表
- **时间对齐**: 通过各类日期字段支持时间序列分析
- **数据规模**: 足够支持大规模统计分析
- **实时性**: 数据更新及时（T+1或T+2）

## 🚀 基于数据结构的开发建议

### 1. 立即可开发的高价值功能

#### A. 财务分析增强 (基于财务四表)
```sql
-- 示例：多期财务对比分析
SELECT 
    ts_code,
    end_date,
    total_revenue,
    n_income_attr_p,
    total_assets,
    total_liab
FROM tu_income i
JOIN tu_balancesheet b USING(ts_code, end_date)
WHERE ts_code = '000001.SZ' 
ORDER BY end_date DESC;
```

#### B. 技术指标计算 (基于日线数据)
```sql
-- 示例：计算移动平均线
SELECT 
    ts_code,
    trade_date,
    close,
    AVG(close) OVER (PARTITION BY ts_code ORDER BY trade_date ROWS 4 PRECEDING) as MA5,
    AVG(close) OVER (PARTITION BY ts_code ORDER BY trade_date ROWS 19 PRECEDING) as MA20
FROM tu_daily_detail 
WHERE ts_code = '000001.SZ'
ORDER BY trade_date DESC;
```

#### C. 估值分析 (基于基本面数据)
```sql
-- 示例：PE/PB历史分位数分析
SELECT 
    ts_code,
    trade_date,
    pe,
    pb,
    PERCENT_RANK() OVER (PARTITION BY ts_code ORDER BY pe) as pe_percentile,
    PERCENT_RANK() OVER (PARTITION BY ts_code ORDER BY pb) as pb_percentile
FROM tu_daily_basic 
WHERE ts_code = '000001.SZ';
```

### 2. 推荐的开发优先级

**Phase 1: 财务分析增强** (2周)
- 基于tu_income, tu_balancesheet, tu_cashflow, tu_fina_indicator
- 实现ROE分解、现金流分析、营收结构分析等

**Phase 2: 技术面分析** (2周)  
- 基于tu_daily_detail, tu_daily_basic
- 实现技术指标计算、形态识别、信号系统等

**Phase 3: 估值分析系统** (1-2周)
- 基于tu_daily_basic结合财务数据
- 实现历史估值分位数、相对估值等

**Phase 4: 资金流向分析** (1周)
- 基于tu_moneyflow_dc, tu_moneyflow_ind_dc
- 实现主力资金监控、资金流向趋势等

现在我已经完全掌握了数据库的详细结构，可以基于实际的字段和数据设计精确的查询功能！