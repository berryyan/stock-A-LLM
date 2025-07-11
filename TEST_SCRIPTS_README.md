# 测试脚本说明文档

## Money Flow Agent 测试脚本

### 当前版本
- **test_money_flow_agent_comprehensive_final.py** - 最终版本（推荐使用）
  - 创建时间：2025-07-10
  - 测试用例：64个（8个功能 × 8个用例）
  - 测试标准：严格遵循"每个功能5个正确用例+3个错误用例"
  - 特点：
    - 系统化的功能分类
    - 完整的结果验证（包含expected_contains）
    - 详细的测试报告
    - 符合SQL Agent测试脚本的标准

### 归档版本
所有旧版本已移至 `scripts/tests/archived_money_flow_tests/` 目录：
- test_money_flow_agent_comprehensive.py - 早期综合测试版本
- test_money_flow_agent_comprehensive_v2.py - 基于新理解的v2版本
- test_money_flow_debug.py - 调试专用脚本
- 其他早期版本...

### 运行方式
```bash
# Windows环境（推荐）
python test_money_flow_agent_comprehensive_final.py

# WSL2环境（需要激活虚拟环境）
source venv/bin/activate && python test_money_flow_agent_comprehensive_final.py
```

### 测试覆盖的功能
1. **个股深度分析** - Money Flow Agent的核心功能
2. **行为模式识别** - 建仓、洗盘、出货等判断
3. **术语标准化** - 非标准术语自动转换
4. **时间周期分析** - 支持天、周、月等周期
5. **SQL路由识别** - 正确识别应该路由到SQL Agent的查询
6. **板块分析** - 当前限制和未来规划
7. **多股票对比** - 对比分析功能
8. **基础输入验证** - 错误处理和边界情况

### 预期结果
- 通过率目标：>80%
- 已知问题：
  - 股票简称会被拒绝（这是设计决策）
  - 板块深度分析当前不支持
  - 部分复杂查询的股票提取可能失败

## Financial Agent 测试脚本

### 当前版本
- **test_financial_agent_comprehensive_fixed.py** - 修复版本
  - 创建时间：2025-07-09
  - 测试用例：约90个
  - 待调试至100%通过率

## Hybrid Agent 测试脚本

### 当前版本
- **test_hybrid_agent_comprehensive_fixed.py** - 修复版本
  - 创建时间：2025-07-09
  - 测试用例：约40个
  - 包含路由测试功能
  - 待调试至100%通过率

## SQL Agent 测试脚本

### 当前版本
- **test_sql_agent_comprehensive.py** - 标准版本
  - 作为其他Agent测试脚本的参考标准
  - 测试框架简洁清晰
  - 通过率：98%+