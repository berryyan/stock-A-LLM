# 股票分析系统功能测试指南

## 前置准备

### 1. 环境激活

#### 后端环境（Windows推荐）
```bash
# Windows Anaconda Prompt
conda activate stock-frontend

# 或使用venv
venv\Scripts\activate
```

#### 前端环境（双环境支持）
```bash
# 检查当前环境
cat frontend/.frontend-env

# WSL2开发环境
cd frontend && ./auto-switch-to-wsl2.sh

# Windows测试环境
cd frontend && switch-env.bat
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

### 五、财务分析功能测试 (v1.4.0+)

#### 财务分析功能分类
1. **财务健康度分析** ✅ 已测试
   - 四维度评分（盈利、偿债、运营、成长）
   - AAA-CCC评级体系
   
2. **杜邦分析（ROE分解）** ✅ 已测试
   - ROE = 净利率 × 总资产周转率 × 权益乘数
   - 多期趋势分析
   
3. **现金流质量分析** 🔍 待测试
   - 现金含量比率
   - 稳定性评分
   - 综合质量评级
   
4. **多期财务对比分析** 🔍 待测试
   - 同比/环比增长率
   - 趋势分析
   - 波动性评估

#### 1. 基础财务健康度分析
```bash
# 激活虚拟环境后运行
source venv/bin/activate && python test_financial_agent.py
```

#### 2. 正常测试用例
```bash
# 使用API测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析贵州茅台的财务健康度",
    "query_type": "financial"
  }'

# 支持的输入格式：
# - 公司名称：贵州茅台、国轩高科、药明康德
# - 6位股票代码：002047、301120
# - 完整证券代码：600519.SH、002074.SZ、301120.SZ
```

#### 3. 多期财务对比分析测试 (v1.4.3新增)
```bash
# 测试基础功能
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析贵州茅台的多期财务对比",
    "query_type": "financial"
  }'

# 支持的查询方式：
# - "分析XX的多期财务对比"
# - "XX的财务对比分析"
# - "XX最近几期的财务变化"
# - "比较XX不同时期的财务数据"

# 预期返回内容：
# - 同比增长率（营收、净利润、现金流、总资产、ROE）
# - 环比增长率（各项指标的季度环比）
# - 趋势分析（上升/下降/平稳/波动）
# - 波动性分析（稳定性评级）
# - 8期财务数据的综合分析报告
```

#### 4. 破坏性测试用例（应返回错误）
```bash
# 5位数字（应提示"股票代码格式不正确，请输入6位数字"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析02359的财务健康度",
    "query_type": "financial"
  }'

# 错误的后缀（应提示"证券代码格式不正确，后缀应为.SZ/.SH/.BJ"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析000000.SX的财务健康度",
    "query_type": "financial"
  }'

# 无效输入（应提示"无法识别输入内容"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析就不告诉你的财务健康度",
    "query_type": "financial"
  }'

# 不存在的股票（应提示"未找到财务数据"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析999999.BJ的财务健康度",
    "query_type": "financial"
  }'
```

#### 5. 完整测试脚本
```bash
# 运行完整的财务分析测试（包含正常和破坏性测试）
source venv/bin/activate && python test_financial_agent.py
source venv/bin/activate && python test_advanced_financial_features.py

# 详细的多期对比测试用例参见：
# docs/test_cases_financial_comparison.md
```

### 六、股票代码映射器测试 (v1.4.3新增)

#### 1. 测试映射器基础功能
```bash
# 运行映射器测试
source venv/bin/activate && python utils/stock_code_mapper.py
```

预期输出：
```
股票代码映射测试:
600519               -> 600519.SH
贵州茅台             -> 600519.SH
茅台                 -> 600519.SH
诺德股份             -> 600110.SH
```

#### 2. 测试API中的映射功能
```bash
# 测试使用公司名称的RAG查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析诺德股份的2024年年报",
    "query_type": "rag"
  }'
```

### 六、文档处理功能测试

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

## 系统功能测试优先级 (2025-06-26更新 - v3.1 React前端驱动策略)

### Phase 1: React MVP + 核心功能测试（第1周）

#### Day 1-3: React基础框架搭建
**开发任务清单**：
```typescript
// 必须完成的组件
- ChatInterface.tsx      // 主聊天界面
- MessageList.tsx        // 消息列表
- InputBox.tsx          // 多行输入框
- SimpleMarkdownRenderer.tsx // 基础Markdown渲染
- api.ts                // API调用封装
```

**验证要点**：
- [ ] 能发送消息到后端API
- [ ] 能正确显示返回结果
- [ ] Markdown基础格式正确渲染
- [ ] 错误处理机制完善

#### Day 4: SQL查询功能测试
**测试用例**：
```javascript
// 使用React界面测试
const sqlTestQueries = [
  "贵州茅台最新股价",
  "A股市值排名前10",
  "今日涨幅最大的10只股票",
  "平安银行最近5日股价"
];
```

#### Day 5: RAG和财务分析测试
**测试用例**：
```javascript
const ragFinancialQueries = [
  "贵州茅台最新公告",
  "分析茅台的财务健康度",
  "平安银行杜邦分析",
  "万科现金流质量分析",
  "比较茅台不同时期的财务数据"
];
```

#### Day 6: 资金流向和混合查询测试
**测试用例**：
```javascript
const moneyFlowQueries = [
  "茅台最近30天资金流向",
  "对比茅台和五粮液资金流向",
  "分析茅台的投资价值"  // 混合查询
];
```

#### Day 7: 问题汇总和修复
**问题分类模板**：
- 🔴 P0: 阻塞性问题（功能无法使用）
- 🟡 P1: 功能性问题（结果不正确）
- 🟢 P2: 体验性问题（可优化）

### 测试环境快速启动

#### 后端API启动
```bash
# Windows环境
venv\Scripts\activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### React前端启动
```bash
cd stock-analysis-frontend
npm install  # 首次运行
npm run dev  # 启动开发服务器
```

### React测试重点关注

1. **API通信测试**
   - 请求发送是否正确
   - 响应处理是否完整
   - 错误状态码处理

2. **数据展示测试**
   - 表格数据格式化
   - 长文本换行显示
   - Markdown渲染效果

3. **交互体验测试**
   - Loading状态显示
   - 错误提示友好性
   - 输入框自适应高度

4. **性能表现测试**
   - 大数据量渲染
   - 连续查询响应
   - 内存使用情况

---

**注意事项**：
1. 测试前确保数据库服务正常运行
2. 首次测试可能需要加载模型，耗时较长
3. 建议在非生产环境进行压力测试
4. 保留测试日志用于问题排查
5. 测试过程中发现的问题应立即记录到开发任务中

## 8. React前端测试 (v1.5.0+)

### 8.1 环境准备
```bash
# Windows环境启动前端
cd E:\PycharmProjects\stock_analysis_system\frontend
npm run dev

# Windows环境启动API
cd E:\PycharmProjects\stock_analysis_system
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 8.2 基础功能测试

#### 界面布局测试
- [ ] 260px侧边栏正确显示
- [ ] 主聊天区域居中对齐
- [ ] 底部输入框响应式布局
- [ ] Claude.ai绿色主题(#10a37f)正确应用

#### 查询功能测试
```
测试查询列表：
1. "贵州茅台最新股价"
2. "分析茅台的财务健康度"
3. "查询贵州茅台最新公告"
4. "茅台的资金流向分析"
5. "比较茅台最近5期财务数据"
```

#### Markdown渲染测试
- [ ] 代码块语法高亮
- [ ] 表格正确格式化
- [ ] 链接可点击并在新标签页打开
- [ ] 引用块样式正确
- [ ] 数学公式渲染（如有）

### 8.3 错误处理测试
- [ ] API未启动时显示友好错误提示
- [ ] 网络超时处理
- [ ] 空查询阻止发送
- [ ] 加载状态正确显示

#### Claude.ai风格测试
- [ ] AI回复无边框直接显示
- [ ] 用户消息带浅灰背景
- [ ] 消息间距和对齐正确
- [ ] 时间戳位置合理

#### 侧边栏折叠测试
- [ ] 折叠/展开按钮正常工作
- [ ] 折叠时只显示图标
- [ ] 打开文档时自动折叠
- [ ] 折叠动画流畅

#### 分屏体验测试
- [ ] 点击"查看数据/文档/详情"按钮正常打开右侧面板
- [ ] 主聊天区域自动调整宽度
- [ ] 分屏时内容显示不拥挤
- [ ] 关闭文档面板后布局恢复

#### 分屏布局一致性测试 (v1.5.3新增)
- [ ] 分屏模式下消息容器与输入框宽度完全对齐
- [ ] 非分屏模式下布局居中显示正常
- [ ] 消息区域和输入框的左右边距一致
- [ ] 整体视觉效果专业、整齐

### 8.3 错误处理测试
- [ ] API未启动时显示友好错误提示
- [ ] 网络超时处理
- [ ] 空查询阻止发送
- [ ] 加载状态正确显示

### 8.4 响应式测试
- [ ] 1920x1080分辨率正常
- [ ] 1366x768分辨率正常
- [ ] 移动端布局（可选）