# 股票分析系统开发计划文档

**版本**: v2.1.11  
**更新日期**: 2025-07-02  
**文档状态**: 正式版

## 目录

1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [Agent职责划分](#agent职责划分)
4. [开发计划](#开发计划)
5. [实施细节](#实施细节)
6. [测试策略](#测试策略)
7. [版本规划](#版本规划)

## 项目概述

股票分析系统v2.2.0旨在通过优化Agent架构和实现快速查询模板，大幅提升系统性能和用户体验。本次升级将Agent从4个扩展到7个，每个Agent都有明确的职责定位和快速响应能力。

### 核心目标

1. **性能提升**：70%的查询通过快速模板响应（<0.5秒）
2. **功能完善**：新增排名分析、公告查询、董秘互动三大功能
3. **架构优化**：明确Agent职责边界，避免功能重叠
4. **用户体验**：支持触发词快速路由，响应更精准

## 系统架构

### 7-Agent架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    Hybrid Agent                         │
│                  （智能路由中心）                        │
└────────────────────────┬────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼───┐  ┌────────┐  ┌▼────────┐  ┌───────▼──┐
│  SQL   │  │  RAG   │  │Financial│  │Money Flow│
│ Agent  │  │ Agent  │  │  Agent  │  │  Agent   │
└────────┘  └────────┘  └─────────┘  └──────────┘
    
         ┌────────┐  ┌────────┐  ┌────────┐
         │  Rank  │  │  ANNS  │  │   QA   │
         │ Agent  │  │ Agent  │  │ Agent  │
         └────────┘  └────────┘  └────────┘
```

### 路由优先级

1. **触发词匹配**（最高优先级）
   - `排行分析：` → Rank Agent
   - `查询公告：` → ANNS Agent
   - `董秘互动：` → QA Agent

2. **模板匹配** → 快速查询模板
3. **Schema路由** → 基于数据库结构
4. **LLM路由** → 智能判断
5. **规则降级** → 关键词匹配

## Agent职责划分

### 1. SQL Agent - 基础数据查询引擎

**定位**：处理80%的常见查询，提供基础数据服务

**快速模板**：
- 股价类：最新股价、历史K线（90天）、历史交易量（90天）
- 财务类：利润查询、市盈率/市净率查询
- 资金类：当日主力净流入排行
- 排名类：总市值排名、流通市值排名

### 2. RAG Agent - 文档内容检索

**定位**：纯文档内容搜索，语义理解

**优化方向**：
- 改进向量搜索质量
- 优化文档切片策略
- 增强过滤条件处理

### 3. Financial Agent - 专业财务分析

**定位**：处理需要复杂计算和专业分析的财务查询

**快速模板**：
- 综合分析：财务健康度快速评分、杜邦分析快速版、现金流质量快速评估
- 对比分析：同行业财务对比、多期财务趋势
- 深度指标：综合盈利能力分析、偿债能力评估

### 4. Money Flow Agent - 资金行为分析

**定位**：处理需要时间序列和行为分析的资金查询

**快速模板**：
- 行为分析：连续N天主力流入、资金异动检测
- 深度分析：四级资金分布分析、主力行为模式识别
- 对比分析：散户vs主力对比、板块资金流向对比

### 5. Rank Agent - 各类排名分析（新增）

**定位**：处理排名查询，提供排名变化分析

**特色功能**：
- 支持排除ST/*ST股票
- 支持排除北交所股票
- 提供排名变化（↑↓→）

**快速模板**：
- 股价类：涨跌幅排行（日/10日）
- 资金类：个股/板块主力资金排行（日/周/月/季）
- 市值类：市值排行TOP4000统计

### 6. ANNS Agent - 公告源数据查询（新增）

**定位**：处理公告元数据查询，返回公告列表和链接

**快速模板**：
- 最新公告列表（默认5天）
- 公司公告查询（默认21天）
- 特定类型公告查询（年报、季报、业绩快报等）

### 7. QA Agent - 董秘互动查询（新增）

**定位**：处理投资者互动平台数据查询

**快速模板**：
- 单关键词查询
- 多关键词组合查询（AND/OR/NOT）

## 开发计划

### Phase 0：路由机制优化（最高优先级，2天）

**目标**：支持7-Agent架构，实现触发词优先路由

**任务清单**：
1. 分析现有路由机制
2. 扩展QueryType枚举
3. 实现触发词检测
4. 添加新路由模式
5. 实现处理方法

### Phase 1：SQL Agent优化（2天）

**目标**：实现7个快速查询模板

**模板列表**：
1. 历史K线查询（90天）
2. 历史交易量查询（90天）
3. 利润查询
4. PE/PB查询
5. 当日主力净流入排行
6. 总市值排名
7. 流通市值排名

### Phase 2：新增3个Agent（3天）

**任务分配**：
- Day 1: Rank Agent
- Day 2: ANNS Agent  
- Day 3: QA Agent

### Phase 3：专业Agent快速路径（2天）

**任务分配**：
- Day 1: Money Flow Agent快速模板
- Day 2: Financial Agent快速模板

### Phase 4：集成测试与优化（2天）

**测试内容**：
1. 路由准确性测试
2. 性能基准测试
3. 文档更新
4. 用户手册

## 实施细节

### 路由优化实施

```python
# 1. 扩展QueryType
class QueryType(str, Enum):
    # 现有类型...
    RANK = 'rank'      # 排名分析
    ANNS = 'anns'      # 公告查询
    QA = 'qa'          # 董秘互动

# 2. 触发词检测
def _check_trigger_words(self, question: str) -> Optional[str]:
    if question.startswith("排行分析："):
        return QueryType.RANK
    elif question.startswith("查询公告："):
        return QueryType.ANNS
    elif question.startswith("董秘互动："):
        return QueryType.QA
    return None

# 3. 路由优先级调整
def _route_query(self, question: str) -> Dict[str, Any]:
    # 1) 触发词优先
    trigger_type = self._check_trigger_words(question)
    if trigger_type:
        return {'query_type': trigger_type, 'reasoning': '触发词匹配'}
    
    # 2) 继续现有路由逻辑...
```

### SQL模板实施示例

```python
# utils/sql_templates.py
class SQLTemplates:
    # 历史K线查询
    STOCK_KLINE_HISTORY = """
        SELECT 
            trade_date,
            open, high, low, close,
            vol, amount, pct_chg
        FROM tu_daily_detail
        WHERE ts_code = :ts_code
            AND trade_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        ORDER BY trade_date DESC
    """
    
    # 市值排名
    MARKET_CAP_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.total_mv,
            d.circ_mv,
            d.pe_ttm,
            d.pb
        FROM tu_daily_basic d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
        ORDER BY d.total_mv DESC
        LIMIT :limit
    """
```

## 测试策略

### 单元测试

每个Agent的快速模板都需要独立测试：
- 输入验证测试
- SQL正确性测试
- 结果格式测试
- 性能基准测试

### 集成测试

- 路由准确性：100个测试用例覆盖所有路由路径
- 端到端测试：从API到最终结果
- 并发测试：50个并发请求

### 性能测试

目标指标：
- 快速模板响应：< 0.5秒
- 普通查询响应：< 5秒
- 复杂查询响应：< 30秒

## 版本规划

### v2.1.11（2025-07-02完成）
- ✅ 财务指标排名快速路径实现
  - PE排名、PB排名、净利润排名、营收排名、ROE排名
  - 性能提升20-600倍（从30-40秒降至0.05-1.5秒）
  - 智能参数提取和异常值过滤
- ✅ 资金类型术语标准化（16种非标准术语映射）
- ✅ 市值排名查询优化（支持无数字默认前10、TOP格式）

### v2.2.0（当前规划）
- 7-Agent架构（已部分实现）
- 快速查询模板（持续扩展中）
- 触发词路由（已实现）

### v2.3.0（计划）
- 真实流式响应
- 数据可视化集成
- 响应格式标准化

### v2.4.0（展望）
- AI策略建议
- 自动化交易信号
- 多市场支持

## 附录

### 相关文档
- [CLAUDE.md](../CLAUDE.md) - 开发指导
- [CURRENT_STATUS.md](./project_status/CURRENT_STATUS.md) - 项目状态
- [test-guide.md](../test-guide.md) - 测试指南

### 开发规范
- 所有新功能必须有对应的测试
- 代码提交前必须通过lint检查
- 文档与代码同步更新
- 遵循语义化版本规范