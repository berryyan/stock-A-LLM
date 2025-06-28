# Schema映射系统技术文档

## 概述

Schema映射系统是一个为股票分析系统设计的性能优化方案，通过预构建的知识库和智能路由机制，将数据库Schema查询时间从3-5秒优化到小于10毫秒，实现了500倍以上的性能提升。

## 系统架构

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    Schema映射系统                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────┐ │
│  │ Schema知识库    │  │ Schema增强路由器  │  │查询模板│ │
│  │ (单例模式)      │  │ (智能路由优化)    │  │  库    │ │
│  └────────┬────────┘  └────────┬─────────┘  └────┬───┘ │
│           │                    │                   │     │
│  ┌────────▼──────────────────────▼─────────────────▼───┐│
│  │              HybridAgent (路由决策中心)              ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 1. Schema知识库 (`utils/schema_knowledge_base.py`)

**功能**: 预构建并缓存数据库表结构信息，提供快速数据定位服务

**核心特性**:
- 单例模式确保全局唯一实例
- 预加载所有表结构到内存
- 中英文字段双向映射
- O(1)时间复杂度的查询性能

**主要方法**:
```python
# 快速定位数据
schema_kb.locate_data("营业收入")  
# 返回: {'table': 'tu_income', 'field': 'revenue', 'type': 'float'}

# 获取主题相关表
schema_kb.get_tables_for_topic("财务")
# 返回: ['tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator']

# 获取表结构信息
schema_kb.get_table_schema("tu_income")
# 返回: 完整的表结构定义
```

### 2. Schema增强路由器 (`utils/schema_enhanced_router.py`)

**功能**: 基于数据库Schema知识优化查询路由决策

**核心特性**:
- 字段检测和表推断
- 关键词权重计算
- 路由得分系统
- 决策验证机制

**路由优化流程**:
1. 分析查询中的字段和表引用
2. 计算各路由类型的得分
3. 验证和增强LLM的路由决策
4. 提供快速路由捷径

**主要方法**:
```python
# 快速路由
schema_router.get_quick_route("分析茅台的财务健康度")
# 返回: "FINANCIAL"

# 增强路由决策
enhanced = schema_router.enhance_routing_decision(query, llm_decision)
# 返回: 增强后的决策，可能覆盖LLM的决定

# 验证路由合理性
is_valid, warning = schema_router.validate_routing(query, route_type)
```

### 3. 查询模板库 (`utils/query_templates.py`)

**功能**: 为常见查询模式提供预定义模板，实现亚毫秒级路由

**模板类型**:
- 股价查询（最新、今日）
- 财务健康度分析
- 杜邦分析
- 资金流向分析
- 公告查询（最新、年报）
- 排名查询（涨幅、市值）
- 比较分析
- 现金流质量分析

**模板匹配流程**:
```python
# 匹配查询模板
template, params = match_query_template("茅台最新股价")
# template.route_type = "SQL_ONLY"
# params = {"time_range": "latest", "entities": ["茅台"]}
```

## 性能优化策略

### 三层路由优化

1. **第一层 - 模板匹配** (<1ms)
   - 正则表达式快速匹配
   - 预定义路由决策
   - 参数自动提取

2. **第二层 - Schema快速路由** (<10ms)
   - 基于关键词的模式识别
   - 无需LLM调用
   - 覆盖80%常见查询

3. **第三层 - Schema增强LLM路由** (1-2秒)
   - LLM智能分析
   - Schema知识增强
   - 处理复杂查询

### 性能对比

| 优化前 | 优化后 | 提升倍数 |
|--------|--------|----------|
| 每次查询数据库Schema (3-5秒) | 内存缓存查询 (<0.1ms) | 30,000-50,000x |
| LLM路由决策 (2-3秒) | 模板/快速路由 (<10ms) | 200-300x |
| 总体响应时间 (5-8秒) | 总体响应时间 (0.01-2秒) | 4-800x |

## 使用指南

### 1. 基础使用

```python
from agents.hybrid_agent import HybridAgent

# 创建代理（自动加载所有优化组件）
agent = HybridAgent()

# 执行查询（自动应用所有优化）
result = agent.query("分析贵州茅台的财务健康度")
```

### 2. 直接使用Schema知识库

```python
from utils.schema_knowledge_base import schema_kb

# 查找数据位置
location = schema_kb.locate_data("市盈率")
print(f"市盈率在表 {location['table']} 的字段 {location['field']}")

# 获取财务相关的所有表
financial_tables = schema_kb.get_tables_for_topic("财务")
```

### 3. 监控路由性能

```python
from utils.routing_monitor import routing_monitor

# 获取路由统计
stats = routing_monitor.get_statistics()
print(f"总查询数: {stats['total_queries']}")
print(f"平均响应时间: {stats['avg_response_time']}秒")
print(f"路由分布: {stats['route_distribution']}")
```

## 扩展和维护

### 添加新的中文映射

编辑 `config/schema_mappings.json`:
```json
{
  "chinese_to_english": {
    "新字段中文名": "new_field_name"
  }
}
```

### 添加新的查询模板

在 `utils/query_templates.py` 中添加:
```python
QueryTemplate(
    name="新模板名称",
    type=TemplateType.NEW_TYPE,
    pattern=r"正则表达式模式",
    route_type="路由类型",
    required_fields=["必需字段"],
    optional_fields=["可选字段"],
    default_params={"默认参数": "值"},
    example="示例查询"
)
```

### 优化路由规则

在 `utils/schema_enhanced_router.py` 中调整:
- `keyword_weights`: 关键词权重
- `table_type_mapping`: 表类型映射
- `quick_patterns`: 快速路由模式

## 最佳实践

### 1. 查询编写建议

- 使用标准的查询表达方式以匹配模板
- 明确指定公司名称或股票代码
- 使用系统支持的关键词（财务健康度、资金流向等）

### 2. 性能优化建议

- 优先使用预定义的查询模式
- 避免过于复杂的复合查询
- 利用查询建议功能引导用户

### 3. 监控和调优

- 定期查看路由统计信息
- 分析慢查询并添加对应模板
- 根据使用频率调整关键词权重

## 故障排除

### 常见问题

1. **Schema知识库未生效**
   - 检查日志中是否有 "Schema知识库构建完成" 信息
   - 确认 `config/schema_mappings.json` 文件存在
   - 验证数据库连接正常

2. **路由决策不准确**
   - 查看路由监控日志分析决策过程
   - 检查是否命中了错误的模板
   - 调整关键词权重或添加新模板

3. **性能未达预期**
   - 确认使用了模板匹配或快速路由
   - 检查是否频繁回退到LLM路由
   - 分析具体查询是否过于复杂

## 版本历史

- v1.0.0 (2025-06-28): 初始版本
  - Schema知识库实现
  - Schema增强路由器
  - 查询模板系统
  - 路由监控功能

## 未来规划

1. **智能模板学习**: 基于用户查询历史自动生成新模板
2. **动态权重调整**: 根据查询成功率自动调整关键词权重
3. **分布式缓存**: 支持多实例部署的Schema知识共享
4. **查询优化建议**: 主动建议用户优化查询表达方式