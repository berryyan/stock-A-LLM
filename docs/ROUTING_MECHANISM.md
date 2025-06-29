# 股票分析系统路由机制文档

## 1. 概述

本文档详细说明股票分析系统v2.1.1的智能路由机制实现，包括路由优先级、具体实现逻辑、文件位置、测试用例以及7个Agent的具体定位。

## 2. 路由优先级体系

系统采用5级优先级路由机制，从高到低依次为：

### 2.1 触发词路由（最高优先级）

**实现位置**: `agents/hybrid_agent.py:397-407` (_check_trigger_words方法)
**配置文件**: `config/routing_config.py:15-19`

```python
TRIGGER_WORDS = {
    "排行分析：": "rank",
    "查询公告：": "anns", 
    "董秘互动：": "qa"
}
```

**工作原理**:
- 检查查询是否以特定触发词开头
- 匹配后直接返回对应的查询类型
- 置信度固定为1.0

**测试用例**:
```python
"排行分析：今日涨幅前10" → rank
"查询公告：贵州茅台最新年报" → anns
"董秘互动：公司对AI技术的看法" → qa
```

### 2.2 模板匹配路由（第二优先级）

**实现位置**: 
- `agents/hybrid_agent.py:409-436` (_check_template_route方法)
- `utils/query_templates.py:337-445` (match_query_template函数)

**配置文件**: `config/routing_config.py:33-39` (TEMPLATE_ROUTE_OVERRIDE)

```python
TEMPLATE_ROUTE_OVERRIDE = {
    "涨幅排名": "rank",
    "市值排名": "rank",
    "总市值排名": "rank",
    "流通市值排名": "rank",
    "最新公告": "anns",
}
```

**工作原理**:
1. 使用正则表达式匹配预定义模板
2. 检查是否需要路由覆盖
3. 提取查询参数和实体
4. 返回路由类型和提取的参数

**模板定义示例** (`utils/query_templates.py:50-62`):
```python
QueryTemplate(
    name="最新股价查询",
    type=TemplateType.PRICE_QUERY,
    pattern=r"(.+?)(?:的)?最新股价",
    route_type="SQL_ONLY",
    required_fields=["close", "trade_date"],
    optional_fields=["change", "pct_chg", "vol"],
    default_params={
        "time_range": "latest",
        "metrics": ["close", "change", "pct_chg"]
    },
    example="茅台最新股价"
)
```

### 2.3 Schema快速路由（第三优先级）

**实现位置**: `agents/hybrid_agent.py:438-455`
**依赖文件**: `utils/schema_enhanced_router.py`

**工作原理**:
- 利用预加载的数据库Schema信息
- 快速模式匹配（<10ms响应）
- 验证路由决策的合理性
- 提供警告信息辅助调试

### 2.4 LLM智能路由（第四优先级）

**实现位置**: `agents/hybrid_agent.py:457-487`
**模型配置**: 使用DeepSeek模型进行智能分析

**查询模式定义** (`agents/hybrid_agent.py:124-210`):
```python
query_patterns = {
    "sql_patterns": [
        "股票价格", "市值", "涨跌幅", "成交量", "市盈率", "市净率",
        "技术指标", "K线", "均线", "排名", "统计", "比较"
    ],
    "rag_patterns": [
        "公告内容", "年报", "季报", "管理层分析", "经营计划",
        "风险提示", "业务介绍", "公司战略", "行业地位"
    ],
    # ... 更多模式
}
```

**工作流程**:
1. 构建分析提示词
2. LLM分析查询意图
3. 返回JSON格式路由决策
4. Schema增强最终决策

### 2.5 规则路由（最低优先级）

**实现位置**: `agents/hybrid_agent.py:494-584` (_rule_based_routing方法)

**评分机制**:
```python
# 优先级从高到低
1. Rank查询 (lines 555-556)
2. QA查询 (lines 557-558)
3. ANNS查询 (lines 559-560)
4. Money Flow分析 (lines 561-562)
5. Financial分析 (lines 563-564)
6. SQL/RAG独占 (lines 565-568)
7. SQL_FIRST/RAG_FIRST (lines 569-572)
8. PARALLEL默认 (lines 573-574)
```

## 3. 7个Agent定位与职责

### 3.1 SQL Agent
**定位**: 基础数据查询
**职责**: 
- 股票价格、成交量、市值查询
- 简单财务指标（PE、PB）
- 基础统计和排序
- K线、均线等技术数据

**典型查询**:
- "茅台最新股价"
- "今日成交量前10"
- "贵州茅台市盈率"

### 3.2 RAG Agent
**定位**: 文档内容搜索
**职责**:
- 公告内容搜索
- 年报、季报文本分析
- 管理层讨论与分析
- 定性信息提取

**典型查询**:
- "茅台年报中关于白酒行业的分析"
- "公司对未来发展的规划"
- "管理层对市场竞争的看法"

### 3.3 Financial Agent
**定位**: 专业财务分析
**职责**:
- 财务健康度评分
- 杜邦分析（ROE分解）
- 现金流质量评估
- 多期财务对比

**典型查询**:
- "分析贵州茅台的财务健康度"
- "平安银行的杜邦分析"
- "万科的现金流质量"

### 3.4 MoneyFlow Agent
**定位**: 资金流向分析
**职责**:
- 主力资金动向
- 超大单行为分析
- 四级资金分布
- 机构资金追踪

**典型查询**:
- "茅台的资金流向如何"
- "今日主力净流入前10"
- "超大单买入最多的股票"

### 3.5 Rank Agent（新增）
**定位**: 专业排名分析
**职责**:
- 涨跌幅排行榜
- 市值排名（总市值、流通市值）
- 板块/行业排名
- ST股票过滤
- 多维度排序

**典型查询**:
- "排行分析：今日涨幅前20（排除ST）"
- "A股市值最大的50只股票"
- "银行板块涨幅排行"

### 3.6 ANNS Agent（新增）
**定位**: 公告元数据查询
**职责**:
- 公告列表查询
- 公告发布时间
- 公告类型分类
- 公告统计分析

**典型查询**:
- "查询公告：贵州茅台最近30天的公告"
- "平安银行2024年发布了多少公告"
- "最新发布公告的10家公司"

### 3.7 QA Agent（新增）
**定位**: 董秘互动查询
**职责**:
- 投资者提问记录
- 公司回复内容
- 互动频率统计
- 热点问题追踪

**典型查询**:
- "董秘互动：投资者最关心的问题"
- "公司对扩产计划的回复"
- "近期互动最活跃的公司"

## 4. 实现文件位置

### 核心文件
- **主路由逻辑**: `agents/hybrid_agent.py`
- **路由配置**: `config/routing_config.py`
- **模板库**: `utils/query_templates.py`
- **Schema路由**: `utils/schema_enhanced_router.py`
- **股票代码映射**: `utils/stock_code_mapper.py`

### Agent实现
- **SQL Agent**: `agents/sql_agent.py`
- **RAG Agent**: `agents/rag_agent.py`
- **Financial Agent**: `agents/financial_agent.py`
- **MoneyFlow Agent**: `agents/money_flow_agent.py`
- **Rank Agent**: `agents/rank_agent.py` (待实现)
- **ANNS Agent**: `agents/anns_agent.py` (待实现)
- **QA Agent**: `agents/qa_agent.py` (待实现)

## 5. 测试用例

### 5.1 触发词测试
```python
test_cases = [
    ("排行分析：今日涨幅前10", "rank"),
    ("查询公告：茅台最新公告", "anns"),
    ("董秘互动：扩产计划", "qa"),
]
```

### 5.2 模板匹配测试
```python
test_cases = [
    ("茅台最新股价", "sql"),
    ("贵州茅台的财务健康度", "financial"),
    ("茅台的资金流向", "money_flow"),
    ("总市值最大的前20只股票", "rank"),  # Override生效
]
```

### 5.3 复杂查询测试
```python
test_cases = [
    ("分析茅台和五粮液的财务对比", "parallel"),
    ("茅台最新股价和公告内容", "sql_first"),
    ("解释茅台的商业模式并分析财务表现", "rag_first"),
]
```

### 5.4 测试脚本位置
- **基础路由测试**: `test_enhanced_routing.py`
- **模板匹配测试**: `utils/query_templates.py:454-492`
- **综合测试**: `comprehensive_routing_test.py`

## 6. 路由决策流程图

```
查询输入
    ↓
[触发词检查] → 匹配? → 返回对应类型
    ↓ 不匹配
[模板匹配] → 匹配? → 检查Override → 返回路由类型
    ↓ 不匹配
[Schema快速路由] → 匹配? → 验证 → 返回路由类型
    ↓ 不匹配
[LLM智能分析] → 成功? → Schema增强 → 返回路由类型
    ↓ 失败
[规则路由] → 关键词评分 → 返回默认路由
```

## 7. 更新迭代指南

### 7.1 添加新的触发词
1. 编辑 `config/routing_config.py`
2. 在 `TRIGGER_WORDS` 字典中添加新映射
3. 更新测试用例

### 7.2 添加新的查询模板
1. 编辑 `utils/query_templates.py`
2. 在 `_build_templates()` 方法中添加新模板
3. 定义pattern、fields、params等
4. 添加到相应的TemplateType

### 7.3 调整路由优先级
1. 编辑 `agents/hybrid_agent.py`
2. 修改 `_rule_based_routing` 中的评分逻辑
3. 调整 `query_patterns` 中的模式定义

### 7.4 添加新的Agent
1. 创建新的Agent类文件
2. 在 `QueryType` 枚举中添加新类型
3. 更新路由逻辑识别新类型
4. 添加相应的模式和关键词
5. 更新配置文件中的描述

## 8. 性能优化建议

### 8.1 当前性能指标
- 触发词匹配: <1ms
- 模板匹配: <5ms
- Schema路由: <10ms
- LLM路由: 1-3秒
- 规则路由: <10ms

### 8.2 优化方向
1. **缓存优化**: 对高频查询缓存路由决策
2. **并行处理**: SQL和RAG查询可并行执行
3. **预加载**: Schema信息启动时预加载
4. **模板索引**: 建立模板快速索引结构

## 9. 注意事项

1. **避免硬编码**: 所有配置都应该在配置文件中
2. **测试覆盖**: 新增路由规则必须有对应测试
3. **向后兼容**: 保持API接口的稳定性
4. **日志记录**: 关键路由决策都要有日志
5. **错误处理**: 每层都要有容错机制

## 10. 版本历史

- **v2.1.1** (2025-06-29): 7-Agent架构，配置化路由
- **v1.5.5** (2025-06-28): 基础4-Agent系统
- **v1.4.0** (2025-06-22): 初始路由系统

---

最后更新: 2025-06-29