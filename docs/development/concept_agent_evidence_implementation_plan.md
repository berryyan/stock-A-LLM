# Concept Agent 证据系统实现方案

## 📅 创建日期：2025-07-18

## 🎯 目标

完整实现原始设计中的4维度评分体系，包括财报、互动平台、公告搜索功能。

## 📊 现有资源盘点

### 1. 互动平台数据 ✅
- **表名**: `tu_irm_qa_sh`（上交所）、`tu_irm_qa_sz`（深交所）
- **字段**: ts_code, name, trade_date, q（问题）, a（回答）
- **数据量**: 20万+条记录
- **可行性**: 直接SQL查询即可

### 2. RAG系统 ✅
- **已有Agent**: `rag_agent.py` 和 `rag_agent_modular.py`
- **功能**: 支持公告和年报的语义搜索
- **可行性**: 需要调用RAG Agent获取证据

### 3. 概念板块数据 ✅
- **三大数据源**: 同花顺、东财、开盘啦
- **已实现**: 概念股成分查询
- **可行性**: 已完成

## 🛠️ 实现方案

### Phase 1: 证据收集器实现（Day 6上午）

#### 1.1 创建EvidenceCollector类

```python
class EvidenceCollector:
    """概念股证据收集器"""
    
    def __init__(self):
        self.db = MySQLConnector()
        self.rag_agent = RAGAgentModular()  # 复用现有RAG
    
    def collect_evidence(self, ts_code: str, concept: str) -> Dict[str, Any]:
        """收集所有维度的证据"""
        evidence = {
            'software': self._collect_software_evidence(ts_code, concept),
            'report': self._collect_report_evidence(ts_code, concept),
            'interaction': self._collect_interaction_evidence(ts_code, concept),
            'announcement': self._collect_announcement_evidence(ts_code, concept)
        }
        return evidence
```

#### 1.2 软件收录证据（已有数据）

```python
def _collect_software_evidence(self, ts_code: str, concept: str):
    """收集软件收录证据"""
    evidence_list = []
    
    # 查询三大数据源
    if self._in_ths_concept(ts_code, concept):
        evidence_list.append({
            'type': '软件收录',
            'source': '同花顺',
            'content': f'同花顺{concept}概念成分股',
            'score': 15
        })
    
    # 类似处理东财和开盘啦
    return evidence_list
```

#### 1.3 互动平台证据（新增）

```python
def _collect_interaction_evidence(self, ts_code: str, concept: str):
    """收集互动平台证据"""
    # 确定交易所
    exchange = 'sh' if ts_code.endswith('.SH') else 'sz'
    table = f'tu_irm_qa_{exchange}'
    
    # 查询相关问答
    query = f"""
    SELECT trade_date, q, a 
    FROM {table}
    WHERE ts_code = %s 
    AND (q LIKE %s OR a LIKE %s)
    ORDER BY trade_date DESC
    LIMIT 5
    """
    
    results = self.db.execute_query(
        query, 
        [ts_code, f'%{concept}%', f'%{concept}%']
    )
    
    evidence_list = []
    for row in results:
        if concept in row['a']:  # 董秘回答中确认
            evidence_list.append({
                'type': '互动平台',
                'source': '董秘回复',
                'date': row['trade_date'],
                'content': f"问：{row['q'][:50]}... 答：{row['a'][:100]}...",
                'score': 20
            })
            break  # 只需要一个确认即可
    
    return evidence_list
```

#### 1.4 年报证据（通过RAG）

```python
def _collect_report_evidence(self, ts_code: str, concept: str):
    """收集财报证据"""
    # 构造查询
    stock_name = self._get_stock_name(ts_code)
    query = f"{stock_name} {concept} 年报 业务 收入"
    
    # 调用RAG Agent
    try:
        result = self.rag_agent.process_query(query)
        if result.success and result.data:
            # 解析RAG返回的内容
            evidence_list = []
            if '年报' in result.data and concept in result.data:
                evidence_list.append({
                    'type': '财报',
                    'source': '年报',
                    'content': self._extract_report_content(result.data),
                    'score': 15
                })
            return evidence_list
    except:
        return []
```

#### 1.5 公告证据（通过RAG）

```python
def _collect_announcement_evidence(self, ts_code: str, concept: str):
    """收集公告证据"""
    stock_name = self._get_stock_name(ts_code)
    query = f"{stock_name} {concept} 公告"
    
    try:
        result = self.rag_agent.process_query(query)
        if result.success and result.data:
            evidence_list = []
            # 提取公告标题和内容
            if concept in result.data:
                evidence_list.append({
                    'type': '公告',
                    'source': '临时公告',
                    'content': self._extract_announcement_title(result.data),
                    'score': 10
                })
            return evidence_list
    except:
        return []
```

### Phase 2: 评分系统重构（Day 6下午）

#### 2.1 修改ConceptScorer

```python
def _calculate_concept_score_v2(self, stock: Dict, evidence: Dict) -> float:
    """
    基于证据的概念关联度评分（满分40）
    完全按照原始设计实现
    """
    score = 0
    
    # 1. 软件收录（40分）
    for ev in evidence.get('software', []):
        score += ev['score']
    
    # 2. 财报证据（30分）
    for ev in evidence.get('report', []):
        score += ev['score']
    
    # 3. 互动平台（20分）
    for ev in evidence.get('interaction', []):
        score += ev['score']
    
    # 4. 公告证据（10分）
    for ev in evidence.get('announcement', []):
        score += ev['score']
    
    return min(score, 100)  # 总分不超过100
```

#### 2.2 修改评分流程

```python
def calculate_scores_with_evidence(self, stocks, technical_data, money_flow_data):
    """带证据的评分计算"""
    scored_stocks = []
    
    for stock in stocks:
        # 收集证据
        evidence = self.evidence_collector.collect_evidence(
            stock['ts_code'], 
            stock['concept']
        )
        
        # 计算得分
        concept_score = self._calculate_concept_score_v2(stock, evidence)
        
        # 保存证据
        stock['evidence'] = evidence
        stock['evidence_list'] = self._flatten_evidence(evidence)
        stock['concept_score'] = concept_score
        
        # ... 其他评分逻辑
```

### Phase 3: 报告生成优化（Day 6晚上）

#### 3.1 证据展示

```python
def _format_evidence_report(self, stock: Dict) -> str:
    """格式化证据报告"""
    lines = [f"### {stock['name']}({stock['ts_code']}) - 概念关联证据\n"]
    
    for ev in stock['evidence_list']:
        lines.append(f"**{ev['type']} - {ev['source']}**")
        lines.append(f"- 内容：{ev['content']}")
        lines.append(f"- 得分：{ev['score']}分\n")
    
    return '\n'.join(lines)
```

## 📈 预期效果

### 评分透明度提升
```
贵州茅台(600519.SH) - 储能概念关联证据

**软件收录 - 东财**
- 内容：东财储能概念成分股
- 得分：15分

**互动平台 - 董秘回复**
- 内容：问：公司是否涉及储能业务... 答：公司暂无储能相关业务
- 得分：0分（否定回答）

总分：15/100分（边缘概念股）
```

### 用户价值
1. **透明度**：用户可以看到每个评分的依据
2. **可验证**：提供具体的证据来源
3. **可信度**：基于事实而非猜测

## ⏰ 时间安排

### Day 6
- 上午：实现EvidenceCollector（4小时）
- 下午：集成到ConceptScorer（3小时）
- 晚上：优化报告生成（2小时）

### Day 7
- 上午：全面测试
- 下午：性能优化
- 晚上：文档更新

## 🚨 风险点

1. **RAG调用性能**
   - 风险：每个股票调用2次RAG可能很慢
   - 缓解：实现缓存机制

2. **数据覆盖度**
   - 风险：不是所有股票都有互动平台数据
   - 缓解：这是正常的，没有就是0分

3. **集成复杂度**
   - 风险：需要修改多个模块
   - 缓解：分步实现，每步测试

## ✅ 决策点

请确认：
1. 是否按此方案实现完整的证据系统？
2. 是否可以接受RAG调用的性能开销？
3. 证据展示的格式是否符合预期？