# Concept Agent Day 6 详细开发计划

## 当前状态回顾

### 已完成功能
1. **证据系统核心实现** ✅
   - EvidenceCollector：4维度证据收集（软件、财报、互动、公告）
   - ConceptScorerV2：基于证据的100分评分系统
   - 报告生成：详细证据展示

2. **技术问题已解决** ✅
   - SQL参数传递（命名参数）
   - 交易所分表查询
   - RAG延迟初始化

3. **基础测试通过** ✅
   - 软件收录查询正常
   - 互动平台证据收集成功
   - 评分计算逻辑正确

### 待解决问题
1. **性能问题**
   - RAG查询可能超时（30秒限制）
   - 大量股票查询时性能下降
   - 无缓存机制，重复查询浪费资源

2. **功能缺陷**
   - 财报/公告证据未充分测试
   - 否定证据处理不够完善
   - 报告格式可以更专业

3. **系统集成**
   - 未与主API系统集成测试
   - 缺少完整的端到端测试
   - 性能监控未实现

## Day 6 开发计划

### 第一阶段：性能优化（上午 9:00-12:00）

#### 1.1 证据缓存机制实现（优先级：高）
```python
# 实现计划
class EvidenceCache:
    """证据缓存管理器"""
    def __init__(self, ttl=3600):  # 1小时缓存
        self._cache = {}
        self._ttl = ttl
    
    def get_key(self, ts_code, concepts):
        return f"{ts_code}_{','.join(sorted(concepts))}"
    
    def get(self, ts_code, concepts):
        key = self.get_key(ts_code, concepts)
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return data
        return None
    
    def set(self, ts_code, concepts, evidence):
        key = self.get_key(ts_code, concepts)
        self._cache[key] = (evidence, time.time())
```

#### 1.2 RAG查询优化（优先级：高）
- 实现查询超时控制（10秒）
- 添加查询结果缓存
- 优化查询构造，减少无效查询
- 批量预热常见概念

#### 1.3 并行证据收集（优先级：中）
```python
# 使用ThreadPoolExecutor并行收集
from concurrent.futures import ThreadPoolExecutor, as_completed

def collect_evidence_parallel(self, ts_code, concepts):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(self._collect_software_evidence, ts_code, concepts): 'software',
            executor.submit(self._collect_interaction_evidence, ts_code, concepts): 'interaction',
            executor.submit(self._collect_report_evidence, ts_code, concepts): 'report',
            executor.submit(self._collect_announcement_evidence, ts_code, concepts): 'announcement'
        }
        
        evidence = {}
        for future in as_completed(futures):
            evidence_type = futures[future]
            try:
                evidence[evidence_type] = future.result(timeout=10)
            except Exception as e:
                logger.error(f"收集{evidence_type}证据失败: {e}")
                evidence[evidence_type] = []
```

### 第二阶段：功能完善（下午 2:00-5:00）

#### 2.1 完整的端到端测试（优先级：高）
创建`test_concept_agent_e2e.py`：
- 测试完整查询流程
- 验证所有证据类型
- 检查报告生成质量
- 性能基准测试

#### 2.2 报告格式优化（优先级：中）
- 添加执行摘要
- 增强表格可读性
- 添加风险提示
- 专业术语解释

#### 2.3 边界情况处理（优先级：中）
- 处理无数据情况
- 优化错误提示
- 增加输入验证
- 完善日志记录

### 第三阶段：系统集成（下午 5:00-6:00）

#### 3.1 API接入测试
- 测试ConceptAgent与main_modular.py集成
- 验证路由功能
- 检查响应格式

#### 3.2 性能监控
- 添加查询耗时统计
- 记录各阶段性能
- 生成性能报告

## 具体实施步骤

### Step 1: 创建性能优化模块（9:00-10:00）
1. 创建`utils/concept/performance_optimizer.py`
2. 实现缓存管理器
3. 实现并行执行器
4. 添加性能监控装饰器

### Step 2: 优化EvidenceCollector（10:00-11:00）
1. 集成缓存机制
2. 实现并行收集
3. 添加超时控制
4. 优化查询效率

### Step 3: 优化RAG查询（11:00-12:00）
1. 实现查询缓存
2. 优化查询构造
3. 添加重试机制
4. 实现降级策略

### Step 4: 创建E2E测试（14:00-15:00）
1. 设计测试用例
2. 实现自动化测试
3. 性能基准测试
4. 生成测试报告

### Step 5: 优化报告生成（15:00-16:00）
1. 改进报告模板
2. 增强数据可视化
3. 添加专业分析
4. 优化输出格式

### Step 6: 系统集成测试（16:00-17:00）
1. API集成测试
2. 性能压力测试
3. 文档更新
4. 准备发布

## 风险管理

### 技术风险
1. **RAG超时问题**
   - 缓解：实现本地缓存，降级到简单搜索
   - 监控：记录超时频率，优化查询

2. **并发问题**
   - 缓解：限制并发数，使用线程安全的数据结构
   - 测试：压力测试验证稳定性

3. **内存问题**
   - 缓解：限制缓存大小，实现LRU淘汰
   - 监控：内存使用率监控

### 时间风险
1. **进度延迟**
   - 缓解：优先完成核心功能
   - 调整：可推迟次要功能到Day 7

## 成功标准

### 性能指标
- [ ] 单次查询响应时间 < 10秒
- [ ] 缓存命中率 > 50%
- [ ] 并发处理能力 > 10 QPS
- [ ] RAG查询成功率 > 90%

### 功能指标
- [ ] 4种证据类型全部正常工作
- [ ] E2E测试通过率 100%
- [ ] 报告质量评分 > 8/10
- [ ] 错误处理覆盖率 100%

### 代码质量
- [ ] 单元测试覆盖率 > 80%
- [ ] 代码注释完整
- [ ] 文档更新及时
- [ ] 无critical级别bug

## 注意事项

1. **开发原则**
   - 保持代码质量，不为赶进度牺牲质量
   - 所有修改必须有测试覆盖
   - 重要决策记录在文档中

2. **测试要求**
   - 每个功能必须有对应测试
   - 性能优化必须有基准对比
   - 边界情况必须充分测试

3. **文档要求**
   - 及时更新技术文档
   - 记录性能优化效果
   - 更新API使用说明

4. **协作要求**
   - 定期提交代码
   - 重要节点更新进度
   - 遇到问题及时沟通

## 检查清单

### 开发前检查
- [x] 回顾Day 5成果和问题
- [x] 明确Day 6目标和优先级
- [x] 准备开发环境和测试数据
- [ ] 创建新的开发分支（如需要）

### 开发中检查
- [ ] 缓存机制实现并测试
- [ ] 并行收集实现并测试
- [ ] RAG优化完成并验证
- [ ] E2E测试编写并通过
- [ ] 报告格式优化完成
- [ ] 性能指标达标

### 开发后检查
- [ ] 所有测试通过
- [ ] 文档更新完成
- [ ] 代码review完成
- [ ] 性能报告生成
- [ ] Git提交并推送
- [ ] 准备Day 7计划