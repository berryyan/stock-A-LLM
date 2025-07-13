# v2.3.0 正确的测试脚本清单

根据我们之前的测试工作，以下是每个Agent应该使用的测试脚本：

## 1. SQL Agent
- **脚本**: `test_sql_agent_comprehensive.py`
- **测试用例数**: 64个
- **之前达到的通过率**: 100%
- **备注**: 这是模块化版本的综合测试，包含了所有SQL查询类型

## 2. Money Flow Agent
- **脚本**: `test_money_flow_agent_comprehensive_final.py`
- **测试用例数**: 64个
- **之前达到的通过率**: 100%
- **备注**: 这是最终修复版本，解决了所有验证和路由问题

## 3. Financial Agent
- **脚本**: `test_financial_agent_comprehensive_windows.py`
- **测试用例数**: 63个
- **之前达到的通过率**: 100%（95.3% -> 100%，通过添加"的"修复）
- **备注**: Windows专用版本，包含了边界问题修复

## 4. RAG Agent
- **脚本**: `test_rag_agent_comprehensive.py`
- **测试用例数**: 72个
- **之前达到的通过率**: 70.8%
- **备注**: 受限于Milvus数据可用性，这是可接受的通过率

## 5. Hybrid Agent
- **脚本**: `test_hybrid_agent_comprehensive.py`
- **测试用例数**: 13个基础用例 + 复合查询测试
- **之前达到的通过率**: ~90%（复合查询已修复）
- **备注**: 包含了复合查询修复后的测试

## 测试执行命令

在Windows Anaconda Prompt中执行：

```bash
# 确保API服务运行在8001端口
conda activate stock-frontend

# SQL Agent测试
python test_sql_agent_comprehensive.py

# Money Flow Agent测试
python test_money_flow_agent_comprehensive_final.py

# Financial Agent测试
python test_financial_agent_comprehensive_windows.py

# RAG Agent测试
python test_rag_agent_comprehensive.py

# Hybrid Agent测试
python test_hybrid_agent_comprehensive.py
```

## 重要提醒

1. 这些都是我们之前精心设计和调试过的测试脚本
2. 每个脚本都包含了完整的测试用例集
3. 测试用例基于test-guide-comprehensive.md文档设计
4. 不要随意创建新的测试脚本，应该使用这些验证过的版本