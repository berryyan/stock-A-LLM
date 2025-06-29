# 下一步开发计划细节 - Phase 2 & 3

**版本目标**: v2.2.0  
**预计时间**: 5-7天

## Phase 2: 新增3个Agent（3-4天）

### 2.1 Rank Agent实现（Day 1）

#### 核心功能
- 涨跌幅排名（含ST过滤）
- 市值排名（总市值、流通市值）
- 成交额/成交量排名
- 板块/行业排名

#### 实现文件
```python
# agents/rank_agent.py
class RankAgent:
    def __init__(self):
        self.ranking_templates = {
            'price_change': '涨跌幅排名',
            'market_cap': '市值排名',
            'volume': '成交量排名',
            'sector': '板块排名'
        }
    
    def analyze_ranking(self, query: str) -> Dict[str, Any]:
        # 1. 解析排名类型
        # 2. 构建SQL查询
        # 3. 执行查询
        # 4. 格式化结果
        pass
```

#### 快速模板示例
```sql
-- 涨跌幅排名（排除ST）
SELECT 
    d.ts_code,
    s.name,
    d.close,
    d.pct_chg,
    d.vol,
    d.amount
FROM tu_daily_detail d
JOIN tu_stock_basic s ON d.ts_code = s.ts_code
WHERE d.trade_date = :trade_date
    AND s.name NOT LIKE '%ST%'
    AND s.list_status = 'L'
ORDER BY d.pct_chg DESC
LIMIT :limit
```

### 2.2 ANNS Agent实现（Day 2）

#### 核心功能
- 公告列表查询
- 公告时间筛选
- 公告类型分类
- 公告统计分析

#### 数据表结构
```sql
-- tu_anns_d表
- ts_code: 股票代码
- ann_date: 公告日期
- title: 公告标题
- type: 公告类型
- pdf_url: PDF链接
```

#### 实现要点
```python
# agents/anns_agent.py
class ANNSAgent:
    def query_announcements(self, query: str) -> Dict[str, Any]:
        # 1. 提取查询参数（股票、时间、类型）
        # 2. 构建SQL查询
        # 3. 返回公告列表
        # 4. 可选：统计分析
        pass
```

### 2.3 QA Agent实现（Day 3）

#### 核心功能
- 投资者提问搜索
- 公司回复内容
- 关键词匹配
- 互动频率统计

#### 数据表结构
```sql
-- tu_irm_qa_sh/sz表
- ts_code: 股票代码
- question_date: 提问日期
- question: 投资者提问
- answer_date: 回复日期
- answer: 公司回复
```

#### 实现策略
```python
# agents/qa_agent.py
class QAAgent:
    def search_qa(self, query: str) -> Dict[str, Any]:
        # 1. 关键词提取
        # 2. 全文搜索或关键词匹配
        # 3. 结果排序（相关性/时间）
        # 4. 格式化输出
        pass
```

### 2.4 集成测试（Day 4）

#### 测试计划
1. **单元测试**
   - 每个Agent独立功能
   - 快速模板准确性
   - 错误处理

2. **集成测试**
   - Hybrid Agent路由
   - 触发词识别
   - 端到端流程

3. **性能测试**
   - 响应时间
   - 并发处理
   - 资源占用

## Phase 3: 专业Agent快速路径（2-3天）

### 3.1 Financial Agent优化（Day 1）

#### 新增快速模板
1. **基础财务指标**
   - ROE/ROA快速查询
   - 负债率查询
   - 现金流状况

2. **简化财务对比**
   - 同行业对比
   - 历史趋势

### 3.2 Money Flow Agent优化（Day 2）

#### 快速分析模板
1. **主力资金快照**
   - 今日主力净流入
   - 5日/10日资金趋势
   - 资金流向排名

2. **异动监测**
   - 大单异动
   - 连续流入/流出

### 3.3 性能优化（Day 3）

#### 优化方向
1. **缓存策略**
   - 热门查询缓存
   - Schema信息缓存
   - 结果缓存

2. **并行处理**
   - 多Agent并行
   - 批量查询优化

3. **索引优化**
   - 数据库索引
   - 查询优化

## 实施建议

### 开发顺序
1. **Rank Agent** - 最简单，SQL为主
2. **ANNS Agent** - 中等复杂度
3. **QA Agent** - 可能需要全文搜索

### 技术要点
1. **统一接口设计**
   ```python
   class BaseAgent:
       def process(self, query: str) -> Dict[str, Any]:
           pass
   ```

2. **错误处理标准化**
   ```python
   {
       'success': bool,
       'data': Any,
       'error': Optional[str],
       'metadata': Dict
   }
   ```

3. **日志规范**
   - Agent名称前缀
   - 查询追踪ID
   - 性能指标

### 测试策略
1. **TDD开发**
   - 先写测试用例
   - 实现功能
   - 重构优化

2. **持续集成**
   - 每完成一个Agent即集成
   - 保持系统可用性

## 风险管理

### 潜在风险
1. **数据表结构变化**
   - 解决：动态Schema读取

2. **性能瓶颈**
   - 解决：渐进式优化

3. **路由冲突**
   - 解决：严格的优先级规则

### 质量保证
1. **代码审查**
   - 每个Agent完成后审查
   - 遵循项目规范

2. **文档同步**
   - 实时更新文档
   - 保持Claude.md同步

---

完成Phase 2&3后，系统将拥有完整的7-Agent架构，覆盖95%以上的用户查询需求。