# 模块化Agent测试指南

## 测试脚本概述

本项目提供四个层次的模块化Agent测试体系：

### 1. test_quick_smoke.py - 快速冒烟测试
- **测试用例数**: 5个（每个Agent一个核心功能）
- **执行时间**: 约1分钟
- **适用场景**: 
  - 快速验证修复效果
  - 日常开发中的快速检查
  - CI/CD快速验证
- **测试内容**:
  - SQL Agent: 股价查询
  - RAG Agent: 发展战略查询
  - Financial Agent: 财务健康度分析
  - Money Flow Agent: 主力资金查询
  - Hybrid Agent: 复合查询测试

### 2. test_modular_smoke.py - 基础功能测试
- **测试用例数**: 15个
- **执行时间**: 约5分钟
- **适用场景**:
  - 功能验证
  - 版本发布前的基础测试
  - 日常回归测试
- **测试内容**:
  - SQL Agent: 4个测试（股价、财务数据、排名、错误处理）
  - RAG Agent: 2个测试（公告搜索、关键词搜索）
  - Financial Agent: 2个测试（财务健康度、杜邦分析）
  - Money Flow Agent: 2个测试（主力资金、资金流向）
  - Hybrid Agent: 5个测试（各类路由、错误传递）

### 3. 单Agent综合测试套件
每个Agent都有独立的综合测试文件：
- **test_sql_agent_comprehensive.py**
  - 测试用例数: 144+（覆盖18个SQL模板）
  - 功能类别: 18个（股价、成交量、估值、K线、排名等）
  - 执行时间: 约10-15分钟

- **test_rag_agent_comprehensive.py**
  - 测试用例数: 64+
  - 功能类别: 8个（公告查询、时间范围、主题分析等）
  - 执行时间: 约10分钟

- **test_financial_agent_comprehensive.py**
  - 测试用例数: 64+
  - 功能类别: 8个（财务健康度、杜邦分析、现金流等）
  - 执行时间: 约10-15分钟

- **test_money_flow_agent_comprehensive.py**
  - 测试用例数: 64+
  - 功能类别: 8个（资金流向、主力资金、板块资金等）
  - 执行时间: 约10分钟

- **test_hybrid_agent_comprehensive.py**
  - 测试用例数: 64+
  - 功能类别: 8个（智能路由、复合查询、投资价值等）
  - 执行时间: 约10分钟

### 4. 全Agent综合测试与分析工具
- **test_all_agents_comprehensive.py**
  - 功能: 一键运行所有5个Agent的综合测试
  - 总测试用例: 400+
  - 执行时间: 约20-30分钟
  - 生成汇总报告: all_agents_comprehensive_results.json

- **analyze_test_results.py**
  - 功能: 分析已有测试结果，无需重新运行测试
  - 支持生成汇总报告、分析特定Agent、列出失败测试
  - 交互式界面，方便快速查看结果

## 测试执行方法

### Windows环境（推荐）
```bash
# 激活虚拟环境
venv\Scripts\activate

# 快速验证
python test_quick_smoke.py             # 1分钟快速测试

# 基础测试
python test_modular_smoke.py           # 5分钟基础测试

# 单Agent综合测试
python test_sql_agent_comprehensive.py      # SQL Agent完整测试
python test_rag_agent_comprehensive.py      # RAG Agent完整测试
python test_financial_agent_comprehensive.py # Financial Agent完整测试
python test_money_flow_agent_comprehensive.py # Money Flow Agent完整测试
python test_hybrid_agent_comprehensive.py   # Hybrid Agent完整测试

# 全部Agent综合测试
python test_all_agents_comprehensive.py     # 运行所有Agent测试（20-30分钟）

# 分析测试结果
python analyze_test_results.py              # 交互式结果分析工具
```

### WSL2环境
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行方式与Windows相同
python test_quick_smoke.py
python test_sql_agent_comprehensive.py
# ... 其他测试脚本
```

## 测试结果说明

### 1. 控制台输出
- 实时显示每个测试用例的执行情况
- 包含测试名称、状态（✅通过/❌失败）、耗时
- 最后显示汇总统计

### 2. JSON结果文件
- `smoke_test_results.json` - test_modular_smoke.py的结果
- `sql_agent_comprehensive_results.json` - SQL Agent综合测试结果
- `rag_agent_comprehensive_results.json` - RAG Agent综合测试结果  
- `financial_agent_comprehensive_results.json` - Financial Agent综合测试结果
- `money_flow_agent_comprehensive_results.json` - Money Flow Agent综合测试结果
- `hybrid_agent_comprehensive_results.json` - Hybrid Agent综合测试结果
- `all_agents_comprehensive_results.json` - 全部Agent测试汇总结果
- 每个文件包含详细的测试结果、错误信息和功能统计

### 3. 测试报告解读
```
总测试数: 44
通过: 40 (90.9%)
失败: 4 (9.1%)

各Agent测试情况:
Agent                总数     通过     失败     正向通过    负向通过   
SQLAgentModular      12       10       2        7          3         
RAGAgentModular      8        7        1        5          2         
...
```

## 测试策略建议

### 日常开发流程
1. 修改代码后运行 `test_quick_smoke.py` 快速验证
2. 功能开发完成后运行 `test_modular_smoke.py` 确保基础功能正常
3. 提交代码前运行 `test_modular_comprehensive.py` 进行全面测试

### 问题排查流程
1. 如果 `test_quick_smoke.py` 失败，说明核心功能受损
2. 运行 `test_modular_comprehensive.py` 找出所有失败的测试用例
3. 查看JSON结果文件获取详细错误信息
4. 针对性修复后重新测试

### 版本发布流程
1. 必须通过 `test_modular_comprehensive.py` 所有测试
2. 正向测试通过率应达到95%以上
3. 负向测试（错误处理）通过率应达到100%
4. 保存测试结果作为版本记录

## 常见问题

### Q: 测试失败但不确定原因？
A: 查看对应的JSON结果文件，里面有详细的错误信息。

### Q: 某个Agent的测试全部失败？
A: 可能是该Agent初始化失败，检查数据库连接、API配置等。

### Q: 测试时间过长？
A: 可以先运行quick或smoke测试，只在必要时运行comprehensive测试。

### Q: 如何添加新的测试用例？
A: 在test_modular_comprehensive.py中使用@runner.test_case装饰器添加，注意指定正确的category（positive/negative）。

## 测试用例设计原则

1. **正向测试**: 验证功能正常工作
   - 使用真实有效的输入
   - 覆盖主要使用场景
   - 验证返回结果的正确性

2. **负向测试**: 验证错误处理
   - 使用无效输入（空查询、错误格式等）
   - 验证错误信息的准确性
   - 确保系统不会崩溃

3. **边界测试**: 验证极限情况
   - 特殊字符、超长输入
   - 日期边界（如未来日期）
   - 并发和性能极限

## 版本历史

- v2.2.3 (2025-07-07): 创建完整的综合测试套件
  - 每个Agent独立的comprehensive测试文件（400+测试用例）
  - 新增test_all_agents_comprehensive.py一键运行工具
  - 新增analyze_test_results.py结果分析工具
  - 更新测试体系为四层架构
- v2.2.2 (2025-07-06): 创建三层测试体系，新增comprehensive测试脚本
- v2.2.1 (2025-07-06): 修复测试兼容性问题
- v2.2.0 (2025-07-06): 模块化架构完成，创建基础测试脚本