# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Stock Analysis System (v1.5.2)** built with Python that provides intelligent stock analysis through SQL queries, RAG (Retrieval-Augmented Generation), and hybrid query capabilities. The system integrates modern LangChain, FastAPI, MySQL, and Milvus to deliver comprehensive financial data analysis and document retrieval.

**Current Status**: ✅ React前端初版实现完成，Claude.ai风格界面上线。财务分析系统错误处理完善，前端错误显示修复。RAG系统深度优化完成，WebSocket实时通信已恢复，股票代码智能映射上线。系统全面修复完成，Phase 2核心功能已验证正常。Windows兼容性100%，RAG查询功能完全恢复，智能日期解析精准识别最新交易日，资金流向分析100%正常运行。Phase 1 深度财务分析系统开发完成, Phase 2 资金流向分析系统开发完成, 智能日期解析v2.0系统开发完成。

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (Updated: venv/ directory)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System

#### 后端API服务器（必须在Windows环境）
```bash
# Windows Anaconda Prompt:
conda activate stock-frontend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 注意：由于WSL2的I/O性能限制，API服务器必须在Windows原生环境运行
```

#### 前端开发服务器（双环境支持）
```bash
# 方案：开发在WSL2，测试在Windows
# 1. 检查/切换环境：
#    WSL2: ./switch-env.sh
#    Windows: switch-env.bat

# 2. 在对应环境安装依赖并运行：
#    cd frontend
#    npm install  # 每个环境需要单独安装
#    npm run dev

# 重要：前端可以在WSL2开发以提高效率，但最终测试必须在Windows环境
```

#### 其他工具
```bash
# Start interactive RAG interface
python rag_query_interface.py

# Run system health check
python scripts/utils/system_check.py
```

### Testing

**重要**: WSL2环境中所有Python命令都需要激活虚拟环境！

#### WSL2环境测试命令格式
```bash
# 标准格式：激活虚拟环境 + Python命令
source venv/bin/activate && python [script_name]

# 或使用便捷脚本
./run_with_venv.sh python [script_name]
```

#### 具体测试命令
```bash
# Test database connections
source venv/bin/activate && python scripts/tests/test_databases.py

# Test API endpoints  
source venv/bin/activate && python scripts/tests/test_api.py

# Test specific components
source venv/bin/activate && python scripts/tests/test_components.py

# Essential comprehensive tests (keep in root directory)
source venv/bin/activate && python baseline_test.py
source venv/bin/activate && python comprehensive_verification.py

# Test financial analysis features (v1.4.0 new)
source venv/bin/activate && python test_financial_agent.py
source venv/bin/activate && python test_advanced_financial_features.py

# Test intelligent date parsing features (v1.4.1+)
source venv/bin/activate && python test_date_intelligence.py
source venv/bin/activate && python test_date_intelligence_integration.py
source venv/bin/activate && python test_date_intelligence_v2.py  # v2.0 enhanced system

# Test money flow analysis features (v1.4.2 new)
source venv/bin/activate && python test_money_flow_simple.py

# Test stock code mapper (v1.4.3 new)
source venv/bin/activate && python utils/stock_code_mapper.py

# Bug fix verification tests (v1.4.1 fixes)
source venv/bin/activate && python test_bug_fixes.py
source venv/bin/activate && python test_money_flow_analysis.py
source venv/bin/activate && python test_latest_trading_day_fix.py
source venv/bin/activate && python test_comprehensive_final.py

# Archived test scripts (in scripts/tests/)
source venv/bin/activate && python scripts/tests/test_optimized_rag.py
source venv/bin/activate && python scripts/tests/test_final_rag.py
source venv/bin/activate && python scripts/tests/test_rag_enhancements.py
source venv/bin/activate && python scripts/tests/test_simple_stats.py

# Performance testing (use longer timeout)
source venv/bin/activate && python scripts/tests/performance_test.py

# Web Frontend Testing (NEW v1.4.2)
# Follow the comprehensive web testing guide:
# docs/testing/WEB_FUNCTIONAL_TEST_GUIDE.md
# Test all core functions through web interface at http://localhost:8000
```

#### 快捷脚本使用方式
```bash
# 使用便捷脚本（推荐）
./run_with_venv.sh python baseline_test.py
./run_with_venv.sh python test_financial_agent.py
```

### Data Processing
```bash
# Load Milvus collection
python scripts/tools/load_milvus_collection.py

# Process documents with smart processor
python smart_processor_v5_1.py

# Batch processing management
python batch_process_manager.py

# Check for duplicates
python scripts/maintenance/milvus_final_dedup.py
```

### Debugging and Maintenance
```bash
# Debug specific issues
python scripts/debugging/check_api_enums.py
python scripts/debugging/diagnose_agent_issue.py

# System analysis
python scripts/analysis/db_analyzer.py
python scripts/analysis/announcement_analyzer.py

# Check PDF downloads
python scripts/debugging/test_cninfo_pdf.py
```

## Architecture Overview

### Core Components

**API Layer** (`api/main.py`):
- FastAPI-based REST API with WebSocket support
- Handles query routing and response formatting
- Provides health checks and system status endpoints

**Agent System** (`agents/`) - *All modernized with LangChain RunnableSequence*:
- `HybridAgent`: Smart query router with modern chain composition using `|` operator
- `SQLAgent`: Handles structured data queries with enhanced input validation
- `RAGAgent`: Document retrieval with semantic search, query statistics, and modern chains
- `FinancialAnalysisAgent`: **[v1.4.0]** 专业财务分析系统，支持四表联合查询和深度财务分析
- `MoneyFlowAgent`: **[v1.4.2]** 资金流向分析系统，支持四级资金分布和主力行为分析

**Database Layer** (`database/`):
- `MySQLConnector`: Manages connections to MySQL for structured financial data
- `MilvusConnector`: Handles vector database operations for document embeddings

**Document Processing** (`rag/document_processor.py`):
- PDF download with three-stage retry strategy for cninfo.com.cn
- Text extraction and chunking with BGE-M3 embeddings
- Intelligent content filtering and metadata extraction

**Stock Code Mapping** (`utils/stock_code_mapper.py`) - *[v1.4.3 NEW]*:
- Dynamic mapping from company names/symbols to ts_code format
- Cache-based architecture with 60-minute TTL
- Thread-safe singleton pattern for global access
- Supports 21,000+ stock mappings from tu_stock_basic table

### Data Flow

1. **Query Processing**: User queries are received by the API layer
2. **Smart Routing**: HybridAgent analyzes the query and routes to appropriate agent(s)
3. **Data Retrieval**: 
   - SQL queries hit MySQL for structured data (stock prices, financial metrics)
   - RAG queries perform semantic search in Milvus for document content
4. **Response Integration**: Results are combined and formatted by LLM for final response

### Key Data Sources

- **MySQL Database**: Contains 28M+ records of stock data from Tushare
- **Milvus Vector Database**: Stores 95,662+ document embeddings from company announcements
- **PDF Documents**: 5000+ financial reports and announcements

## Configuration

**Environment Variables** (`.env`):
```bash
# Database connections
MYSQL_HOST=10.0.0.77
MYSQL_PORT=3306
MYSQL_DATABASE=Tushare
MYSQL_USER=readonly_user
MYSQL_PASSWORD=

MILVUS_HOST=10.0.0.77
MILVUS_PORT=19530
MILVUS_USER=root
MILVUS_PASSWORD=Milvus

# LLM API keys
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

**Settings** (`config/settings.py`):
- Database connection pools and timeouts
- Text processing parameters (chunk size: 1000, overlap: 200)
- Embedding model: BGE-M3 (1024 dimensions)
- Performance monitoring and caching configurations

## Important Development Notes

### Query Types
The system supports six main query types:
- `sql`: For numerical data, rankings, and structured queries
- `rag`: For document content, explanations, and qualitative analysis  
- `financial_analysis`: For professional financial analysis and scoring (Phase 1 ✅)
- `money_flow`: For capital flow analysis and institutional behavior (Phase 2 ✅)
- `technical_analysis`: For technical indicators and trend analysis (Phase 2 planned)
- `hybrid`: Automatically routes or combines multiple approaches

### Error Handling
- All agents return standardized response format with `success`, `error`, and result fields
- Input validation prevents empty/whitespace queries from causing errors  
- Modern LangChain error handling with try-catch around `invoke()` calls
- Milvus collections are automatically loaded if needed
- PDF downloads use three-stage retry with session management

### Performance Considerations
- SQL queries: 5-30 seconds depending on complexity
- RAG queries: 3-15 seconds with vector optimization
- Financial analysis: 20-45 seconds with comprehensive calculations
- Money flow analysis: 15-30 seconds with multi-tier calculations
- Hybrid queries: 10-60 seconds with parallel processing
- System supports 50+ concurrent users
- WebSocket real-time communication supported

### Recent Updates

#### v1.5.2 - 前端样式优化与分屏体验改进 (2025-06-26)

**Claude.ai风格优化** ✅:
- **消息显示改进**: AI回复采用无边框直接显示，用户消息简化样式
- **布局宽度优化**: 分屏时充分利用空间，减少两侧留白
- **侧边栏折叠功能**: 支持手动和自动折叠，节省显示空间
- **分屏体验提升**: 打开文档时自动折叠侧边栏，优化空间利用

**技术改进** ✅:
- 超时时间增加到10分钟（600秒）
- Message组件重构，更接近Claude.ai体验
- 响应式布局优化，分屏/非分屏自适应
- 添加平滑过渡动画效果

**用户体验提升** ✅:
- 对话内容显示更清晰，减少视觉干扰
- 分屏模式下阅读体验显著改善
- 侧边栏智能折叠，最大化内容显示区域
- 支持查看数据、文档、财务详情等多种源数据

#### v1.5.0 - React前端初版实现 (2025-06-26)

**React前端开发完成** ✅:
- **Claude.ai风格界面**: 260px侧边栏、主聊天区、底部输入框
- **完整Markdown渲染**: 支持代码高亮、表格美化、数学公式、引用块
- **API集成完成**: 与后端/query接口对接，支持所有查询类型
- **双环境架构确立**: Windows运行前端和API服务，WSL2用于Claude Code开发

**技术栈实现** ✅:
- React + TypeScript + Vite构建系统
- Tailwind CSS实现Claude.ai配色方案
- react-markdown + remark/rehype插件链
- react-syntax-highlighter代码高亮

**已修复问题** ✅:
- react-markdown v9 className属性兼容性问题
- PostCSS配置与Tailwind CSS版本匹配
- Node.js版本兼容性（v18与Vite 5.2.0）

**前端运行指南** ✅:
```bash
# Windows环境运行前端
cd E:\PycharmProjects\stock_analysis_system\frontend
npm run dev

# Windows环境运行API
cd E:\PycharmProjects\stock_analysis_system
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### v1.4.3+ - 财务分析用户体验优化 (2025-06-25 晚)

**财务分析报告优化** ✅:
- **股票信息标注**: 所有财务分析报告开头明确显示股票名称和代码
- **StockCodeMapper增强**: 新增反向映射缓存（ts_code→name）
- **性能优化**: 利用现有缓存机制，避免重复数据库查询
- **错误处理完善**: 前端WebSocket消息智能检测错误响应

**技术实现** ✅:
- 扩展`utils/stock_code_mapper.py`添加`get_stock_name()`方法
- 更新`agents/financial_agent.py`的分析链提示词模板
- 修复前端`templates/index.html`的错误消息显示逻辑
- 所有4个财务分析方法统一添加股票信息参数

#### v1.4.3 - RAG系统优化与股票代码映射器实现 (2025-06-25)

**RAG查询系统修复** ✅:
- **QueryType枚举修复**: 解决SQL_FIRST/RAG_FIRST等路由混乱问题
- **RAG容错机制**: 过滤条件无结果时自动降级到无过滤搜索
- **路由调试增强**: 添加详细的路由决策日志追踪

**股票代码映射器（新增）** ✅:
- **缓存+数据库架构**: 基于tu_stock_basic表的动态查询
- **统一映射标准**: 股票名称/代码→ts_code格式
- **高性能设计**: 60分钟TTL缓存 + LRU二级缓存
- **智能处理**: 自动去除公司后缀，支持常见简称
- **线程安全**: 单例模式确保全局唯一实例

#### v1.4.2-final - 系统全面修复 + Phase 2功能验证完成 (2025-06-24)

**系统修复完成状态** ✅:
- **Windows兼容性修复**: 解决signal.SIGALRM问题，BGE-M3模型采用threading方案
- **RAG查询完全恢复**: 修复智能日期解析过度干预，RAG成功率100%
- **SQL/Financial Agent优化**: 修复输出解析错误和NoneType安全检查
- **数据驱动交易日判断**: 精准识别2025-06-24为最新交易日

**Phase 2功能验证结果** ✅:
- **资金流向分析系统**: 100%正常运行，茅台资金流向104秒专业报告
- **智能日期解析v2.0**: 时间点vs时间段精准识别，缓存优化
- **完整测试覆盖**: TEST_MANUAL_v1.4.1.md (403行) 保留完整
- **网页界面状态**: ⚠️ 基础版本保留，WebSocket功能需恢复

#### v1.4.0 - Phase 1 深度财务分析系统 (2025-06-22)

**FinancialAnalysisAgent 核心功能** ✅:
- **四表联合分析**: 利润表(83字段) + 资产负债表(161字段) + 现金流量表(73字段) + 财务指标(143字段)
- **财务健康度评分**: 基于盈利能力、偿债能力、运营能力、成长能力四维度的智能评分系统(AAA-CCC评级)
- **杜邦分析功能**: ROE分解分析(净利率×资产周转率×权益乘数)，支持多期趋势分析
- **现金流质量分析**: 现金含量比率计算、稳定性评分、综合质量评级
- **多期财务对比**: 同比/环比增长率、趋势分析、波动性评估
  - 同比增长分析(YoY): 对比去年同期，需至少5期数据
  - 环比增长分析(QoQ): 对比上一期，需至少2期数据
  - 趋势判断: 上升/下降/平稳/波动趋势识别
  - 稳定性评级: 基于标准差的波动性分析（非常稳定/比较稳定/一般稳定/波动较大）
  - 详细文档: `docs/financial_comparison_analysis.md`

**智能查询能力** ✅:
- **自然语言解析**: 支持"分析茅台的财务健康度"、"杜邦分析"、"现金流质量"等中文查询
- **股票代码识别**: 自动提取TS代码(如600519.SH)或根据公司名称(如"贵州茅台")查找
- **查询意图路由**: 智能识别财务分析意图并调用相应分析功能

**专业分析报告** ✅:
- **LLM增强分析**: 结合财务计算结果和AI分析生成专业财务报告
- **多维度洞察**: 核心结论、详细分析、风险提示、投资建议
- **数据可视化**: 格式化的财务指标展示和趋势分析

**测试验证** ✅:
- 贵州茅台财务健康度: AA级(81分)，盈利能力强，偿债能力优秀
- 平安银行杜邦分析: 净利率41.82%，但资产周转率低(0.006次)，高杠杆(11.42倍)
- 现金流质量分析: 准确识别茅台现金流波动问题，万科现金流质量评级
- 查询响应时间: 25-30秒，包含完整的LLM分析报告生成

#### v1.4.1 - 智能日期解析系统 (2025-06-23)

**智能日期解析核心功能** ✅:
- **自然语言时间识别**: 自动识别"最新"、"最近"、"现在"等时间表达
- **数据类型智能分类**: 区分股价数据、财务数据、公告数据的时间需求
- **最近交易日查询**: 智能获取最近可用的交易日（避免非交易日查询错误）
- **最新报告期识别**: 自动查找最新的年报、季报、半年报期间
- **最新公告日期**: 动态获取特定股票的最新公告发布日期

**系统集成** ✅:
- **SQL Agent集成**: 预处理"茅台最新股价"→"茅台2025-06-23股价" (已修复)
- **RAG Agent集成**: 预处理"贵州茅台最新公告"→"贵州茅台2025-06-23公告" (已修复)
- **Hybrid Agent支持**: 复合查询中的智能时间解析
- **缓存机制**: 1小时TTL缓存，避免重复数据库查询

**解析示例** ✅ (更新为v2.0):
- "茅台最新股价" → 查询2025-06-23交易日数据 (修复日期缓存BUG)
- "5天前的股价" → 查询2025-06-17数据 (时间点)
- "前5天的走势" → 查询2025-06-17至2025-06-23走势 (时间段)
- "上个月的数据" → 查询2025-05-23数据 (21个交易日前)
- "去年同期股价" → 查询2024-06-21股价 (智能修正非交易日)

**技术实现** ✅:
- 新增 `utils/date_intelligence.py` 智能日期解析模块
- 正则表达式模式匹配 + 股票代码识别
- SQLAlchemy参数化查询，防止SQL注入
- 统一错误处理和日志记录

#### v1.4.2 - Phase 2 资金流向分析和网页前端 + 日期解析v2.0 (2025-06-23)

**资金流向分析系统** ✅:
- **主力资金分析**: 最高优先级，分析主力资金(大单+超大单)净流入/流出
- **超大单行为模式**: 重点单独分析，识别机构建仓/减仓/洗盘行为
- **四级资金分布**: 超大单(≥100万)、大单(20-100万)、中单(4-20万)、小单(<4万)
- **专业评估系统**: 资金流向强度、一致性评分、投资建议

**网页版前端界面** ✅:
- **ChatGPT风格交互**: 类似对话式的自然语言交互界面
- **WebSocket实时通信**: 支持即时对话，无需刷新页面
- **音体化设计**: 适配手机和电脑端，支持快捷按钮
- **实时加载提示**: 查询处理状态实时反馈

**智能日期解析v2.0** ✅:
- **时间点vs时间段区分**: 精确区分"5天前"(时间点)和"前5天"(时间段)
- **专业交易日计算**: 周5天、月21天、季61天、半年120天、年250天
- **年份相对日期修正**: 去年同期非交易日智能向前查找最近交易日
- **完整中文支持**: 支持最新、上周、上个月、去年、最近N天等所有常用表达

**系统集成** ✅:
- **MoneyFlowAgent**: 新增资金流向分析专用Agent
- **Hybrid Agent路由**: 支持MONEY_FLOW查询类型智能路由
- **API端点完善**: POST /money-flow-analysis接口和完整文档
- **前端整合**: templates/index.html实现网页交互

**测试验证** ✅:
- 贵州茅台资金流向: 主力资金净流入+1.25亿元，超大单呈现建仓特征
- 网页前端: 成功实现自然语言交互，支持所有模块查询
- 日期解析v2.0: 修复日期缓存BUG，现正确返回2025-06-23最新数据
- API文档: 完整更新所有端点文档，新增标签分组和使用示例

**技术实现** ✅:
- 新增 `utils/money_flow_analyzer.py` 资金流向分析核心模块
- 新增 `agents/money_flow_agent.py` 资金流向分析Agent
- 新增 `templates/index.html` 网页前端界面
- 重写 `utils/date_intelligence.py` v2.0架构，新增设计文档
- 完善 API文档和标签分组，新增多个使用示例

#### v1.3.8 - LangChain现代化 (2025-06-22)

**LangChain Modernization Complete** ✅:
- Updated all `LLMChain` to modern `RunnableSequence` pattern
- Replaced deprecated `Chain.run()` with `invoke()` method
- Implemented pipeline composition with `|` operator: `prompt | llm | parser`
- Resolved all LangChain deprecation warnings
- Fixed `StdOutCallbackHandler` errors completely

**Enhanced Input Validation** ✅:
- Added empty query validation to all agents (RAG, SQL, Hybrid)
- Standardized error response formats across all components
- Prevents crashes from empty or whitespace-only inputs

**RAG Agent Improvements** ✅:
- Added query statistics tracking (`query_count`, `success_count`)
- Implemented `get_stats()` method for performance monitoring
- Enhanced error handling and logging

**Testing & Quality Assurance** ✅:
- All 6/6 comprehensive tests passing
- Test script organization: essential tests in root, archived tests in `scripts/tests/`
- Baseline functionality verification with `baseline_test.py`
- Performance and integration testing completed

### Core Documentation

When updating project documentation, always update all three core documents:
1. **CLAUDE.md** (this file) - Development guidance and technical overview
2. **test-guide.md** - Comprehensive testing procedures and test cases
3. **docs/project_status/CURRENT_STATUS.md** - Project status, version history, and known issues

### Testing Strategy

**Script Testing (Backend API)**:
- Use the test-guide.md for comprehensive testing procedures
- Essential comprehensive tests: `baseline_test.py`, `comprehensive_verification.py`
- Feature-specific tests: Financial Analysis, Money Flow, Date Intelligence
- Performance benchmarks in scripts/tests/

**Web Frontend Testing (User Experience)**:
- **网页版功能测试指南**: `docs/testing/WEB_FUNCTIONAL_TEST_GUIDE.md` ⭐ **[NEW v1.4.2]**
- 全面覆盖所有核心功能的网页版测试用例
- 包含功能性测试、破坏性测试、性能测试、用户体验测试
- 脚本测试vs网页版测试双重验证体系
- 持续集成测试清单和回归测试基准

**Testing Infrastructure**:
- API endpoints available at http://localhost:8000/docs
- Interactive testing via rag_query_interface.py
- Web interface testing at http://localhost:8000
- Automated test execution via dedicated scripts

### Log Files
- API logs: `logs/api.log`
- Database logs: `logs/mysql_connector.log`, `logs/milvus_connector.log`
- Agent logs: `logs/hybrid_agent.log`, `logs/rag_agent.log`, `logs/sql_agent.log`
- Document processing: `logs/document_processor.log`

### Data Directories
- PDF storage: `data/pdfs/`
- Performance logs: `data/performance_logs/`
- Cache files: `data/pdfs/cache/`

## Development Best Practices

### Code Quality
- All LangChain code uses modern patterns (v0.1+ compatible)
- Input validation is mandatory for all public methods
- Error handling follows standardized response format
- Test coverage includes unit, integration, and performance tests

### Query Development
```python
# Example: Modern LangChain pattern in agents
qa_chain = qa_prompt | self.llm | StrOutputParser()
result = qa_chain.invoke({"context": context, "question": question})

# Example: Using stock code mapper (v1.4.3)
from utils.stock_code_mapper import convert_to_ts_code

# Convert various formats to ts_code
ts_code = convert_to_ts_code("茅台")           # Returns: "600519.SH"
ts_code = convert_to_ts_code("600519")         # Returns: "600519.SH"
ts_code = convert_to_ts_code("贵州茅台")        # Returns: "600519.SH"
ts_code = convert_to_ts_code("诺德股份")        # Returns: "600110.SH"
```

### Testing Protocol

**Backend API Testing**:
1. Run `baseline_test.py` for quick functionality check
2. Run `comprehensive_verification.py` for full system validation
3. Check specific features with archived tests in `scripts/tests/`
4. Performance testing via dedicated scripts

**Web Frontend Testing** ⭐ **[NEW v1.4.2]**:
1. **Quick Verification** (15 minutes): Follow 回归测试清单 in WEB_FUNCTIONAL_TEST_GUIDE.md
2. **Complete Testing** (60 minutes): Execute all test cases in the web guide
3. **Cross-Platform Testing**: Test on different browsers and devices  
4. **Performance Validation**: Verify response times meet web interface standards

**Release Testing Protocol**:
- Script tests must pass 100% before web testing
- Web testing validates complete user experience  
- Both testing layers required for production releases

## Next Development Priority (v3.1 - Claude.ai风格React前端改版)

### 环境架构设计 (NEW)
```
开发环境架构：
┌─────────────────────────────────────────────────┐
│                 Windows 系统                     │
│  ┌─────────────────────┬──────────────────────┐ │
│  │   Anaconda环境       │    开发工具           │ │
│  │  - Node.js 18+      │  - PyCharm           │ │
│  │  - npm/yarn         │  - VS Code           │ │
│  │  - React开发服务器   │  - Git               │ │
│  └─────────────────────┴──────────────────────┘ │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │              WSL2 (Ubuntu)               │   │
│  │  ┌──────────────┬───────────────────┐   │   │
│  │  │  venv环境    │   Node.js环境      │   │   │
│  │  │ - Python 3.10│  - nvm管理         │   │   │
│  │  │ - FastAPI    │  - Node.js 18+     │   │   │
│  │  │ - LangChain  │  - npm包管理       │   │   │
│  │  └──────────────┴───────────────────┘   │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Phase 0: 环境准备与备份（第1-2天）NEW
- **环境备份**: 
  - WSL2: `pip freeze > requirements_backup_$(date +%Y%m%d).txt`
  - Anaconda: `conda env export > environment_backup_$(date +%Y%m%d).yml`
- **前端开发环境搭建**:
  - Windows Anaconda创建node环境，安装Node.js 18+
  - WSL2安装nvm和Node.js，保持版本一致
- **环境同步脚本**: 编写自动化脚本确保两边环境一致

### Phase 1: Claude.ai风格React MVP（第3-7天）
- **基础架构**: 
  - React + TypeScript + Vite项目初始化
  - 安装react-markdown、remark-gfm、react-syntax-highlighter等依赖
- **核心组件开发**:
  - Claude.ai风格布局：260px侧边栏、主内容区、#10a37f主色调
  - MarkdownRenderer：完整实现代码高亮、表格美化、数学公式等
  - 左右分屏逻辑：智能判断内容类型，自动显示文档区
  - 核心组件：Sidebar、ChatArea、MessageList、InputBox、DocumentViewer
- **API集成**:
  - 与后端/query接口对接，处理sources数据分发
  - 支持WebSocket流式响应

### Phase 2: 功能增强与优化（第8-14天）
- **高级功能**:
  - 消息流式响应：逐字显示和打字光标效果
  - 股票数据可视化：K线图、成交量图、资金流向图
  - 增强表格组件：排序筛选、数值格式化、涨跌颜色
- **用户体验**:
  - 亮色/深色主题切换
  - 快捷键支持（Ctrl+N新建对话等）
  - 响应式设计适配移动端

### Phase 3: 后端优化与技术分析（第15-21天）
- **数据库Schema中文映射系统**
- **RAG查询智能降级机制**
- **技术面分析系统实现**

### Git版本管理
```bash
# 当前分支: dev-react-frontend-v2
# 环境备份完成后开始开发
git add -A && git commit -m "chore: 环境备份和开发准备"
```

### 部署文档要求
- 详细记录WSL2+Windows双环境配置步骤
- 创建.env.development和.env.production
- 编写setup脚本自动化环境配置

The system is designed for production use with comprehensive error handling, logging, monitoring capabilities, and full LangChain modernization (v1.3.8).