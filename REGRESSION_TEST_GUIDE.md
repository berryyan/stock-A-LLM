# v2.3.0 回归测试指南

## 测试准备

### 1. 环境要求
- Windows操作系统（原生环境，非WSL2）
- Anaconda已安装
- stock-frontend conda环境已配置

### 2. 启动服务
在开始测试前，请确保以下服务正在运行：

```bash
# 窗口1：启动模块化API服务（端口8001）
conda activate stock-frontend
python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001
```

## 运行测试

### 方法一：批量运行（推荐）

1. 打开Anaconda Prompt
2. 激活环境：
   ```bash
   conda activate stock-frontend
   cd E:\PycharmProjects\stock_analysis_system
   ```
3. 运行批处理脚本：
   ```bash
   run_regression_tests_windows.bat
   ```

### 方法二：单独运行每个测试

如果批量运行有问题，可以单独运行每个测试：

```bash
# 1. SQL Agent测试（预计5-10分钟）
python test_sql_agent_comprehensive_windows.py > test_results\sql_agent_regression_20250712.txt 2>&1

# 2. Money Flow Agent测试（预计5-10分钟）
python test_money_flow_agent_comprehensive_final.py > test_results\money_flow_regression_20250712.txt 2>&1

# 3. Financial Agent测试（预计30-45分钟，LLM响应慢）
python test_financial_agent_comprehensive_windows.py > test_results\financial_regression_20250712.txt 2>&1

# 4. RAG Agent测试（预计15-20分钟）
python test_rag_agent_comprehensive.py > test_results\rag_agent_regression_20250712.txt 2>&1

# 5. Hybrid Agent测试（预计2-3分钟）
python test_hybrid_quick_verify.py > test_results\hybrid_agent_regression_20250712.txt 2>&1
```

## 分析结果

测试完成后，运行分析脚本：

```bash
python analyze_regression_results.py
```

这将生成一个综合分析报告：`test_results/regression_analysis_20250712.md`

## 注意事项

1. **测试时间**：
   - 全部测试预计需要60-90分钟
   - Financial Agent测试特别慢（LLM响应）
   - 建议在系统负载较低时运行

2. **常见问题**：
   - 如果API服务未启动，测试会失败
   - 如果超时，可以单独重新运行该测试
   - 测试结果会保存在test_results目录

3. **结果判定**：
   - SQL Agent期望100%通过率
   - Money Flow Agent期望100%通过率
   - Financial Agent期望100%通过率
   - Hybrid Agent期望90%+通过率
   - RAG Agent已知有数据问题，70%+即可

## 向Claude反馈结果

请将以下文件发送给Claude：
1. `test_results/regression_analysis_20250712.md` - 自动生成的分析报告
2. 如有特殊错误，可提供具体的测试日志文件