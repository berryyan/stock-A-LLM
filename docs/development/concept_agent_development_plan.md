# Concept Agent 开发计划

版本：v1.0  
创建时间：2025-07-16  
预计开发周期：7-10天

## 1. 开发阶段划分

### Phase 1: 基础架构搭建（2天）
目标：建立Agent基本框架和核心数据结构

### Phase 2: 数据采集实现（2天）
目标：实现多源数据采集和缓存机制

### Phase 3: 评分系统实现（2天）
目标：实现配置化的三维评分系统

### Phase 4: LLM集成与输出（2天）
目标：集成LLM能力，生成专业报告

### Phase 5: 测试与优化（1-2天）
目标：完整测试，性能优化，bug修复

## 2. 详细开发步骤

### Day 1: 基础框架搭建

#### 上午任务（4小时）
1. **创建Agent主体结构**
   ```
   agents/concept_agent_modular.py  # 主Agent文件
   utils/concept/                   # 概念相关工具目录
   ├── input_processor.py          # 输入处理器
   ├── concept_matcher.py          # 概念匹配器
   └── scoring_config.py           # 评分配置
   ```

2. **实现输入处理器**
   - ConceptInputProcessor类
   - 输入类型识别（keyword/concept/news）
   - 基础测试用例

3. **创建数据模型**
   ```python
   # 概念股数据模型
   @dataclass
   class ConceptStock:
       ts_code: str
       name: str
       concept_names: List[str]
       scores: Dict[str, float]
       details: Dict[str, Any]
   ```

#### 下午任务（4小时）
4. **配置评分系统框架**
   - 创建scoring_config.py
   - 实现配置加载机制
   - 设计评分接口

5. **搭建缓存框架**
   - 实现CacheManager基类
   - 内存缓存（LRU）实现
   - 数据库缓存接口

6. **创建测试框架**
   - 单元测试基础结构
   - Mock数据准备
   - 测试工具函数

### Day 2: 概念匹配与LLM集成

#### 上午任务（4小时）
1. **实现概念数据访问层**
   ```python
   class ConceptDataAccess:
       def get_all_concepts(self) -> List[str]
       def get_concept_members(self, concept: str) -> List[str]
       def search_concepts(self, keyword: str) -> List[str]
   ```

2. **LLM概念扩展实现**
   - 第一次LLM调用接口
   - Prompt模板设计
   - 响应解析器

3. **概念匹配器实现**
   - 精确匹配
   - 模糊匹配
   - 降级策略

#### 下午任务（4小时）
4. **新闻文本处理**
   - 新闻解析prompt设计
   - 关键词提取逻辑
   - 测试用例编写

5. **交易日历缓存**
   - TradingCalendarCache实现
   - 本地文件存储
   - 自动更新机制

### Day 3: 数据采集层实现

#### 上午任务（4小时）
1. **资金流向数据采集**
   ```python
   class MoneyFlowCollector:
       async def get_daily_flow(self, ts_code: str)
       async def get_weekly_flow(self, ts_code: str)
       async def get_continuous_days(self, ts_code: str)
   ```

2. **板块数据采集**
   - 板块涨跌幅排名
   - 板块资金流向
   - 涨停股票统计

3. **批量采集优化**
   - 并发控制
   - 批量查询
   - 错误重试

#### 下午任务（4小时）
4. **技术指标采集（重点）**
   - Tushare API集成
   - stk_factor_pro数据获取
   - 前复权数据处理

5. **缓存策略实现**
   - 21天技术数据缓存
   - 更新检测机制
   - 过期数据清理

### Day 4: 盘后更新机制

#### 上午任务（4小时）
1. **定时任务框架**
   ```python
   class DailyUpdateScheduler:
       def schedule_update(self)
       def check_trading_day(self)
       def retry_mechanism(self)
   ```

2. **批量更新实现**
   - 全量股票列表获取
   - 分批更新策略
   - 进度跟踪

3. **更新日志记录**
   - 更新状态记录
   - 失败重试记录
   - 性能统计

#### 下午任务（4小时）
4. **按需更新机制**
   - 数据新鲜度检查
   - 用户提示机制
   - 增量更新实现

5. **容错处理**
   - API限流处理
   - 部分失败处理
   - 降级策略

### Day 5: 评分系统核心实现

#### 上午任务（4小时）
1. **概念关联度评分**
   ```python
   class ConceptRelevanceScorer:
       def score_board_membership(self, stock_data: Dict) -> float
       def score_leading_limit(self, stock_data: Dict) -> float
       def score_mentions(self, stock_data: Dict) -> float
   ```

2. **详细评分逻辑**
   - 板块成分股判断
   - 率先涨停计算
   - 财报/公告/互动提及统计

3. **评分配置应用**
   - 动态加载配置
   - 权重调整
   - 开关控制

#### 下午任务（4小时）
4. **资金流向评分**
   - 日周流入判断
   - 占比排名计算
   - 连续性统计

5. **技术形态评分**
   - MACD状态判断
   - 均线排列计算
   - 板块内对比

### Day 6: 评分系统完善

#### 上午任务（4小时）
1. **综合评分引擎**
   ```python
   class FlexibleScoringEngine:
       def calculate_total_score(self, stock: ConceptStock) -> Dict
       def rank_stocks(self, stocks: List[ConceptStock]) -> List
       def generate_score_details(self, stock: ConceptStock) -> Dict
   ```

2. **评分明细生成**
   - 各项得分记录
   - 扣分原因说明
   - 加分项目标注

3. **批量评分优化**
   - 并行计算
   - 结果缓存
   - 性能监控

#### 下午任务（4小时）
4. **评分测试**
   - 边界条件测试
   - 典型案例测试
   - 性能压力测试

5. **评分调优**
   - 参数微调
   - 权重优化
   - 阈值调整

### Day 7: LLM报告生成

#### 上午任务（4小时）
1. **报告模板设计**
   - Markdown格式模板
   - 动态内容填充
   - 表格生成器

2. **第二次LLM调用**
   - 报告生成prompt
   - TOP5详细分析
   - 板块整体分析

3. **LLM响应处理**
   - 结果解析
   - 格式化处理
   - 错误处理

#### 下午任务（4小时）
4. **完整报告组装**
   - 评分表格生成
   - 图表数据准备
   - 时间戳标注

5. **输出优化**
   - 内容排版
   - 重点突出
   - 可读性提升

### Day 8: 集成测试

#### 上午任务（4小时）
1. **端到端测试**
   - 完整流程测试
   - 各类输入测试
   - 异常情况测试

2. **性能测试**
   - 响应时间测试
   - 并发压力测试
   - 缓存效果测试

3. **兼容性测试**
   - 与现有Agent兼容
   - API接口测试
   - 数据格式验证

#### 下午任务（4小时）
4. **集成到系统**
   - 路由配置
   - API端点添加
   - 文档更新

5. **用户测试**
   - 真实案例测试
   - 反馈收集
   - 问题修复

### Day 9-10: 优化与完善

1. **性能优化**
   - 查询优化
   - 缓存优化
   - 并发优化

2. **功能完善**
   - 边界处理
   - 错误提示
   - 日志完善

3. **文档编写**
   - API文档
   - 使用指南
   - 部署文档

4. **上线准备**
   - 代码审查
   - 安全检查
   - 发布计划

## 3. 风险与应对

### 技术风险
1. **Tushare API限制**
   - 风险：调用频率限制导致数据更新失败
   - 应对：实现智能限流和重试机制

2. **LLM响应不稳定**
   - 风险：LLM输出格式不一致
   - 应对：严格的响应解析和降级策略

3. **性能瓶颈**
   - 风险：大量股票评分计算耗时
   - 应对：并行处理和缓存优化

### 业务风险
1. **数据质量问题**
   - 风险：概念分类不准确
   - 应对：多源数据交叉验证

2. **评分系统偏差**
   - 风险：评分权重不合理
   - 应对：配置化设计，便于调整

## 4. 里程碑

- **M1 (Day 2)**: 基础框架完成，可进行概念匹配
- **M2 (Day 4)**: 数据采集完成，可获取完整数据
- **M3 (Day 6)**: 评分系统完成，可计算股票得分
- **M4 (Day 8)**: 功能完整，可生成分析报告
- **M5 (Day 10)**: 优化完成，达到生产标准

## 5. 资源需求

### 开发资源
- 主开发人员：1人
- 代码审查：定期进行
- 测试支持：自动化测试

### 技术资源
- Tushare Pro账号（10000+积分）
- LLM API（DeepSeek）
- 数据库访问权限

### 测试数据
- 典型概念案例10个
- 测试股票池100只
- 历史数据3个月

---

文档版本：v1.0  
最后更新：2025-07-16