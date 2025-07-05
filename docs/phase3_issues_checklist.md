# Phase 3 模块化Agent问题清单

**创建时间**: 2025-07-06  
**状态**: 待修复

## 测试结果总结

### ✅ 成功的部分
1. 所有模块化Agent都已创建
2. 参数提取器工作正常
3. 股票验证功能正常
4. 所有Agent初始化成功（除了Hybrid Agent）

### ❌ 需要修复的问题

## 1. RAG Agent 问题

### 问题1.1: MilvusConnector接口不匹配
- **错误信息**: `MilvusConnector.search() got an unexpected keyword argument 'expr'`
- **原因**: RAG Agent模块化版本使用了不兼容的参数调用MilvusConnector
- **位置**: rag_agent_modular.py中的搜索调用
- **修复方案**: 检查MilvusConnector.search()的正确参数格式

### 问题1.2: date_intelligence未定义
- **错误信息**: `name 'date_intelligence' is not defined`
- **原因**: 在某些代码路径中date_intelligence未导入或使用错误
- **位置**: rag_agent_modular.py
- **修复方案**: 确保正确导入和使用date_intelligence

## 2. Financial Agent 问题

### 问题2.1: 父类方法调用错误
- **错误信息**: `'super' object has no attribute '_identify_analysis_type'`
- **原因**: 模块化版本错误地调用了父类的私有方法
- **位置**: financial_agent_modular.py
- **修复方案**: 
  - 直接调用父类的公开方法
  - 或在子类中重新实现该方法

## 3. Money Flow Agent 问题

### 问题3.1: 父类方法调用错误
- **错误信息**: `'super' object has no attribute '_identify_query_type'`
- **原因**: 同Financial Agent类似的问题
- **位置**: money_flow_agent_modular.py 第251行
- **修复方案**: 
  - 检查父类是否真的有此方法
  - 如果是私有方法，需要在子类中重新实现

## 4. Hybrid Agent 问题

### 问题4.1: 缺少方法实现
- **错误信息**: `'HybridAgentModular' object has no attribute '_create_routing_prompt'`
- **原因**: 模块化版本继承了父类但缺少必要的方法实现
- **位置**: hybrid_agent_modular.py
- **修复方案**: 
  - 检查父类的初始化流程
  - 实现缺失的方法或调整初始化逻辑

## 修复优先级（按照"优先修复公共模块"原则）

1. **高优先级**：
   - MilvusConnector接口问题（影响所有RAG查询）
   - 父类方法调用问题（影响继承架构）

2. **中优先级**：
   - date_intelligence导入问题
   - Hybrid Agent方法实现

## 修复计划

### Step 1: 检查MilvusConnector接口
- 查看database/milvus_connector.py中search方法的正确参数
- 更新RAG Agent的调用方式

### Step 2: 修复父类方法调用
- 检查各个Agent的父类实现
- 确定私有方法是否应该被子类调用
- 必要时在子类中重新实现

### Step 3: 完善Hybrid Agent
- 检查父类的完整初始化流程
- 实现所有必要的方法

### Step 4: 修复其他小问题
- date_intelligence导入
- 其他边界情况

## 测试验证计划

1. 单独测试每个修复的Agent
2. 运行集成测试
3. 验证向后兼容性
4. 性能测试