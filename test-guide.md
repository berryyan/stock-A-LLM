# 股票分析系统功能测试指南

**版本**: v2.1.2
**更新日期**: 2025-06-30
**说明**: 包含7-Agent架构测试方案（含3个待实现的新Agent）、SQL Agent快速模板测试

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

#### 4. 破坏性测试用例（应返回错误）- v1.5.5更新
```bash
# 5位数字（应提示"股票代码应为6位数字，您输入了5位"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析02359的财务健康度",
    "query_type": "financial"
  }'

# 错误的后缀（应提示"证券代码格式错误：后缀'SX'不正确，应为.SZ/.SH/.BJ"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析000000.SX的财务健康度",
    "query_type": "financial"
  }'

# 大小写错误（v1.5.5新增 - 应提示"证券代码后缀大小写错误，应为.SH"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "600519.sh最新股价",
    "query_type": "sql"
  }'

# 简称提示（v1.5.5新增 - 应提示"请使用完整公司名称，如：贵州茅台"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "茅台最新股价",
    "query_type": "sql"
  }'

# 无效输入（应提示"无法识别输入内容"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析就不告诉你的财务健康度",
    "query_type": "financial"
  }'

# 不存在的股票（v1.5.5改进 - 应提示"股票代码999999.BJ不存在，请检查是否输入正确"）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "999999.BJ最新股价",
    "query_type": "sql"
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

### 六、股票识别测试 (v2.1.2修复)

#### 1. 测试"平安"歧义修复
```bash
# 测试平安相关查询
source venv/bin/activate && python test_pingan_fix.py
```

预期输出：
```
查询: 平安银行PE
✅ 查询成功
结果: 平安银行（000001.SZ）在2025-06-23的估值指标...

查询: 中国平安PE  
✅ 查询成功
结果: 中国平安（601318.SH）在2025-06-23的估值指标...
```

#### 2. 测试股票简称映射
```bash
# 测试简称映射修复
source venv/bin/activate && python test_short_name_fix.py
```

#### 3. 测试简称歧义性分析
```bash
# 运行歧义性分析脚本
source venv/bin/activate && python check_short_name_ambiguity.py
```

查看生成的报告：`SHORT_NAME_AMBIGUITY_REPORT.md`

### 七、数据库Schema中文映射测试 (v2.0新增)

#### 1. 测试Schema缓存管理器
```bash
# 测试动态Schema读取和中文查询解析
source venv/bin/activate && python test_schema_mapping.py
```

预期输出：
```
缓存统计信息:
- 表数量: 14
- 字段总数: 500+
- 中文字段名数量: 400+

数据库表列表:
1. tu_anns_d - 公告数据表
2. tu_balancesheet - 资产负债表
3. tu_cashflow - 现金流量表
...

测试中文查询解析:
查询: 查询贵州茅台最新股价
查询类型: stock_price
生成SQL: SELECT open, high, low, close, vol, amount FROM tu_daily_detail WHERE ts_code = '600519.SH' AND trade_date >= DATE_SUB(CURDATE(), INTERVAL 0 DAY)
```

#### 2. 测试中文字段映射
```python
# 测试代码示例
from utils.schema_cache_manager import SchemaCacheManager

manager = SchemaCacheManager()

# 测试表名映射
print(manager.get_table_by_chinese("股票日线行情"))  # -> tu_daily_detail

# 测试字段映射
field_info = manager.get_field_by_chinese("收盘价")
print(f"{field_info['table']}.{field_info['field']}")  # -> tu_daily_detail.close
```

#### 3. 测试自然语言查询解析
```python
from utils.chinese_query_parser import ChineseQueryParser

parser = ChineseQueryParser()

# 解析查询
result = parser.parse_query("茅台最近30天的收盘价和成交量")
print(result)
# {
#   "query_type": "stock_price",
#   "tables": ["tu_daily_detail"],
#   "fields": ["close", "vol"],
#   "conditions": {"ts_code": "600519.SH", "days": 30}
# }
```

### 八、SQL Agent快速模板测试 (v2.1.2新增)

#### 1. 运行快速模板测试
```bash
# 测试SQL Agent快速模板功能
source venv/bin/activate && python test_sql_quick_templates.py
```

预期输出：
```
测试统计:
总测试数: 9
成功数: 8
使用快速路径: 4
快速路径平均响应时间: 0.02秒
非快速路径平均响应时间: 51.13秒
快速路径加速比: 2481.5x
```

#### 2. 快速模板测试用例

##### 股价查询（快速路径）
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
  }'
# 预期：0.02秒内返回结果
```

##### 估值指标查询（快速路径）
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "中国平安的市盈率",
    "query_type": "sql"
  }'
# 预期：返回PE、PE_TTM、PB等指标
```

##### 涨跌幅排名（快速路径）
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今天涨幅最大的前10只股票",
    "query_type": "sql"
  }'
# 预期：快速返回排名表格，不触发股票验证
```

##### 市值排名（快速路径）
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "总市值最大的前20只股票",
    "query_type": "sql"
  }'
# 预期：返回格式化的市值排名表
```

##### 历史K线查询（快速路径）
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最近90天的K线走势",
    "query_type": "sql"
  }'
# 预期：返回表格化的K线数据
```

#### 3. 性能对比测试
```bash
# 对比相同查询的不同路径
# 1. 强制使用快速路径（通过精确匹配模板）
# 2. 强制使用LLM路径（通过修改查询描述）

# 测试脚本中已包含详细的性能统计
```

#### 4. 验证优化效果
- 排名查询不再触发股票验证
- 特定股票查询仍然保留验证
- 查询类型智能判断

### 九、路由机制测试 (v2.1.2新增)

#### 1. 测试路由修复
```bash
# 测试模板路由覆盖修复
source venv/bin/activate && python test_routing_fix.py
```

预期输出：
```
查询: 今天涨幅最大的前10只股票
  匹配模板: 涨幅排名
  原始路由: SQL_ONLY
  覆盖路由: 无
  最终路由: SQL_ONLY

查询: 排行分析：今日涨幅前10
  未匹配到模板
```

#### 2. 测试完整路由功能
```bash
# 运行增强路由测试
source venv/bin/activate && python test_enhanced_routing.py
```

### 十、文档处理功能测试

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

### 十一、数据维护功能测试

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

### 十二、性能测试

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
| SQL查询 | 实时股价（快速） | ✅ | 0.02s | v2.1.2新增 |
| SQL查询 | 实时股价（LLM） | ✅ | 5s | - |
| SQL查询 | 涨跌排行（快速） | ✅ | 0.02s | v2.1.2新增 |
| SQL查询 | 涨跌排行（LLM） | ✅ | 8s | - |
| SQL查询 | PE/PB查询（快速） | ✅ | 0.02s | v2.1.2新增 |
| SQL查询 | K线数据（快速） | ✅ | 0.02s | v2.1.2新增 |
| RAG查询 | 财务查询 | ✅ | 3s | - |
| RAG查询 | 多公司对比 | ✅ | 5s | - |
| 混合查询 | 综合分析 | ✅ | 15s | - |
| API服务 | 健康检查 | ✅ | <1s | - |
| 文档处理 | PDF下载 | ✅ | 2-10s | - |

### 性能指标
- SQL查询平均响应（快速路径）：0.02秒
- SQL查询平均响应（LLM路径）：51.13秒
- 快速路径加速比：2481.5x
- RAG查询平均响应：3-5秒
- 并发支持：50+用户
- 系统稳定性：99.9%

## 7-Agent架构测试方案 (v2.2.0规划)

### 新增Agent测试用例

#### 1. Rank Agent测试（待实现）
```bash
# 触发词测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "排行分析：今日涨幅前10的股票",
    "query_type": "hybrid"
  }'

# 排除ST股票测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "排行分析：市值前20（排除ST）",
    "query_type": "hybrid"
  }'

# 板块排名测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "排行分析：银行板块市值排名",
    "query_type": "hybrid"
  }'
```

#### 2. ANNS Agent测试（待实现）
```bash
# 触发词测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询公告：贵州茅台最新年报",
    "query_type": "hybrid"
  }'

# 时间范围测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询公告：平安银行最近30天的公告",
    "query_type": "hybrid"
  }'

# 公告类型测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询公告：600519.SH业绩快报",
    "query_type": "hybrid"
  }'
```

#### 3. QA Agent测试（待实现）
```bash
# 触发词测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "董秘互动：贵州茅台产能扩张计划",
    "query_type": "hybrid"
  }'

# 关键词组合测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "董秘互动：平安银行AND不良贷款",
    "query_type": "hybrid"
  }'

# 逻辑排除测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "董秘互动：招商银行投资NOT房地产",
    "query_type": "hybrid"
  }'
```

### 路由机制测试 (v2.1.2更新)

#### 1. 路由优先级测试
```bash
# 测试触发词路由（最高优先级）
source venv/bin/activate && python test_enhanced_routing.py

# 查看路由机制文档
cat docs/ROUTING_MECHANISM.md
```

#### 2. 模板匹配测试
```bash
# 运行模板匹配单元测试
python utils/query_templates.py

# 预期输出：
# 查询模板匹配测试
# ==============================================================
# 查询: 茅台最新股价
#   匹配模板: 最新股价查询
#   路由类型: SQL_ONLY
#   提取参数: {'entities': ['茅台'], 'time_range': 'latest', 'metrics': ['close', 'change', 'pct_chg']}
```

### 路由准确性测试矩阵 (v2.1.2更新)

| 查询内容 | 预期路由 | 触发方式 |
| "排行分析：涨幅榜" | Rank Agent | 触发词 |
| "查询公告：年报" | ANNS Agent | 触发词 |
| "董秘互动：分红" | QA Agent | 触发词 |
| "贵州茅台最新股价" | SQL Agent | 模板匹配 |
| "分析茅台财务健康度" | Financial Agent | 关键词 |
| "茅台资金流向分析" | Money Flow Agent | 关键词 |
| "贵州茅台年报分析" | RAG Agent | 文档需求 |

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

#### 深色主题UI测试 (v1.5.3+新增)
- [ ] 深色主题下复制按钮背景色正确(#1e1e1e)
- [ ] 复制按钮悬停效果明显(#2a2a2a)
- [ ] 复制按钮图标颜色清晰可见(#e0e0e0)
- [ ] 代码块与复制按钮视觉区分明显
- [ ] 深色主题下的滚动条样式统一
- [ ] 文档查看器边框颜色与主题协调

### 8.3 错误处理测试
- [ ] API未启动时显示友好错误提示
- [ ] 网络超时处理
- [ ] 空查询阻止发送
- [ ] 加载状态正确显示

### 8.4 响应式测试
- [ ] 1920x1080分辨率正常
- [ ] 1366x768分辨率正常
- [ ] 移动端布局（可选）

### 8.5 分屏功能完整测试 (重点)

#### 分屏触发测试
- [ ] 点击"查看数据"按钮正确打开数据面板
- [ ] 点击"查看文档"按钮正确打开文档面板
- [ ] 点击"查看详情"按钮正确打开财务详情
- [ ] 连续点击不同按钮切换内容正常

#### 分屏内容测试
- [ ] 表格数据显示格式正确
- [ ] 文档内容Markdown渲染正常
- [ ] 代码块语法高亮正常
- [ ] 滚动条独立工作

#### 分屏交互测试
- [ ] 复制按钮功能正常
- [ ] 关闭按钮(×)响应正确
- [ ] 左右面板宽度比例合理
- [ ] 分屏状态下继续对话功能正常

#### 主题切换测试
- [ ] 亮色主题下分屏显示正常
- [ ] 深色主题下分屏显示正常
- [ ] 主题切换时分屏内容保持不变
- [ ] 复制按钮在两种主题下都清晰可见

### 8.6 流式响应功能测试 (v1.5.4新增)

#### 流式显示效果测试
- [ ] 消息逐字符显示，模拟打字效果
- [ ] 默认每次显示3个字符，间隔30ms
- [ ] 打字光标在流式响应时闪烁显示
- [ ] 流式响应完成后光标自动消失

#### 停止查询功能测试
- [ ] 流式响应时发送按钮变为红色停止按钮
- [ ] 点击停止按钮能够中断查询
- [ ] 停止后按钮恢复为发送按钮
- [ ] 停止后可以立即发送新查询

#### 性能和稳定性测试
- [ ] 长文本响应流式显示流畅
- [ ] 快速切换查询不会造成显示混乱
- [ ] 组件卸载时正确清理定时器
- [ ] 内存使用稳定，无泄漏

#### 边界情况测试
- [ ] 空响应处理正常
- [ ] 超长响应（>10000字符）显示正常
- [ ] 特殊字符（emoji、数学符号等）显示正常
- [ ] 网络中断时的错误处理