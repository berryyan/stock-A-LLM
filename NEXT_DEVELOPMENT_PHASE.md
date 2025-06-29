# 下一步开发计划 - Stock Analysis System v2.2.0

**文档版本**: v5.0  
**更新日期**: 2025-06-29  
**当前版本**: v2.1.1 (代码清理完成，准备7-Agent架构)  
**当前分支**: dev-react-frontend-v2  
**重大决策**: 扩展到7-Agent架构，优先实施路由机制优化

## 📋 目录

1. [当前状态总结](#当前状态总结)
2. [7-Agent架构设计](#7-agent架构设计)
3. [Phase 0: 路由机制优化](#phase-0-路由机制优化)
4. [Phase 1: SQL Agent快速模板](#phase-1-sql-agent快速模板)
5. [Phase 2: 新增3个Agent](#phase-2-新增3个agent)
6. [Phase 3: 专业Agent快速路径](#phase-3-专业agent快速路径)
7. [Phase 4: 集成测试与优化](#phase-4-集成测试与优化)
8. [已完成功能总结](#已完成功能总结)

## 当前状态总结

### v2.1.1 最新成就
- ✅ 完成代码清理，删除未使用的Schema相关文件
- ✅ 确认SchemaKnowledgeBase为实际使用的Schema系统
- ✅ 分析并明确了Agent职责重叠问题
- ✅ 设计7-Agent架构方案
- ✅ 流式响应功能完整实现（v1.5.4完成）

### 系统现状
- **前端**: React前端功能完整，Claude.ai风格界面
- **后端**: 4个Agent功能完整，准备扩展到7个
- **性能优化空间**: 
  - 70%查询可通过快速模板实现（<0.5秒）
  - Schema系统已实现快速查询（<10ms）
  - 需要补充各Agent的快速查询模板

## 7-Agent架构设计

### 架构图
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

### Agent职责定位

1. **SQL Agent** - 基础数据查询（处理80%常见查询）
2. **Money Flow Agent** - 资金时序分析（主力行为、资金异动）
3. **Financial Agent** - 复杂财务分析（财务健康度、杜邦分析）
4. **Rank Agent** - 排名分析（触发词："排行分析："）
5. **ANNS Agent** - 公告查询（触发词："查询公告："）
6. **QA Agent** - 董秘互动（触发词："董秘互动："）
7. **RAG Agent** - 文档内容搜索（语义检索）

## 🎯 Phase 0: 路由机制优化（最高优先级，2天）

### 目标
- 支持7-Agent架构的路由需求
- 实现触发词优先路由机制
- 扩展QueryType枚举
- 优化路由性能

### 任务清单

#### 1. 扩展QueryType枚举（Day 1）
```python
# agents/hybrid_agent.py
class QueryType(str, Enum):
    # 现有类型
    SQL_ONLY = "sql"
    RAG_ONLY = "rag"
    FINANCIAL = "financial"
    MONEY_FLOW = "money_flow"
    # 新增类型
    RANK = "rank"          # 排名分析
    ANNS = "anns"          # 公告查询
    QA = "qa"              # 董秘互动
```

#### 2. 实现触发词检测（Day 1）
```python
def _check_trigger_words(self, question: str) -> Optional[str]:
    """检测触发词并返回对应的查询类型"""
    trigger_mapping = {
        "排行分析：": QueryType.RANK,
        "查询公告：": QueryType.ANNS,
        "董秘互动：": QueryType.QA
    }
    
    for trigger, query_type in trigger_mapping.items():
        if question.startswith(trigger):
            return query_type
    return None
```

#### 3. 优化路由优先级（Day 1）
```python
def _route_query(self, question: str) -> Dict[str, Any]:
    """优化后的路由逻辑"""
    # 1) 触发词优先（最高优先级）
    trigger_type = self._check_trigger_words(question)
    if trigger_type:
        return {
            'query_type': trigger_type,
            'reasoning': '触发词匹配',
            'confidence': 1.0
        }
    
    # 2) 模板匹配
    template_result = match_query_template(question)
    if template_result:
        return {
            'query_type': template_result['type'],
            'reasoning': '模板匹配',
            'confidence': 0.95
        }
    
    # 3) Schema快速路由
    schema_result = schema_router.get_quick_route(question)
    if schema_result and schema_result['confidence'] > 0.8:
        return schema_result
    
    # 4) LLM路由
    # 5) 规则降级
```

#### 4. 添加新路由模式（Day 2）
```python
# config/routing_patterns.py
ROUTING_PATTERNS = {
    'rank_patterns': {
        'keywords': ['排行', '排名', '前十', 'TOP', '涨幅榜', '跌幅榜'],
        'patterns': [
            r'.*排行.*',
            r'.*排名.*',
            r'.*前\d+.*',
            r'.*涨跌幅.*排.*'
        ]
    },
    'anns_patterns': {
        'keywords': ['公告', '年报', '季报', '业绩快报', '问询函'],
        'patterns': [
            r'.*公告.*列表',
            r'.*最新.*公告',
            r'.*年报.*季报'
        ]
    },
    'qa_patterns': {
        'keywords': ['董秘', '互动', '问答', '投资者关系'],
        'patterns': [
            r'.*董秘.*问.*',
            r'.*投资者.*问.*'
        ]
    }
}
```

#### 5. 实现处理方法（Day 2）
```python
# agents/hybrid_agent.py
def _handle_rank(self, question: str, **kwargs) -> Dict[str, Any]:
    """处理排名分析查询"""
    from agents.rank_agent import RankAgent
    rank_agent = RankAgent()
    return rank_agent.process(question, **kwargs)

def _handle_anns(self, question: str, **kwargs) -> Dict[str, Any]:
    """处理公告查询"""
    from agents.anns_agent import ANNSAgent
    anns_agent = ANNSAgent()
    return anns_agent.process(question, **kwargs)

def _handle_qa(self, question: str, **kwargs) -> Dict[str, Any]:
    """处理董秘互动查询"""
    from agents.qa_agent import QAAgent
    qa_agent = QAAgent()
    return qa_agent.process(question, **kwargs)
```

## 🎯 Phase 1: SQL Agent快速模板（2天）

### 目标
- 实现7个高频查询的快速模板
- 减少LLM调用，提升响应速度
- 覆盖80%的常见查询场景

### 模板实现计划

#### 1. 历史K线查询（90天）
```python
# utils/sql_templates.py
STOCK_KLINE_HISTORY = """
    SELECT 
        trade_date as 交易日期,
        open as 开盘价,
        high as 最高价,
        low as 最低价,
        close as 收盘价,
        vol as 成交量,
        amount as 成交额,
        pct_chg as 涨跌幅
    FROM tu_daily_detail
    WHERE ts_code = :ts_code
        AND trade_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
    ORDER BY trade_date DESC
"""
```

#### 2. 历史交易量查询（90天）
```python
STOCK_VOLUME_HISTORY = """
    SELECT 
        trade_date as 交易日期,
        vol as 成交量,
        amount as 成交额,
        turnover_rate as 换手率
    FROM tu_daily_detail d
    JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
    WHERE d.ts_code = :ts_code
        AND d.trade_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
    ORDER BY d.trade_date DESC
"""
```

#### 3. 利润查询
```python
COMPANY_PROFIT = """
    SELECT 
        end_date as 报告期,
        total_revenue as 营业总收入,
        revenue as 营业收入,
        operate_profit as 营业利润,
        total_profit as 利润总额,
        n_income as 净利润,
        n_income_attr_p as 归母净利润
    FROM tu_income
    WHERE ts_code = :ts_code
        AND report_type = '1'
    ORDER BY end_date DESC
    LIMIT :limit
"""
```

#### 4. PE/PB查询
```python
VALUATION_METRICS = """
    SELECT 
        trade_date as 交易日期,
        pe as 市盈率,
        pe_ttm as 市盈率TTM,
        pb as 市净率,
        ps as 市销率,
        ps_ttm as 市销率TTM
    FROM tu_daily_basic
    WHERE ts_code = :ts_code
        AND trade_date = :trade_date
"""
```

#### 5. 当日主力净流入排行
```python
MONEY_FLOW_RANKING = """
    SELECT 
        m.ts_code,
        s.name as 股票名称,
        m.net_mf_amount as 主力净流入,
        m.net_mf_amount_rate as 主力净流入率,
        d.pct_chg as 涨跌幅
    FROM tu_moneyflow_dc m
    JOIN tu_stock_basic s ON m.ts_code = s.ts_code
    JOIN tu_daily_detail d ON m.ts_code = d.ts_code AND m.trade_date = d.trade_date
    WHERE m.trade_date = :trade_date
        AND s.list_status = 'L'
    ORDER BY m.net_mf_amount DESC
    LIMIT :limit
"""
```

#### 6. 总市值排名
```python
MARKET_CAP_RANKING = """
    SELECT 
        d.ts_code,
        s.name as 股票名称,
        d.close as 收盘价,
        d.total_mv as 总市值,
        d.circ_mv as 流通市值,
        d.pe_ttm as 市盈率TTM,
        d.pb as 市净率
    FROM tu_daily_basic d
    JOIN tu_stock_basic s ON d.ts_code = s.ts_code
    WHERE d.trade_date = :trade_date
        AND s.list_status = 'L'
    ORDER BY d.total_mv DESC
    LIMIT :limit
"""
```

#### 7. 流通市值排名
```python
CIRC_CAP_RANKING = """
    SELECT 
        d.ts_code,
        s.name as 股票名称,
        d.close as 收盘价,
        d.circ_mv as 流通市值,
        d.total_mv as 总市值,
        d.turnover_rate as 换手率,
        d.volume_ratio as 量比
    FROM tu_daily_basic d
    JOIN tu_stock_basic s ON d.ts_code = s.ts_code
    WHERE d.trade_date = :trade_date
        AND s.list_status = 'L'
    ORDER BY d.circ_mv DESC
    LIMIT :limit
"""
```

## 🎯 Phase 2: 新增3个Agent（3天）

### Day 1: Rank Agent实现

#### 核心功能
- 支持各类排名查询
- 自动排除ST/*ST股票
- 支持排除北交所股票
- 提供排名变化标识

#### 实现文件
```python
# agents/rank_agent.py
class RankAgent:
    """排名分析专用Agent"""
    
    def __init__(self):
        self.templates = {
            '涨跌幅排行': PRICE_CHANGE_RANKING,
            '主力资金排行': MONEY_FLOW_RANKING,
            '市值排行': MARKET_CAP_RANKING,
            # ...
        }
    
    def process(self, question: str, exclude_st: bool = True, 
                exclude_bse: bool = False) -> Dict[str, Any]:
        """处理排名查询"""
        # 解析查询意图
        # 选择模板
        # 执行查询
        # 格式化结果
```

### Day 2: ANNS Agent实现

#### 核心功能
- 查询公告元数据
- 返回公告列表和链接
- 支持按类型筛选
- 支持时间范围查询

#### 实现文件
```python
# agents/anns_agent.py
class ANNSAgent:
    """公告查询专用Agent"""
    
    def __init__(self):
        self.ann_types = {
            '年报': ['年度报告'],
            '季报': ['第一季度报告', '第三季度报告'],
            '半年报': ['半年度报告'],
            '业绩快报': ['业绩快报'],
            '业绩预告': ['业绩预告']
        }
    
    def process(self, question: str, days: int = 5) -> Dict[str, Any]:
        """处理公告查询"""
        # 解析公告类型
        # 构建查询
        # 返回公告列表
```

### Day 3: QA Agent实现

#### 核心功能
- 查询董秘互动数据
- 支持关键词搜索
- 支持逻辑组合（AND/OR/NOT）
- 返回问答对

#### 实现文件
```python
# agents/qa_agent.py
class QAAgent:
    """董秘互动查询Agent"""
    
    def __init__(self):
        self.db_connector = MySQLConnector()
    
    def process(self, question: str) -> Dict[str, Any]:
        """处理董秘互动查询"""
        # 解析关键词
        # 构建查询逻辑
        # 查询tu_qa表
        # 返回问答结果
```

## 🎯 Phase 3: 专业Agent快速路径（2天）

### Day 1: Money Flow Agent快速模板

#### 实现模板
1. **连续N天主力流入**
```python
CONTINUOUS_INFLOW = """
    SELECT 
        ts_code,
        COUNT(*) as 连续流入天数,
        SUM(net_mf_amount) as 累计流入金额
    FROM tu_moneyflow_dc
    WHERE trade_date >= :start_date
        AND net_mf_amount > 0
    GROUP BY ts_code
    HAVING COUNT(*) >= :min_days
    ORDER BY SUM(net_mf_amount) DESC
"""
```

2. **资金异动检测**
```python
MONEY_FLOW_ABNORMAL = """
    SELECT 
        ts_code,
        trade_date,
        net_mf_amount,
        net_mf_amount_rate,
        buy_elg_amount,
        buy_lg_amount
    FROM tu_moneyflow_dc
    WHERE ABS(net_mf_amount_rate) > :threshold
        AND trade_date = :trade_date
    ORDER BY ABS(net_mf_amount) DESC
"""
```

### Day 2: Financial Agent快速模板

#### 实现模板
1. **财务健康度快速评分**
```python
FINANCIAL_HEALTH_QUICK = """
    WITH latest_financial AS (
        SELECT 
            ts_code,
            MAX(end_date) as latest_date
        FROM tu_fina_indicator
        WHERE report_type = '1'
        GROUP BY ts_code
    )
    SELECT 
        f.ts_code,
        f.roe as 净资产收益率,
        f.roa as 总资产收益率,
        f.debt_to_assets as 资产负债率,
        f.current_ratio as 流动比率,
        f.quick_ratio as 速动比率
    FROM tu_fina_indicator f
    JOIN latest_financial l ON f.ts_code = l.ts_code AND f.end_date = l.latest_date
    WHERE f.ts_code = :ts_code
"""
```

2. **杜邦分析快速版**
```python
DUPONT_QUICK = """
    SELECT 
        end_date,
        roe as ROE,
        npta as 净利率,
        assets_turn as 资产周转率,
        equity_multiplier as 权益乘数
    FROM tu_fina_indicator
    WHERE ts_code = :ts_code
        AND report_type = '1'
    ORDER BY end_date DESC
    LIMIT 4
"""
```

## 🎯 Phase 4: 集成测试与优化（2天）

### Day 1: 测试实施

#### 1. 路由准确性测试
- 准备100个测试用例
- 覆盖所有7个Agent
- 验证触发词效果
- 测试边界情况

#### 2. 性能基准测试
- 快速模板响应时间 < 0.5秒
- 普通查询响应时间 < 5秒
- 复杂查询响应时间 < 30秒
- 并发性能测试（50并发）

### Day 2: 文档与优化

#### 1. 更新文档
- API文档更新
- 用户使用指南
- 开发者文档
- 测试报告

#### 2. 性能优化
- SQL查询优化
- 缓存策略调整
- 连接池优化
- 日志级别调整

## 预期成果

### 性能提升
- **快速查询占比**: 从30% → 70%
- **平均响应时间**: 从10秒 → 3秒
- **用户满意度**: 显著提升

### 功能增强
- **新增功能**: 排名分析、公告查询、董秘互动
- **查询准确率**: 95%以上
- **系统稳定性**: 支持100+并发用户

### 技术改进
- **代码质量**: 模块化、可维护性提升
- **测试覆盖**: 90%以上
- **文档完善**: 用户和开发文档齐全

## 已完成功能总结

### v2.1.1 最新成就 ✅
- 完成代码清理，删除未使用的Schema相关文件
- 确认SchemaKnowledgeBase为实际使用的Schema系统
- 分析并明确了Agent职责重叠问题
- 设计7-Agent架构方案

### 前端功能 ✅
- React + TypeScript + Claude.ai风格界面
- 流式响应 + 打字效果 + 停止按钮
- 完整Markdown渲染（代码高亮、表格、公式）
- 分屏布局 + 侧边栏折叠
- 深色主题优化

### 后端功能 ✅
- 四大Agent系统（SQL、RAG、Financial、MoneyFlow）
- Hybrid Agent智能路由
- SchemaKnowledgeBase快速查询（<10ms）
- 智能日期解析v2.0
- 股票代码映射器
- WebSocket实时通信
- 完整错误处理

### 系统特性 ✅
- Windows兼容性100%
- 双环境开发支持
- 完整测试框架
- API文档完善

### 性能指标 ✅
- Schema查询: <10ms
- SQL查询: 5-30秒
- RAG查询: 3-15秒
- 财务分析: 20-45秒
- 资金流向: 15-30秒
- 并发用户: 50+

---

**下一步行动**: 开始实施Phase 0 - 路由机制优化，支持7-Agent架构