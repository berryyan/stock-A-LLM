# 测试环境使用指南

## 测试环境划分

### ✅ WSL2可执行的测试（<30秒）

1. **连通性测试**
   - API健康检查：`/health`
   - 简单SQL查询：`列出所有表`
   - 基础路由测试

2. **代码检查**
   - 语法检查
   - 类型检查
   - 文件存在性验证

3. **快速单元测试**
   - 工具函数测试
   - 简单组件渲染测试

### ❌ 必须在Windows执行的测试（>30秒）

1. **复杂查询测试**
   - 财务分析查询（通常需要1-2分钟）
   - 资金流向分析（通常需要1-3分钟）
   - RAG文档检索（可能需要30秒-2分钟）
   - 混合查询（可能需要1-5分钟）

2. **性能测试**
   - `performance_test.py`
   - 并发测试
   - 压力测试

3. **完整功能测试**
   - `comprehensive_verification.py`
   - `test_financial_agent.py`
   - `test_money_flow_analysis.py`

4. **端到端测试**
   - 完整用户流程
   - 多步骤操作
   - WebSocket实时通信

## 测试脚本示例

### WSL2快速测试脚本
```bash
#!/bin/bash
# quick_test_wsl2.sh
echo "🚀 WSL2快速测试"

# 1. API连通性
echo "测试API连接..."
curl -s http://10.0.0.66:8000/health | jq '.status' || echo "API未运行"

# 2. 简单查询（<30秒）
echo "测试简单查询..."
curl -s -X POST http://10.0.0.66:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "列出所有表", "query_type": "sql"}' \
  | jq '.success'

echo "✅ 快速测试完成"
```

### Windows完整测试命令
```powershell
# Windows PowerShell
# 1. 财务分析测试（预计2-3分钟）
python test_financial_agent.py

# 2. 资金流向测试（预计1-2分钟）
python test_money_flow_simple.py

# 3. 综合验证（预计5-10分钟）
python comprehensive_verification.py
```

## 记住原则

1. **Claude在WSL2开发时**：
   - 只做文件修改和快速验证
   - 不写长时间运行的测试脚本
   - 不执行复杂查询

2. **需要完整测试时**：
   - 明确告知用户："这个测试需要在Windows执行"
   - 提供具体的Windows测试命令
   - 不尝试在WSL2中运行

3. **超时处理策略**：
   - WSL2：最多等待30秒
   - Windows：用户手动执行，无超时限制