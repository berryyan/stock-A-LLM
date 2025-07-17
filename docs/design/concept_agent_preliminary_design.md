# Concept Agent 初步设计文档

版本：v0.1（初步设计）  
创建时间：2025-07-13  
状态：待数据库准备后细化  
作者：Stock Analysis System Team

## 1. 概述

### 1.1 背景
Concept Agent是v2.4.0计划中的核心Agent之一，旨在提供基于事实依据的概念股智能发现和分析能力。与网络上随意的概念股列表不同，本Agent强调所有概念关联都必须有明确的事实依据。

### 1.2 核心价值
通过有事实根据的信息、公告、数据、行情、技术指标等判断分析出一个概念的龙头和跟涨股票列表。

### 1.3 设计原则
- **事实驱动**：所有概念关联必须有明确依据
- **多源验证**：结合软件收录、财报、互动平台、公告等多维度信息
- **实时更新**：每日更新概念数据和技术指标
- **智能匹配**：支持精确和模糊概念匹配

## 2. 功能设计

### 2.1 核心功能流程

```
用户输入（关键词/描述）
    ↓
【第一步：概念识别与股票发现】
    ├─→ 精确匹配：现有概念板块数据库
    ├─→ 模糊匹配：板块名称、描述的语义匹配
    └─→ 扩展发现：互动平台 + 公告RAG（当上述无结果时）
         ↓
    概念板块列表 + 概念股列表
         ↓
【第二步：数据分析与筛选】
    ├─→ 资金流向分析
    ├─→ 行情形态分析
    └─→ 技术指标筛选
         ↓
    综合分析报告
```

### 2.2 查询场景

#### A类查询：关键词发现
- 输入示例："充电宝相关的概念板块和概念股有哪些？"
- 功能：根据关键词找出所有相关概念板块和成分股

#### B类查询：条件筛选
- 输入示例："半导体相关的概念股最近哪些符合日周主力资金净流入、MACD水上红柱且5日10日均线多头排列的？"
- 功能：在概念股范围内进行技术条件筛选

### 2.3 功能边界

**包含功能**：
- ✅ 概念板块识别（精确+模糊匹配）
- ✅ 概念股列表获取
- ✅ 关联原因分析（多维度证据）
- ✅ 技术指标筛选
- ✅ 资金流向分析
- ✅ 综合报告生成

**不包含功能**：
- ❌ 概念趋势预测
- ❌ 主动推荐概念股
- ❌ 美股概念支持（暂时）

## 3. 数据架构设计（待实施）

### 3.1 核心数据表设计

```sql
-- 1. 概念板块主表
tu_concept_blocks (
    concept_code VARCHAR(20),      -- BKxxxx.DC
    concept_name VARCHAR(100),     -- 概念名称
    source VARCHAR(50),           -- 来源（东财/同花顺/通达信）
    description TEXT,             -- 概念描述
    keywords TEXT,                -- 关键词列表（JSON格式）
    update_date DATE,
    PRIMARY KEY (concept_code, source)
)

-- 2. 概念股成分表
tu_concept_stocks (
    concept_code VARCHAR(20),
    ts_code VARCHAR(20),
    join_date DATE,               -- 加入日期
    join_reason TEXT,             -- 加入原因
    source VARCHAR(50),           -- 数据来源
    weight DECIMAL(10,4),         -- 权重/重要度
    status VARCHAR(20),           -- 活跃/历史
    PRIMARY KEY (concept_code, ts_code, source)
)

-- 3. 概念股关联证据表
tu_concept_evidence (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20),
    concept_code VARCHAR(20),
    evidence_type VARCHAR(50),    -- 财报/互动/公告
    evidence_date DATE,
    evidence_content TEXT,        -- 具体内容
    relevance_score INT,          -- 关联度评分(0-100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 4. 概念股技术数据缓存表（日更新）
tu_concept_technical_cache (
    ts_code VARCHAR(20),
    trade_date DATE,
    -- 资金流向
    main_net_inflow_daily DECIMAL(20,2),
    main_net_inflow_weekly DECIMAL(20,2),
    main_net_rate DECIMAL(10,4),
    -- 技术指标
    ma5 DECIMAL(10,2),
    ma10 DECIMAL(10,2),
    ma20 DECIMAL(10,2),
    macd_status VARCHAR(20),      -- 水上/水下
    macd_trend VARCHAR(20),       -- 红柱/绿柱
    ma_pattern VARCHAR(50),       -- 多头/空头排列
    -- 行情形态
    price_trend VARCHAR(50),      -- 趋势判断
    volume_pattern VARCHAR(50),   -- 量能形态
    PRIMARY KEY (ts_code, trade_date)
)
```

### 3.2 数据来源
- **概念板块数据**：由另一个项目每日从东财、同花顺等API采集
- **互动平台数据**：每日更新的董秘问答数据
- **公告数据**：通过现有RAG系统的公告数据库
- **技术指标**：每日19点后批量计算并缓存

## 4. 关联度算法设计

### 4.1 多维度评分体系

```python
def calculate_relevance_score(stock, concept):
    """
    计算股票与概念的关联度评分
    总分100分，分为4个维度
    """
    score = 0
    evidence = []
    
    # 1. 软件收录权重（40分）
    software_score = 0
    if in_eastmoney_concept:
        software_score += 15
        evidence.append({
            'type': '软件收录',
            'source': '东财',
            'content': f'东财{concept}概念成分股',
            'score': 15
        })
    if in_tonghuashun_concept:
        software_score += 15
        evidence.append({
            'type': '软件收录',
            'source': '同花顺',
            'content': f'同花顺{concept}概念成分股',
            'score': 15
        })
    if in_other_software:
        software_score += 10
        evidence.append({
            'type': '软件收录',
            'source': '其他',
            'content': f'其他软件收录',
            'score': 10
        })
    
    # 2. 财报证据权重（30分）
    report_score = 0
    if concept_in_annual_report:
        report_score += 15
        evidence.append({
            'type': '财报',
            'source': '年报',
            'content': report_content[:100],
            'score': 15
        })
    if concept_in_quarterly_report:
        report_score += 15
        evidence.append({
            'type': '财报',
            'source': '季报',
            'content': '季报业务涉及',
            'score': 15
        })
    
    # 3. 互动平台权重（20分）
    interaction_score = 0
    if secretary_confirmed:
        interaction_score += 20
        evidence.append({
            'type': '互动平台',
            'source': '董秘回复',
            'content': interaction_content[:100],
            'score': 20
        })
    
    # 4. 公告证据权重（10分）
    announcement_score = 0
    if concept_in_announcements:
        announcement_score += 10
        evidence.append({
            'type': '公告',
            'source': '临时公告',
            'content': announcement_title,
            'score': 10
        })
    
    total_score = software_score + report_score + interaction_score + announcement_score
    
    return {
        'total_score': total_score,
        'evidence_list': evidence,
        'score_breakdown': {
            'software': software_score,
            'report': report_score,
            'interaction': interaction_score,
            'announcement': announcement_score
        }
    }
```

### 4.2 关联强度分级
- **核心概念股**（80-100分）：多维度强关联
- **重要概念股**（60-79分）：有明确业务关联
- **相关概念股**（40-59分）：有一定关联
- **边缘概念股**（20-39分）：弱关联

## 5. 技术实现方案

### 5.1 模块设计

```python
class ConceptAgentModular:
    """概念股分析Agent模块化版本"""
    
    def __init__(self):
        # 复用现有模块
        self.parameter_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        # 复用分析模块
        self.money_flow_analyzer = MoneyFlowAnalyzer()
        # self.technical_analyzer = TechnicalAnalyzer()  # 待Technical Agent完成
        
        # 概念专用模块
        self.concept_matcher = ConceptMatcher()
        self.evidence_collector = EvidenceCollector()
        self.relevance_calculator = RelevanceCalculator()
        self.concept_screener = ConceptScreener()
```

### 5.2 查询处理流程

```python
async def process_query(self, query: str) -> AgentResponse:
    """处理概念股查询"""
    # 1. 参数提取
    params = self.parameter_extractor.extract(query)
    
    # 2. 识别查询类型
    query_type = self._identify_query_type(query)
    
    if query_type == 'DISCOVERY':
        # A类查询：概念发现
        return await self._handle_concept_discovery(params)
    elif query_type == 'SCREENING':
        # B类查询：条件筛选
        return await self._handle_concept_screening(params)
```

## 6. 待讨论的细节

### 6.1 模糊匹配算法
- **选项1**：基于分词的关键词匹配
- **选项2**：基于embedding的语义相似度
- **选项3**：混合方案（关键词+语义）
- **需要确定**：匹配阈值和优先级

### 6.2 技术指标细节
- **多头排列定义**：MA5 > MA10 > MA20？还是需要斜率判断？
- **MACD状态判断**：单日还是连续N日？
- **成交量配合**：是否需要量能确认？

### 6.3 输出格式优化
- **分级显示**：是否区分核心/重要/相关概念股？
- **证据展示**：详细模式vs简洁模式？
- **排序规则**：按关联度？市值？涨跌幅？

### 6.4 性能优化
- **预计算策略**：哪些指标需要预计算？
- **缓存机制**：查询结果缓存时长？
- **并发处理**：批量股票分析如何优化？

## 7. 实施计划

### Phase 1：数据准备（等待外部项目）
- [ ] 等待概念板块表创建
- [ ] 等待成分股数据导入
- [ ] 确认数据更新机制

### Phase 2：核心开发（数据就绪后）
- [ ] 实现概念匹配模块
- [ ] 实现证据收集模块
- [ ] 实现关联度计算
- [ ] 实现条件筛选功能

### Phase 3：集成测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 用户测试

## 8. 风险与依赖

### 8.1 外部依赖
- **数据源依赖**：需要外部项目提供概念数据
- **更新时效**：依赖每日19点的数据更新

### 8.2 技术风险
- **查询性能**：B类查询可能涉及大量计算
- **数据一致性**：多源数据的一致性保证

## 9. 总结

Concept Agent将为用户提供基于事实的概念股分析能力，核心特点：
1. **事实驱动**：所有推荐都有明确依据
2. **多维验证**：结合多个数据源交叉验证
3. **智能筛选**：支持复杂的技术条件筛选
4. **透明可信**：提供详细的关联证据

当前状态：等待数据库表创建后进一步细化设计。

---
文档版本：v0.1  
最后更新：2025-07-13  
下一步：等待数据表创建后更新为v1.0正式版