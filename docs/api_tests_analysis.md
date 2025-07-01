# API测试用例分析报告

## 概述
本文档分析了test-guide.md中的API测试用例，评估其在当前版本的适用性，并提供转换为前端查询测试的建议。

## API测试用例分类与分析

### 一、基础API测试（仍然适用）

#### 1. 健康检查API ✅
```bash
curl http://localhost:8000/health
```
**状态**: 适用
**说明**: 系统健康检查接口，用于监控服务状态
**转换建议**: 保留为API测试，无需转换

#### 2. API文档访问 ✅
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**状态**: 适用
**说明**: API文档接口，开发必需
**转换建议**: 保留为API测试

### 二、通用查询API（部分可转换）

#### 1. /api/query 接口测试
**状态**: 适用但建议转换
**原因**: 此接口是前端调用的核心接口

**可转换的测试用例**:
```bash
# 原API测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
  }'

# 转换为前端查询测试
在前端界面输入：贵州茅台最新股价
预期：快速返回股价数据
```

### 三、专用API接口（建议保留）

#### 1. 财务分析专用接口 ⚠️
```bash
curl -X POST http://localhost:8000/financial-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "stock": "600519.SH",
    "analysis_type": "health_score"
  }'
```
**状态**: 可能已废弃
**说明**: 前端可能直接使用/api/query接口
**建议**: 验证是否仍在使用，如已废弃则删除

#### 2. 资金流向专用接口 ⚠️
```bash
curl -X POST http://localhost:8000/money-flow-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "stock": "300750.SZ",
    "days": 30
  }'
```
**状态**: 可能已废弃
**建议**: 同上

### 四、批量和历史查询API（保留）

#### 1. 批量查询接口 ❓
```bash
curl -X POST http://localhost:8000/api/batch-query
```
**状态**: 需验证是否实现
**建议**: 如已实现则保留，否则标记为"计划功能"

#### 2. 历史查询接口 ❓
```bash
curl -X GET http://localhost:8000/api/query-history?limit=10
```
**状态**: 需验证是否实现
**建议**: 同上

## 转换建议汇总

### 完全转换为前端测试的用例

1. **SQL查询类**
   - 股价查询
   - 涨跌幅排名
   - 市值排名
   - 成交额排名
   - K线查询
   - 估值指标查询

2. **RAG查询类**
   - 公告查询
   - 研报分析
   - 财务报告查询

3. **财务分析类**
   - 财务健康度分析
   - 杜邦分析
   - 多期对比
   - 现金流分析

4. **资金流向类**
   - 个股资金流向
   - 资金流向对比

### 保留为API测试的用例

1. **系统接口**
   - 健康检查 (/health)
   - API文档 (/docs, /redoc)

2. **特殊功能**（如果存在）
   - 批量查询接口
   - 历史记录接口
   - WebSocket连接测试

3. **错误处理测试**
   - 恶意输入测试
   - SQL注入防护测试
   - 参数验证测试

## 更新后的测试结构建议

### test-guide-v2.md 结构优化
```
1. 前端查询测试（主要部分）
   - SQL查询测试
   - 财务分析测试
   - 资金流向测试
   - RAG文档查询测试
   - 混合查询测试
   - 界面功能测试

2. 测试脚本集合
   - 自动化测试脚本
   - 性能测试脚本
   - 集成测试脚本

3. API接口测试（精简版）
   - 系统健康检查
   - 错误处理验证
   - 特殊功能测试

4. 性能基准测试
   - 查询性能指标
   - 并发测试结果

5. 问题排查指南
   - 常见问题解决
   - 日志查看方法
   - 调试工具使用
```

## 实施步骤

1. **验证API端点**
   ```bash
   # 检查哪些API端点仍在使用
   grep -r "app.post\|app.get" api/main.py
   ```

2. **更新测试文档**
   - 移除已废弃的API测试
   - 将可转换的测试改写为前端测试
   - 保留必要的API测试

3. **创建API测试验证脚本**
   ```python
   # verify_api_endpoints.py
   import requests
   
   endpoints = [
       ("/health", "GET"),
       ("/api/query", "POST"),
       ("/financial-analysis", "POST"),
       ("/money-flow-analysis", "POST"),
       ("/api/batch-query", "POST"),
       ("/api/query-history", "GET")
   ]
   
   for endpoint, method in endpoints:
       # 测试端点是否存在
   ```

## 结论

大部分API测试用例可以转换为更直观的前端查询测试，这样更符合实际使用场景。保留少量必要的API测试用于系统监控和特殊功能验证。建议定期review API接口，及时更新测试文档。