# Concept Agent 综合测试指南

## 概述

本文档说明如何在Windows环境下运行Concept Agent的综合测试。测试脚本不设置超时时间，会完整测试所有功能模块。

## 测试环境要求

### 系统要求
- Windows 10/11
- Python 3.8+
- Anaconda（推荐）或标准Python环境

### 依赖包
```bash
langchain>=0.1.0
langchain-openai
fastapi
pymysql
pandas
numpy
sentence-transformers
```

### 数据库连接
- MySQL数据库可访问
- Milvus向量数据库可访问
- `.env`文件配置正确

## 运行测试

### 方法1：使用Python启动器（推荐）

```bash
# 在Anaconda Prompt或命令行中
python run_comprehensive_test.py
```

优点：
- 自动检查环境
- 提供详细的运行信息
- 自动显示测试结果摘要

### 方法2：使用批处理文件

```bash
# 双击运行或在命令行中
run_comprehensive_test.bat
```

### 方法3：直接运行测试脚本

```bash
python test_concept_agent_comprehensive_windows.py
```

## 测试内容

### 1. 基本功能测试
- 单一概念查询
- 多概念查询
- 板块查询
- 问句形式查询

### 2. 性能测试
- 缓存效果测试
- 批量查询性能
- 响应时间统计

### 3. 证据系统测试
- 软件收录证据
- 互动平台证据
- 财报证据（通过RAG）
- 公告证据（通过RAG）

### 4. 错误处理测试
- 空查询处理
- 超长查询处理
- 特殊字符处理
- 无效概念处理

### 5. 系统集成测试
- 完整查询流程
- 各模块协同工作
- 优化器集成效果

## 测试输出

### 1. 实时日志
- 控制台实时输出
- 保存到文件：`concept_agent_test_YYYYMMDD_HHMMSS.log`

### 2. 测试报告
- JSON格式：`concept_agent_test_report_YYYYMMDD_HHMMSS.json`
- 包含所有测试结果和性能数据

### 3. 测试摘要
测试完成后会显示：
- 各类测试的通过率
- 性能指标（缓存加速比、平均响应时间等）
- 证据收集统计
- 错误处理统计

## 预期结果

### 正常情况
- 基本功能测试：通过率 > 80%
- 缓存加速比：> 10x
- 平均响应时间：< 10秒
- 证据收集：每只股票至少有1种证据
- 错误处理：100%正确处理

### 常见问题

#### 1. RAG查询超时
- 现象：财报/公告证据收集慢
- 原因：Milvus查询或LLM响应慢
- 解决：检查网络连接，优化查询

#### 2. 数据库连接失败
- 现象：初始化失败
- 原因：数据库配置错误或网络问题
- 解决：检查.env配置，测试数据库连接

#### 3. 内存不足
- 现象：测试中断或变慢
- 原因：模型加载占用大量内存
- 解决：关闭其他程序，增加虚拟内存

## 测试时间

完整测试预计需要：
- 基本功能测试：2-3分钟
- 性能测试：2-3分钟
- 证据系统测试：3-5分钟
- 错误处理测试：1分钟
- 集成测试：1-2分钟

**总计：10-15分钟**

## 测试后分析

### 查看日志
```python
# 查看测试日志
with open('concept_agent_test_20250718_150000.log', 'r', encoding='utf-8') as f:
    print(f.read())
```

### 分析报告
```python
import json

# 加载测试报告
with open('concept_agent_test_report_20250718_150000.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

# 分析基本功能测试
basic_tests = report['results']['basic_tests']
success_rate = sum(1 for t in basic_tests if t['success']) / len(basic_tests)
print(f"基本功能测试通过率: {success_rate:.1%}")
```

## 持续集成建议

1. **定期运行**：每天运行一次完整测试
2. **版本对比**：保存历史测试结果，对比性能变化
3. **自动告警**：测试失败时自动通知
4. **性能基准**：建立性能基准线，监控退化

## 注意事项

1. **不要中断测试**：测试脚本没有设置超时，需要耐心等待完成
2. **资源占用**：测试期间会占用较多CPU和内存
3. **网络要求**：需要稳定的网络连接访问LLM API
4. **数据一致性**：测试结果可能因数据更新而变化

## 联系支持

如遇到问题，请提供：
1. 完整的日志文件
2. 测试报告JSON文件
3. 环境信息（Python版本、依赖包版本等）
4. 错误截图或详细描述