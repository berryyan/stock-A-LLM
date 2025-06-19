# 股票分析系统功能测试指南

## 前置准备

### 1. 环境激活
```bash
# Windows
stock_analysis_env\Scripts\activate

# Linux/Mac
source stock_analysis_env/bin/activate
```

### 2. 确认服务状态
```bash
# 检查系统健康状态
python scripts/utils/system_check.py

# 确认数据库连接
python scripts/tests/test_databases.py
```

## 功能测试步骤

### 一、API服务测试

#### 1. 启动API服务
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 访问文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 3. 健康检查
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
    "status": "healthy",
    "mysql": "connected",
    "milvus": "connected",
    "timestamp": "2025-06-15T..."
}
```

### 二、SQL查询功能测试

#### 1. 使用API测试SQL查询
```bash
# 测试实时股价查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
  }'

# 测试涨跌幅排行
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今天涨幅最大的10只股票",
    "query_type": "sql"
  }'

# 测试历史数据
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最近一个月的平均成交量",
    "query_type": "sql"
  }'
```

#### 2. 使用测试脚本
```bash
python scripts/tests/test_api.py
```

### 三、RAG查询功能测试

#### 1. 启动RAG查询界面
```bash
python rag_query_interface.py
```

#### 2. 测试查询示例
```
# 在交互界面中输入以下查询：
> 贵州茅台2024年第一季度营收情况
> 比较茅台和五粮液的毛利率
> /company 600519.SH
> /finance
```

#### 3. 使用API测试RAG
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析茅台的高端化战略",
    "query_type": "rag"
  }'
```

### 四、混合查询功能测试

```bash
# 测试智能路由
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析贵州茅台的财务状况和股价表现",
    "query_type": "hybrid"
  }'
```

### 五、文档处理功能测试

#### 1. 测试PDF下载功能
```bash
# 测试特定公司的PDF下载
python scripts/tests/test_cninfo_pdf.py
```

#### 2. 运行智能处理器
```bash
python smart_processor_v5_1.py

# 选择处理选项：
# 2 - 处理年度报告
# 3 - 处理季度报告
# 4 - 处理最近公告（带过滤）
```

### 六、数据维护功能测试

#### 1. Milvus去重检查
```bash
python scripts/maintenance/milvus_dedup_script_v2.py
```

#### 2. 批量处理管理
```bash
python scripts/maintenance/batch_process_manager.py
# 选择1查看进度
# 选择2开始新批次
```

### 七、性能测试

#### 1. 查询性能测试
```bash
python scripts/tests/performance_test.py
```

#### 2. 并发测试
```bash
python scripts/tests/concurrent_test.py
```

## 常见问题排查

### 1. Milvus集合未加载
```bash
python scripts/tools/load_milvus_collection.py
```

### 2. PDF下载失败
```bash
# 查看日志
tail -f logs/document_processor.log

# 手动测试下载
python scripts/debugging/test_pdf_download.py
```

### 3. API响应慢
```bash
# 检查系统资源
python scripts/analysis/system_monitor.py

# 查看慢查询日志
tail -f logs/slow_queries.log
```

## 测试报告模板

### 功能测试结果
| 功能模块 | 测试项 | 状态 | 响应时间 | 备注 |
|---------|--------|------|----------|------|
| SQL查询 | 实时股价 | ✅ | 5s | - |
| SQL查询 | 涨跌排行 | ✅ | 8s | - |
| RAG查询 | 财务查询 | ✅ | 3s | - |
| RAG查询 | 多公司对比 | ✅ | 5s | - |
| 混合查询 | 综合分析 | ✅ | 15s | - |
| API服务 | 健康检查 | ✅ | <1s | - |
| 文档处理 | PDF下载 | ✅ | 2-10s | - |

### 性能指标
- SQL查询平均响应：XX秒
- RAG查询平均响应：XX秒
- 并发支持：XX用户
- 系统稳定性：XX%

## 自动化测试

### 运行完整测试套件
```bash
# 运行所有测试
pytest tests/ -v

# 生成测试报告
pytest tests/ --html=reports/test_report.html
```

### 持续监控
```bash
# 启动监控服务
python scripts/monitoring/system_monitor.py

# 查看监控面板
http://localhost:8080/monitoring
```

---

**注意事项**：
1. 测试前确保数据库服务正常运行
2. 首次测试可能需要加载模型，耗时较长
3. 建议在非生产环境进行压力测试
4. 保留测试日志用于问题排查