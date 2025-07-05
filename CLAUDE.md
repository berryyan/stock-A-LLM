# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 重要目录说明 (Important Directory Structure)

- **主前端目录**: `/frontend` - React + TypeScript + Claude.ai风格界面
- **后端API目录**: `/api` - FastAPI后端服务
- **Agent系统**: `/agents` - 各种查询处理Agent
- **配置文件**: 根目录 - .env, requirements.txt等
- **文档目录**: `/docs` - 项目文档和状态记录

⚠️ **注意**: 请勿混淆 `frontend` 与其他可能存在的前端目录

## Project Overview

This is a **Stock Analysis System (v2.1.18)** built with Python that provides intelligent stock analysis through SQL queries, RAG (Retrieval-Augmented Generation), and hybrid query capabilities. The system integrates modern LangChain, FastAPI, MySQL, and Milvus to deliver comprehensive financial data analysis and document retrieval.

**Current Status**: ✅ 参数提取器增强完成，支持特殊股票名称100%准确率提取。修复ST股票提取正则表达式，使用负向预查避免过度匹配。股票验证错误消息传递机制修复，月份/年份范围模式匹配完整实现。日期智能解析增强，支持"最后的"、"N年前"等相对日期表达。限制提取逻辑优化，在提取前排除已识别的股票名称。特殊股票名称支持完善：ST/*ST/S/XD前缀、-U/-W/-UW后缀、英文+中文组合（GQY视讯）、中文数字名称（三六零）、A/B后缀股票（万科A）全部支持。多股票提取改进，extract_multiple_stocks方法增强，支持各种连接词（和/与/及/、/，/vs/VS）。边界条件处理优化，支持数字作为边界。测试覆盖率100%：原始15个测试全部通过，特殊股票名称测试全部通过，扩展参数提取器测试全部通过。复杂查询支持完善，如"GQY视讯、七一二和大北农的对比"、"TCL科技和TCL智家财务对比"等。股票验证公用模块化完成，创建stock_validation_helper统一验证模块，SQL Agent全面使用公用验证方法，大小写错误验证完全修复，错误信息准确性从6.2%提升至81.2%。股票验证逻辑统一化，验证失败立即返回错误，不尝试"修复"。缓存键生成问题识别，_extract_query_params方法修复，convert_to_ts_code直接调用全部替换为验证方法。测试通过率大幅提升：股价查询/估值查询/成交量查询100%通过，K线查询验证逻辑增强，个股主力资金/利润查询验证完善。公用方法原则全面贯彻，所有Agent共享相同的验证逻辑。SQL Agent边界测试问题修复完成，股票代码无后缀识别支持，日期模式识别增强，日期替换空格智能添加。股票提取方法统一化，UnifiedStockValidator集成，所有模板股票识别能力一致性提升。SQL Agent提取功能增强完成，日期范围连接符扩展，月份/年份转日期范围实现，股票名称智能清理修复。综合测试27/27全部通过。前端主题系统完整实现，支持亮色/暗色主题切换，主题偏好本地存储。公告日期范围查询功能完善，SQL Agent公告查询功能实现。多个后端崩溃问题修复，利润查询模板增强，净利润排名字段映射修复，RAG查询参数类型修复。前端Markdown表格暗色模式优化，个股/板块主力资金查询格式优化，营收排名模板正则增强。财务指标排名快速路径实现，PE/PB/ROE等5个新模板已上线，响应时间1-2秒。资金类型术语标准化，支持16种非标准术语映射。市值排名查询优化，支持无数字默认前10。日期智能解析DISTINCT问题修复，股票识别修复，路由机制修复。SQL Agent快速模板完成，路由机制文档化，7-Agent架构Phase 0&1完成。代码清理完成，SchemaKnowledgeBase确认为实际使用系统。流式响应功能完整实现，React前端Phase 1完成。RAG系统优化完成，WebSocket通信恢复，股票代码映射上线。系统全面修复完成，Windows兼容性100%，Phase 1深度财务分析系统完成，Phase 2资金流向分析系统完成，智能日期解析v2.0系统完成。

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

# ⚠️ WSL2开发限制（Claude必须遵守）：
# - 仅用于：文件操作、Git管理、简单连通性测试
# - 禁止在WSL2：执行超过30秒的查询测试、性能测试、完整功能验证
# - 所有长时间运行的测试必须在Windows环境手动执行
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

# Test financial ranking features (v2.1.11 new)
source venv/bin/activate && python test_ranking_comprehensive.py
source venv/bin/activate && python test_ranking_simple.py

# Test parameter extractor features (v2.1.18 new)
source venv/bin/activate && python tests/test_parameter_extractor_extended.py
source venv/bin/activate && python tests/test_special_stock_names.py

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

### Important Query Guidelines
**Stock Entity Recognition** (Enhanced in v1.5.5):
- The system does NOT support fuzzy/partial matching for stock names or codes
- Users MUST provide exact stock names (e.g., "贵州茅台" not "茅台") 
- Supported formats: Full company name, 6-digit code (600519), or ts_code (600519.SH)
- NEW: Smart case-sensitive error detection (e.g., "600519.sh" → "应为.SH")
- NEW: Common abbreviation guidance (e.g., "茅台" → "请使用完整公司名称，如：贵州茅台")
- Invalid inputs will result in precise error messages with specific guidance
- All stock entity conversion is handled by `utils.unified_stock_validator` with enhanced validation

### 资金查询功能规范 (Money Flow Query Guidelines) - v2.1.4

**标准资金类型定义**:
系统仅支持以下标准资金类型，不接受其他别称：
- **主力资金** = 超大单 + 大单（数据库字段：net_mf_amount）
- **超大单资金**：≥100万元（数据库字段：net_elg_amount）
- **大单资金**：20-100万元（数据库字段：net_lg_amount）
- **中单资金**：4-20万元（数据库字段：net_md_amount）
- **小单资金**：<4万元（数据库字段：net_sm_amount）

**非标准术语处理**:
- 当用户使用"机构资金"、"大资金"等非标准术语时，系统将提示：
  "请使用标准资金类型：主力资金、超大单资金、大单资金、中单资金、小单资金"

**板块查询支持**:
- 板块查询不支持简称，必须使用完整板块名称
- ✅ 正确：银行板块、新能源板块、白酒板块
- ❌ 错误：银行、新能源、白酒（缺少"板块"后缀）

**查询类型划分**:
1. **数据查询（SQL_ONLY）**：获取具体数值，快速返回表格数据
   - 个股主力资金查询："贵州茅台的主力资金"
   - 板块主力资金查询："银行板块的主力资金"
   - 主力净流入排行："主力净流入排名前10"
   
2. **深度分析（MONEY_FLOW）**：生成分析报告，包含LLM分析
   - 资金流向分析："分析贵州茅台的资金流向"
   - 超大单分析："分析宁德时代的超大单资金"
   
3. **复杂排名分析（RANK）**：未来规划，通过"排名分析："前缀路由

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

#### v2.1.18 - 参数提取器增强与特殊股票名称支持 (2025-07-05)

**参数提取器增强** ✅:
- **股票验证错误消息传递**: 修复`_extract_stocks`方法，确保验证失败时正确传递错误信息
- **月份/年份范围提取**: 完整实现`_extract_month_year_range`方法，支持"1月到3月"、"2024年"等表达
- **相对日期提取改进**: 添加"最后的"、"N年前"等模式支持，提升日期智能解析能力
- **限制提取逻辑优化**: 在提取数量限制前先排除已识别的股票名称，避免误匹配

**特殊股票名称支持** ✅:
- **ST股票提取修复**: 使用负向预查`(?=[和与及、，,]|$|\s|的|最|从)`避免过度匹配
- **特殊前缀支持**: ST/*ST/S/XD等前缀股票完美识别
- **特殊后缀支持**: -U/-W/-UW后缀股票（如埃夫特-U、思特威-W、奥比中光-UW）
- **英文+中文组合**: GQY视讯、TCL科技、TCL智家、TCL中环等
- **中文数字名称**: 三六零、七一二、六九一二等
- **A/B后缀股票**: 万科A、南玻A、特力A、渝三峡A等

**多股票提取改进** ✅:
- **extract_multiple_stocks增强**: 添加所有必要的股票名称提取模式
- **连接词支持扩展**: 支持和、与、及、、、，、vs、VS等多种连接词
- **边界条件优化**: 支持数字作为边界（如"TCL智家2025年"）
- **普通中文股票名**: 添加通用模式确保"大北农"等普通名称不被遗漏

**测试覆盖与验证** ✅:
- **参数提取器扩展测试**: 15个测试100%通过
- **特殊股票名称测试**: 7个测试100%通过，覆盖所有特殊格式
- **复杂查询验证**: "GQY视讯、七一二和大北农的对比"完美提取
- **TCL系列测试**: "TCL科技和TCL智家2025年一季度财务对比"正确识别两个股票

**技术实现细节** ✅:
- 修改`utils/parameter_extractor.py`优化股票提取逻辑
- 更新`utils/unified_stock_validator.py`的`extract_multiple_stocks`方法
- 增强正则表达式边界条件，添加`\d`、`vs`、`VS`等边界
- 创建专门的测试文件验证特殊股票名称提取能力

#### v2.1.17 - SQL Agent提取功能增强 (2025-07-04)

**提取功能增强** ✅:
- **日期范围连接符扩展**: 支持"-"和"~"作为日期范围连接符
- **月份/年份转日期范围**: 新增`_extract_month_year_range()`方法
- **股票名称智能清理**: 修复日期替换导致的股票名称提取问题

#### v2.1.15 - 前端主题系统完整实现 (2025-07-04)

**主题系统实现** ✅:
- **完整的主题切换系统**: ThemeContext上下文管理，支持手动切换
- **UI组件更新**: 侧边栏主题切换按钮，太阳/月亮图标
- **样式系统升级**: Tailwind配置`darkMode: 'class'`

#### v2.1.13 - SQL Agent公告查询功能实现 (2025-07-04 01:00)

**新功能实现** ✅:
- **公告查询模板**: 支持灵活的日期和股票描述，与股价查询保持一致
- **多种日期支持**: 最新、昨天、特定日期、日期范围（本周、本月等）
- **SQL模板扩展**: 新增ANNOUNCEMENT_BY_DATE和ANNOUNCEMENT_BY_RANGE模板
- **快速路径实现**: 公告查询通过SQL Agent快速返回，响应时间1-2秒

**功能边界明确** ✅:
- **SQL Agent**: 负责返回公告列表（标题、日期、链接）
- **RAG Agent**: 负责分析公告具体内容
- **路由优化**: 移除"最新公告"→ANNS的错误路由覆盖
- **文档说明**: 创建announcement_query_boundary.md明确功能边界

**测试与文档** ✅:
- 更新test-guide-comprehensive.md，添加1.18公告查询测试用例
- 创建功能边界说明文档
- 保持"查询公告："触发词给未来ANNS Agent

#### v2.1.15 - 前端主题系统完整实现 (2025-07-04)

**主题系统实现** ✅:
- **完整的主题切换系统**: 
  - 创建 `ThemeContext` 上下文管理主题状态
  - 支持手动切换亮色/暗色主题
  - 主题偏好保存到 localStorage
  - 智能初始化（用户设置 > 系统偏好 > 默认亮色）
- **UI组件更新**: 
  - 侧边栏添加主题切换按钮（支持折叠/展开状态）
  - 太阳/月亮图标切换
  - 优雅的过渡动画效果
- **样式系统升级**: 
  - Tailwind配置 `darkMode: 'class'`
  - 全局组件支持 `dark:` 前缀样式
  - 移除CSS媒体查询依赖

**Markdown表格优化** ✅:
- 修复暗色模式下表格标题可读性问题
- 暗色模式：浅色背景+黑色文字
- 亮色模式：浅灰背景+黑色文字
- 确保两种主题下的良好对比度

**组件主题适配** ✅:
- **App主容器**: 亮色白色背景，暗色深灰背景
- **侧边栏**: 亮色浅灰，暗色深灰，边框适配
- **消息气泡**: 用户消息支持两种主题配色
- **输入框**: 文字、占位符、边框主题适配
- **工具栏**: 图标和文字颜色主题适配

**技术实现** ✅:
- React Context API 管理主题状态
- localStorage 持久化用户偏好
- 系统偏好检测作为默认值
- 类名切换而非CSS变量

#### v2.1.17 - SQL Agent提取功能增强 (2025-07-04)

**提取功能增强** ✅:
- **日期范围连接符扩展**: 
  - 支持 "-" 和 "~" 作为日期范围连接符
  - 扩展 `_extract_date_range_from_query()` 支持多种格式
  - 示例：`贵州茅台2025-06-01至2025-06-30的K线`
- **月份/年份转日期范围**: 
  - 新增 `_extract_month_year_range()` 方法
  - 支持"6月"→(20250601, 20250630)转换
  - 支持"2024年"→(20240101, 20241231)转换
  - 支持季度："2025年第二季度"→(20250401, 20250630)
- **股票名称智能清理**: 
  - 修复"万科A前天的成交量"等提取问题
  - 智能去除时间后缀，保证股票名称准确
  - 优化 `_extract_query_params()` 逻辑

**测试验证** ✅:
- K线查询：支持日期范围、月份、年份、季度等多种格式
- 成交量查询：修复日期替换导致的股票名称提取错误
- 综合测试：27/27 模板测试全部通过
- 测试文档更新至v5.1版本

#### v2.1.14 - 公告日期范围查询功能完善 (2025-07-04)

**功能增强** ✅:
- **日期范围查询支持**: 
  - 支持"到"和"至"两种日期分隔符
  - 新增`_extract_date_range_from_query()`方法
  - 支持多种日期格式（YYYYMMDD、YYYY-MM-DD、YYYY年MM月DD日）
- **公告查询模板增强**: 
  - 更新正则表达式支持日期范围匹配
  - 修复普通路由的逻辑判断
  - 确保快速路径和普通路由行为一致
- **测试覆盖**: 
  - 创建专门的测试脚本验证功能
  - 所有测试用例通过

**技术实现** ✅:
- 新增日期范围提取和规范化方法
- 优化公告查询处理逻辑的条件分支
- 确保日期范围正确显示在查询结果中

#### v2.1.13 - SQL Agent公告查询功能实现 (2025-07-04)

**新功能实现** ✅:
- **公告查询完整支持**:
  - 最新公告查询
  - 指定日期公告查询
  - 日期范围公告查询（本月、本周、最近N天等）
- **三个SQL模板**:
  - ANNOUNCEMENT_LATEST
  - ANNOUNCEMENT_BY_DATE
  - ANNOUNCEMENT_BY_RANGE
- **功能边界明确**:
  - SQL Agent: 返回公告列表（标题、日期、链接）
  - RAG Agent: 分析公告内容

#### v2.1.12 - 多个后端崩溃问题修复与功能增强 (2025-07-03)

**后端稳定性修复** ✅:
- **利润查询崩溃修复**: 修复period参数缺失导致的KeyError，增加默认值处理
- **净利润排名崩溃修复**: 修复字段映射错误（n_income字段在财务表中实际为净利润）
- **RAG查询崩溃修复**: 修复limit参数类型错误，确保转换为整数类型
- **错误处理增强**: 所有修复点都添加了try-except保护和详细日志

**功能优化** ✅:
- **利润查询模板增强**: 
  - 支持指定报告期查询（如"贵州茅台2025年一季度利润"）
  - 默认查询最新报告期数据
  - 自动格式化报告期显示（如20250331→2025年一季度）
- **前端表格显示优化**: 
  - 修复Markdown表格在暗色模式下的背景色问题
  - 统一表格样式，提升可读性
- **资金查询格式优化**: 
  - 个股主力资金返回单行数据
  - 板块主力资金返回多行排名
  - 路由准确性提升，避免误判
- **营收排名模板增强**: 
  - 支持更多自然语言表达（"营业收入"、"营收"、"收入"）
  - 提升模板匹配成功率

**测试与文档** ✅:
- 更新test-guide-comprehensive.md至v4.7版本
- 添加新功能测试用例
- 更新错误处理测试用例

#### v2.1.11 - 财务指标排名快速路径实现 (2025-07-02)

**新增财务排名快速路径** ✅:
- **5个新增排名模板**: PE排名、PB排名、净利润排名、营收排名、ROE排名
- **性能大幅提升**: 查询响应时间从30-40秒降至1-2秒
  - PE/PB查询：约1.5秒（提升20倍）
  - 财务数据查询：约0.1秒（提升300倍）
  - ROE查询：约0.05秒（提升600倍）
- **智能参数提取**: 支持"最高/最低"、默认前10、数字提取等多种表达
- **数据过滤**: 自动排除异常值（PE<0或>10000、PB<0或>1000等）

**技术实现** ✅:
- 新增5个SQL模板（sql_templates.py）：PE_RANKING、PB_RANKING、PROFIT_RANKING、REVENUE_RANKING、ROE_RANKING
- 配置对应查询模板（query_templates.py）支持自然语言匹配
- 扩展sql_agent.py的_try_quick_query方法实现快速路径
- 修正数据库字段映射（使用n_income替代net_profit）

**测试与文档** ✅:
- 创建综合测试文件test_ranking_comprehensive.py（5分钟超时）
- 测试通过率：基本功能100%，综合测试64%（16/25）
- 更新test-guide-comprehensive.md添加5个新模板测试用例（v4.6）
- 项目状态文档已更新至v2.1.11

#### v2.1.10 - 资金类型术语标准化 (2025-07-02)

**资金类型术语标准化功能** ✅:
- **术语映射**: 支持16种常见非标准术语自动转换为标准术语
- **智能识别**: 自动将"游资"、"散户"等转换为标准术语
- **友好提示**: 查询结果中包含术语转换提示
- **错误引导**: 无法识别的术语提供标准术语说明

#### v2.1.4 - 资金查询功能标准化 (2025-07-02)

**资金查询功能规范化** ✅:
- **标准资金类型定义**: 统一使用主力资金、超大单、大单、中单、小单五种标准类型
- **非标准术语处理**: 机构资金、大资金等非标准术语将提示用户使用标准术语
- **板块查询支持**: 新增板块主力资金查询功能，必须使用"XX板块"完整名称
- **查询类型明确划分**: 
  - SQL_ONLY：快速数据查询（个股/板块主力资金、排名查询）
  - MONEY_FLOW：深度分析报告（需包含"分析"、"如何"等关键词）
- **测试文档更新**: test-guide-comprehensive.md v4.6，重组资金查询测试用例

#### v2.1.3 - 日期智能解析修复 (2025-06-30)

**日期智能解析DISTINCT问题修复** ✅:
- **问题根因**: tu_daily_detail表每个交易日有多条记录（对应不同股票），SQL查询缺少DISTINCT导致返回相同日期
- **修复内容**: 
  - 在`get_latest_trading_day()`、`get_nth_trading_day_before()`、`get_trading_days_range()`方法中添加DISTINCT
  - 修复文件：`utils/date_intelligence.py`（第165、175、337、371行）
- **验证结果**:
  - 最近5个交易日: 正确返回`2025-06-23 至 2025-06-27`（修复前错误：`2025-06-27 至 2025-06-27`）
  - SQL Agent测试成功率: 17/21 (81%)

#### v2.1.2 - SQL Agent快速模板与路由机制修复 (2025-06-30)

**SQL Agent快速模板实现** ✅:
- **扩展SQL模板库**: 新增7个快速模板（市值排名、涨跌幅排名、成交额排名、PE/PB查询、历史K线等）
- **性能提升**: 快速路径平均响应0.02秒，加速比2481.5倍
- **优化查询验证**: 排名查询不再触发股票验证

**路由机制修复** ✅:
- **修复TEMPLATE_ROUTE_OVERRIDE错误**: 删除将SQL Agent查询路由到未实现Agent的覆盖规则
- **确保快速模板正常工作**: SQL Agent可以正确处理涨幅排名、市值排名等查询

**股票识别优化** ✅:
- **修复"平安"歧义**: 移除有歧义的"平安"→"中国平安"映射
- **改进股票名称提取**: 优先直接提取完整股票名称，修正"万科企业"为"万科A"

#### v2.1.1 - 代码清理与7-Agent架构设计 (2025-06-29)

**代码清理与验证** ✅:
- **删除未使用文件**: 
  - `utils/chinese_query_parser.py` - 从未被调用的中文查询解析器
  - `utils/schema_cache_manager.py` - 功能已被SchemaKnowledgeBase替代
- **确认实际实现**: 
  - SchemaKnowledgeBase是实际使用的Schema系统
  - 查询速度<10ms，性能优秀
  - 通过测试用例"路桥信息的最新股价是多少？"追踪验证

**7-Agent架构设计** ✅:
- **现有4个Agent**: SQL、RAG、Financial、MoneyFlow
- **新增3个Agent**: 
  - Rank Agent - 排名分析（触发词："排行分析："）
  - ANNS Agent - 公告查询（触发词："查询公告："）
  - QA Agent - 董秘互动（触发词："董秘互动："）
- **路由优化**: 触发词优先匹配，提升响应准确率

**Agent职责明确** ✅:
- 解决了Agent功能重叠问题
- 每个Agent有清晰的职责边界
- SQL Agent处理80%常见查询，专业Agent处理深度分析

#### v1.5.5 - 统一股票验证器大幅优化 (2025-06-29)

**验证器智能化改进** ✅:
- **大小写智能提示**: 识别.sh/.sz/.bj等所有大小写组合，精确提示正确格式.SH/.SZ/.BJ
- **常见简称映射**: 20个常用简称自动提示完整名称（茅台→贵州茅台、平安→中国平安、建行→建设银行等）
- **精细错误分类**: 新增INVALID_CASE、STOCK_NOT_EXISTS、USE_FULL_NAME错误类型
- **复合查询支持**: extract_multiple_stocks方法支持"贵州茅台和五粮液对比"等多股票查询

**错误提示优化** ✅:
- 大小写错误: "证券代码后缀大小写错误，应为.SH"（而非通用的格式错误）
- 简称提示: "请使用完整公司名称，如：贵州茅台"
- 股票不存在: "股票代码123456.SH不存在，请检查是否输入正确"
- 位数错误: "股票代码应为6位数字，您输入了5位"

**Agent集成** ✅:
- SQL Agent和Money Flow Agent已集成新验证器
- Financial Agent保持原有验证逻辑不变
- RAG Agent维持宽松验证策略
- 所有Agent验证逻辑一致性测试100%通过

#### v2.1.2 - SQL Agent快速模板与路由文档化 (2025-06-30)

**SQL Agent快速模板完成** ✅:
- **新增7个SQL模板**: 市值排名、涨跌幅排名、成交额排名、PE/PB查询、历史K线、板块股票
- **性能大幅提升**: 快速路径平均响应0.02秒，加速比2481.5倍
- **智能路径选择**: 模板匹配成功时避免LLM调用
- **格式化输出**: 专业的排名表格、估值指标、K线数据展示

**路由机制文档化** ✅:
- **创建docs/ROUTING_MECHANISM.md**: 详细说明5级优先级路由体系
- **7-Agent定位明确**: 每个Agent的职责和典型查询
- **实现细节**: 文件位置、行号、测试用例
- **更新指南**: 如何添加新模板、调整优先级

**查询验证优化** ✅:
- **排名查询免验证**: 排名类查询不再触发股票验证
- **更灵活的判断**: 区分特定股票查询和排名查询

#### v2.1.1 - 7-Agent架构设计与代码清理 (2025-06-29)

**Phase 0 路由机制优化** ✅:
- **触发词路由**: 配置化管理，避免硬编码
- **模板覆盖机制**: TEMPLATE_ROUTE_OVERRIDE修正路由冲突
- **QueryType扩展**: 新增RANK、ANNS、QA类型

**代码清理** ✅:
- **删除未使用文件**: chinese_query_parser.py、schema_cache_manager.py
- **确认实现**: SchemaKnowledgeBase是实际使用的Schema系统

#### v1.5.4 - 流式响应完整实现与项目清理 (2025-06-28)

**流式响应功能完成** ✅:
- **WebSocket流式通信**: 实现逐字符显示效果，模拟真实打字体验
- **打字光标动画**: 添加闪烁光标，增强视觉反馈
- **停止查询按钮**: 支持中断正在进行的查询，提升用户控制感
- **useStreamingResponse Hook**: 封装流式响应逻辑，便于复用

**项目结构优化** ✅:
- **目录清理**: 删除混淆的`stock-analysis-frontend`旧目录
- **文档更新**: 在CLAUDE.md开头添加重要目录说明
- **避免混淆**: 明确标注主前端目录为`/frontend`

**技术实现** ✅:
- 自定义Hook管理流式状态和定时器
- 支持配置每次显示字符数和间隔时间
- 内存泄漏防护，组件卸载时清理定时器
- 集成停止功能到SmartInput组件

#### v1.5.3+ - React前端Phase 1基本完成总结 (2025-06-27)

**Phase 1 React前端MVP成果汇总** ✅:
- **完整Claude.ai风格实现**: 260px侧边栏、主聊天区、优雅的消息展示
- **全功能Markdown渲染**: 代码高亮(Prism.js)、表格美化、数学公式(KaTeX)、引用块
- **双环境开发方案成熟**: WSL2开发 + Windows测试的完整工作流
- **UI/UX细节完善**: 深色主题优化、分屏布局一致性、侧边栏折叠、响应式设计
- **API集成完整**: 支持所有查询类型（SQL、RAG、财务分析、资金流向）

**技术栈确立** ✅:
- React 18.3.1 + TypeScript 5.6.2 + Vite 5.4.10
- react-markdown 9.0.1 + 完整插件生态链
- Tailwind CSS 3.4.15 + 自定义Claude主题
- Axios API调用 + 错误处理机制

**开发经验沉淀** ✅:
- 环境切换脚本（auto-switch-to-wsl2.sh、switch-env.bat）
- WSL2专用配置（.env.wsl2）解决API访问问题
- 完整的测试指南（TEST_ENVIRONMENT_GUIDE.md）
- 双环境node_modules独立管理方案

#### v1.5.3+ - React前端UI深色主题优化 (2025-06-27)

**深色主题UI完善** ✅:
- **复制按钮样式优化**: 
  - 深色主题下使用深灰色背景(#1e1e1e)，避免与代码块背景冲突
  - 悬停效果使用更深的颜色(#2a2a2a)，提供清晰的交互反馈
  - 图标颜色调整为浅灰(#e0e0e0)，确保在深色背景下清晰可见
  - 优化按钮位置和内边距，提升点击体验

- **分屏布局一致性强化**:
  - 统一文档查看器和主消息区的宽度处理
  - 确保深色主题下的边框和分隔线颜色一致
  - 优化滚动条样式，与深色主题协调

**技术实现细节** ✅:
- 更新DocumentViewer组件的复制按钮样式逻辑
- 添加深色主题专用的hover状态样式
- 调整z-index层级，确保按钮始终可见
- 完善深色主题下的对比度和可访问性

#### v1.5.3 - 分屏布局一致性修复 (2025-06-27)

**分屏模式宽度一致性优化** ✅:
- **问题修复**: 解决分屏模式下消息容器与输入框宽度不一致的问题
- **布局改进**: 统一使用固定宽度(768px)确保视觉对齐
- **样式优化**: 移除原有的gap留白，使用padding实现间距控制
- **细节完善**: 输入框容器添加px-4内边距，与消息区域完美对齐

**技术实现** ✅:
- 修改InputArea组件的容器样式，使用固定宽度替代百分比宽度
- 调整主布局的flex-grow策略，确保分屏时的空间分配合理
- 优化padding和margin配置，实现像素级对齐
- 提升整体视觉一致性和专业度

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
2. **test-guide-comprehensive.md** - Comprehensive testing procedures and test cases (覆盖所有7个Agent，包含已实现和未来规划功能)
3. **docs/project_status/CURRENT_STATUS.md** - Project status, version history, and known issues

### Testing Strategy

**Script Testing (Backend API)**:
- Use the test-guide-comprehensive.md for comprehensive testing procedures
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

## Next Development Priority (v2.2.0 - 查询模块化架构重构)

### 系统现状评估 (2025-07-05)

**已完成功能**:
- ✅ React前端Phase 1完整实现（Claude.ai风格、流式响应、分屏布局）
- ✅ 后端核心功能100%完成（SQL、RAG、Financial、MoneyFlow）
- ✅ SchemaKnowledgeBase快速查询（<10ms查询，499个中文映射）
- ✅ 股票验证公用模块化完成（stock_validation_helper.py）
- ✅ SQL Agent全面使用公用验证方法，测试通过率81.8%

**系统问题与优化空间**:
- ⚠️ 代码重复严重，每个Agent都有独立的参数提取和验证逻辑
- ⚠️ 错误处理不统一，用户体验不一致
- ⚠️ 缺少统一的结果格式化机制
- ⚠️ 新功能开发需要在多处重复实现

### v2.2.0 开发计划（7天）- 查询模块化架构重构

#### Phase 1：创建基础模块（2天）

**Day 1 - 参数处理模块**：
1. 创建`parameter_extractor.py` - 统一参数提取
   - 股票提取（复用stock_validation_helper）
   - 日期提取（复用date_intelligence）
   - 数量限制提取
   - 指标列表提取
2. 创建`query_validator.py` - 统一参数验证
   - 必需参数验证
   - 参数格式验证
   - 范围检查
3. 编写单元测试

**Day 2 - 结果处理模块**：
1. 创建`result_formatter.py` - 统一结果格式化
   - 排名表格格式化
   - 财务数据格式化
   - K线数据格式化
   - 通用表格格式化
2. 创建`error_handler.py` - 统一错误处理
   - 错误码定义
   - 用户友好消息
   - 调试信息管理
3. 编写集成测试

#### Phase 2：模块集成（3天）

**Day 3 - SQL Agent重构**：
1. 集成新模块到SQL Agent
2. 替换现有的参数提取逻辑
3. 统一错误处理流程
4. 保持功能完全兼容

**Day 4 - 其他Agent集成**：
1. RAG Agent集成新模块
2. Financial Agent集成
3. Money Flow Agent集成
4. 统一所有Agent的处理流程

**Day 5 - 测试与修复**：
1. 完整回归测试
2. 性能测试
3. 修复发现的问题
4. 更新文档

#### Phase 3：扩展优化（2天）

**Day 6 - 功能增强**：
1. 添加更多格式化选项
2. 增强参数提取能力
3. 优化缓存机制
4. 支持更多查询模式

**Day 7 - 文档与交付**：
1. 编写模块使用指南
2. 更新所有相关文档
3. 创建迁移指南
4. 最终测试和发布

### 成功指标
- ✅ 代码重复率降低80%
- ✅ 新功能开发时间减少50%
- ✅ 测试覆盖率提升到90%
- ✅ 查询响应时间减少30%

### Git版本管理
```bash
# 当前分支: dev-react-frontend-v2
# 版本: v2.1.19 → v2.2.0
git add -A && git commit -m "feat: 查询模块化架构重构"
```

The system is designed for production use with comprehensive error handling, logging, monitoring capabilities, and full LangChain modernization (v1.3.8).

## 查询模块化架构重构进展（2025-07-05更新）

### ✅ Phase 1: 基础模块开发（已完成 - 2025-07-05）

#### 完成的模块：
1. **parameter_extractor.py** - 统一参数提取器
   - 支持股票、日期、数量、排序、板块等参数提取
   - 集成UnifiedStockValidator和DateIntelligence
   - 修复了股票简称处理不一致问题
   
2. **query_validator.py** - 统一参数验证器
   - 完整的参数验证逻辑
   - 基于模板的验证支持
   
3. **result_formatter.py** - 统一结果格式化器
   - 支持表格、文本等多种格式
   - 智能列类型推断和格式化
   
4. **error_handler.py** - 统一错误处理器
   - 错误分类和严重程度管理
   - 用户友好的错误消息

#### 测试结果：
- 参数提取测试：28/38通过（73.7%）
- 结果处理测试：13/13通过（100%）

### 🚧 Phase 2: Agent适配（进行中）

**当前任务**：将各个Agent适配到新的模块化架构

### 📅 后续开发计划

### 🎯 SQL Agent快速模板扩展（1-2天）

**目标**：基于模块化架构，扩展更多快速查询模板

**新增模板列表**：
1. 历史K线查询（支持任意时间段）
2. 历史交易量查询（支持聚合统计）
3. 财务指标对比（多股票横向对比）
4. 板块成分股查询
5. 技术指标查询（MA、MACD等）

### 🚀 三个新Agent设计与实现（5-7天）

#### 2.1 设计阶段（必须先完成）
- Rank Agent详细设计文档
- ANNS Agent详细设计文档
- QA Agent详细设计文档
- 统一Agent接口规范
- **必须获得用户批准后才能开始开发**

#### 2.2 原型开发（小步验证）
- 每个Agent先实现最小可行版本
- 独立测试核心功能
- 不修改现有路由机制

#### 2.3 集成开发（谨慎推进）
- 更新路由配置（需用户确认）
- 实现触发词机制
- 添加错误处理和降级策略

#### 2.4 测试验证
- 单元测试、集成测试、回归测试、性能测试
- 确保无性能退化

### 🔧 Phase 3: 专业Agent快速路径优化（3-4天）

#### 3.1 SQL Agent进一步优化
- 实现更多快速模板
- 优化现有模板性能
- 添加智能缓存机制
- 目标：常用查询<0.3秒

#### 3.2 RAG Agent快速路径
- 常见查询模式识别
- 向量检索优化
- 结果缓存机制
- 目标：常用RAG查询<2秒

#### 3.3 Financial Agent快速路径
- 财务指标预计算
- 分析模板优化
- 并行计算实现
- 目标：财务分析<10秒

#### 3.4 Money Flow Agent快速路径
- 数据聚合优化
- 实时计算缓存
- 快速统计实现
- 目标：资金分析<5秒

#### 3.5 新Agent快速路径（如果Phase 2完成）
- Rank Agent快速排名
- ANNS Agent快速公告查询
- QA Agent快速问答匹配
- 目标：快速路径覆盖80%场景

### ✅ Phase 4: 全面集成测试（2-3天）

#### 4.1 功能测试
- 7个Agent完整功能测试
- 路由机制测试
- 边界条件测试

#### 4.2 性能测试
- 响应时间测试
- 并发测试
- 压力测试

#### 4.3 用户验收测试
- 真实场景测试
- 用户反馈收集
- 最终调优

### 📝 开发原则

1. **设计先行**：每个Phase必须先完成设计文档并获得用户确认
2. **小步快跑**：功能点独立开发，避免大规模重构
3. **沟通优先**：重要决策必须请示，定期汇报进展
4. **测试驱动**：先写测试用例，回归测试防止破坏
5. **安全第一**：所有输入验证，所有输出过滤，不修改核心稳定代码

### ⏱️ 总时间估算：12-17天

## 暂缓开发的功能

### 中文数字识别功能（2025-07-03 23:21 决定暂缓）

**功能描述**: 支持"前十"、"前二十"等中文数字表达自动转换为阿拉伯数字

**暂缓原因**:
1. 不利于系统快速开发和迭代
2. 增加系统复杂度，可能引入新的问题
3. 用户可以直接使用阿拉伯数字，学习成本低
4. 投入产出比不高

**设计方案**: 详见 `docs/design/chinese_number_recognition_design.md`

**替代方案**: 
- 在用户界面提供清晰的查询示例
- 优化错误提示，引导用户使用正确格式

**未来计划**: 待系统稳定后，根据用户反馈决定是否实施