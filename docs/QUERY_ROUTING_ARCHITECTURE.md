# 查询路由架构说明

## 概述

系统采用三层缓存架构处理中文自然语言查询，实现高效的查询理解和路由。

## 三层缓存架构

### 第一层：股票代码映射缓存（StockCodeMapper）
- **缓存内容**: 22,554个股票名称/代码 → ts_code映射
- **数据来源**: tu_stock_basic表
- **缓存时间**: 60分钟
- **功能**: 
  - "贵州茅台" → "600519.SH"
  - "茅台" → "600519.SH"
  - "600519" → "600519.SH"

### 第二层：数据库Schema缓存（SchemaCacheManager）
- **缓存内容**: 
  - 14个表的中英文映射
  - 535个字段的中英文映射
  - 字段类型、单位等元数据
- **数据来源**: INFORMATION_SCHEMA
- **缓存时间**: 60分钟
- **功能**:
  - 表名映射: "A股日线行情数据表" → "tu_daily_detail"
  - 字段映射: "收盘价" → "close"，"成交量" → "vol"

### 第三层：查询结果缓存（各Agent内部）
- **缓存内容**: 查询结果
- **缓存时间**: 根据查询类型不同
- **功能**: 相同查询直接返回缓存结果

## 查询处理流程

```
用户输入: "查询贵州茅台最新股价"
    ↓
[Hybrid Agent]
    ↓
[ChineseQueryParser] ← 使用 SchemaCacheManager
    ├─ 查询类型识别: stock_price
    ├─ 表映射: "日线行情" → "tu_daily_detail"
    ├─ 股票映射: "贵州茅台" → "600519.SH" ← 使用 StockCodeMapper
    ├─ 字段映射: ["收盘价", "成交量"] → ["close", "vol"]
    └─ 时间解析: "最新" → 最近交易日
    ↓
[路由决策]
    ├─ SQL查询: 结构化数据查询
    ├─ RAG查询: 文档检索
    ├─ 财务分析: 专业财务分析
    └─ 资金流向: 资金流向分析
    ↓
[SQL Agent] → 执行SQL查询
    ↓
返回结果
```

## 详细示例

### 1. 简单股价查询

**输入**: "查询茅台最新股价"

**解析过程**:
```python
# ChineseQueryParser.parse_query()
{
    "query_type": "stock_price",
    "tables": ["tu_daily_detail"],  # Schema缓存提供
    "fields": ["open", "high", "low", "close", "vol", "amount"],  # 默认字段
    "conditions": {
        "ts_code": "600519.SH",  # StockCodeMapper提供
        "days": 0  # 最新 = 0天
    }
}
```

**生成SQL**:
```sql
SELECT open, high, low, close, vol, amount 
FROM tu_daily_detail 
WHERE ts_code = '600519.SH' 
  AND trade_date >= DATE_SUB(CURDATE(), INTERVAL 0 DAY)
```

### 2. 复杂财务查询

**输入**: "分析平安银行最近5期的营业收入和净利润"

**解析过程**:
```python
{
    "query_type": "financial",
    "tables": ["tu_income"],  # Schema缓存: "利润表" → "tu_income"
    "fields": ["revenue", "n_income"],  # Schema缓存: "营业收入" → "revenue"
    "conditions": {
        "ts_code": "000001.SZ",  # StockCodeMapper: "平安银行" → "000001.SZ"
        "periods": 5
    }
}
```

### 3. 资金流向查询

**输入**: "茅台今天的主力资金流向"

**解析过程**:
```python
{
    "query_type": "money_flow",
    "tables": ["tu_moneyflow_dc"],  # Schema缓存提供
    "fields": ["buy_elg_vol", "sell_elg_vol", "net_mf_vol"],  # 主力资金字段
    "conditions": {
        "ts_code": "600519.SH",
        "days": 0  # 今天
    }
}
```

## 性能优化

### 缓存命中率
- StockCodeMapper: >95%（股票名称相对固定）
- SchemaCacheManager: 100%（表结构很少变化）
- 查询结果缓存: 约30%（查询多样性高）

### 响应时间
1. **缓存命中时**: <10ms
2. **缓存未命中**:
   - StockCodeMapper刷新: ~500ms（查询22K条记录）
   - SchemaCacheManager刷新: ~1s（查询元数据）
3. **端到端查询**: 50-200ms（不含LLM调用）

### 内存使用
- StockCodeMapper: ~5MB
- SchemaCacheManager: ~2MB
- 总内存占用: <10MB

## 扩展性设计

### 1. 新增查询类型
在ChineseQueryParser中添加新的查询模式：
```python
'new_type': {
    'keywords': ['关键词1', '关键词2'],
    'patterns': [r'正则模式'],
    'default_table': '默认表名',
    'default_fields': ['默认字段列表']
}
```

### 2. 自定义字段映射
如果数据库字段注释不标准，可以在SchemaCacheManager中添加特殊处理：
```python
# 在_parse_comment方法中添加特殊规则
if field_name == 'special_field':
    return {'name': '特殊中文名', 'unit': '单位'}
```

### 3. 同义词支持
可以在StockCodeMapper中添加同义词映射：
```python
# 常见别名映射
self.aliases = {
    '茅台': '贵州茅台',
    '平安': '平安银行',
    '万科': '万科A'
}
```

## 监控和维护

### 关键指标
1. 缓存命中率
2. 查询解析成功率
3. 平均响应时间
4. 内存使用量

### 日志位置
- StockCodeMapper: `logs/stock_code_mapper.log`
- SchemaCacheManager: `logs/mysql_connector.log`
- ChineseQueryParser: `logs/hybrid_agent.log`

### 维护建议
1. 定期检查缓存命中率，低于80%时分析原因
2. 监控新股票上市，确保映射及时更新
3. 数据库表结构变更时，清理Schema缓存
4. 定期分析查询日志，优化常见查询模式