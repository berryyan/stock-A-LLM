# SQL Agent字段名称修复总结

## 问题描述
在运行`test_sql_fixes_quick.py`时发现50%的测试失败，错误信息显示：
- `❌ 失败: 查询执行失败: 'n_income'`
- `❌ 失败: 查询执行失败: 'net_mf_amount'`

## 根本原因
SQL模板与实际代码中使用的字段名称不一致：

1. **利润查询问题**：
   - SQL模板使用别名: `i.n_income as net_profit`
   - 代码访问字段: `row['n_income']` (应该是 `row['net_profit']`)
   - 缺少字段: `basic_eps` 未在SQL中查询

2. **资金流向问题**：
   - 实际字段名: `net_amount` (主力资金净流入)
   - 错误引用: `row['net_mf_amount']` 

## 修复内容

### 1. 修复利润查询字段访问
**文件**: `agents/sql_agent_modular.py` (第649-659行)
```python
# 处理可能存在的字段名问题
revenue = row.get('revenue', 0) or 0
net_profit = row.get('net_profit', row.get('n_income', 0)) or 0
basic_eps = row.get('basic_eps', 0) or 0
```

### 2. 添加缺失的basic_eps字段
**文件**: `utils/sql_templates.py` (PROFIT_LATEST模板)
```sql
SELECT 
    i.ts_code,
    s.name,
    i.end_date,
    i.revenue,
    i.n_income as net_profit,
    i.n_income_attr_p as net_profit_attr_p,
    i.basic_eps,  -- 新增字段
    i.report_type,
    ...
```

### 3. 修复资金流向字段名称
**文件**: `agents/sql_agent_modular.py` (第999行)
```python
# 修改前: f"{row['net_mf_amount'] / 10000:.2f}"
# 修改后: f"{row['net_amount'] / 10000:.2f}"
```

## 数据库字段说明

### tu_income表（利润表）
- `revenue` - 营业收入
- `n_income` - 净利润
- `basic_eps` - 基本每股收益

### tu_moneyflow_dc表（资金流向）
- `net_amount` - 主力资金净流入额（超大单+大单）
- `buy_elg_amount` - 超大单买入额
- `buy_lg_amount` - 大单买入额
- `pct_change` - 涨跌幅

## 验证测试

创建了两个测试脚本：
1. `test_sql_fixes_v2.py` - 详细测试字段修复效果
2. 原有的 `test_sql_fixes_quick.py` - 快速验证

## 预期结果

修复后，以下查询应该能正常工作：
- ✅ 贵州茅台的利润
- ✅ 中国平安最新净利润  
- ✅ 主力净流入排名前10
- ✅ 主力净流出排名前10
- ✅ 万科A6月的K线
- ✅ PE最高的10只股票

## 注意事项

1. **字段别名一致性**：确保SQL模板中的别名与代码中的字段访问一致
2. **防御性编程**：使用`row.get()`方法并提供默认值，避免KeyError
3. **字段兼容性**：同时支持原字段名和别名，提高代码健壮性