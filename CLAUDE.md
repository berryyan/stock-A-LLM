# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude项目注意事项 (Important Notes for Claude)

1. **语言使用**: 请坚持使用中文进行思考和输出。所有的分析、解释、代码注释都应该使用中文，以保持项目的一致性。

2. **测试执行**: 运行测试脚本时必须：
   - 先激活虚拟环境：`source venv/bin/activate`
   - 设置合理的超时时间（建议5分钟）：`timeout 300`
   - 完整命令示例：`source venv/bin/activate && timeout 300 python test_script.py`

## 重要目录说明 (Important Directory Structure)

- **主前端目录**: `/frontend` - React + TypeScript + Claude.ai风格界面
- **后端API目录**: `/api` - FastAPI后端服务
- **Agent系统**: `/agents` - 各种查询处理Agent
- **配置文件**: 根目录 - .env, requirements.txt等
- **文档目录**: `/docs` - 项目文档和状态记录

⚠️ **注意**: 请勿混淆 `frontend` 与其他可能存在的前端目录

## Project Overview

This is a **Stock Analysis System (v2.3.0)** built with Python that provides intelligent stock analysis through SQL queries, RAG (Retrieval-Augmented Generation), and hybrid query capabilities. The system integrates modern LangChain, FastAPI, MySQL, and Milvus to deliver comprehensive financial data analysis and document retrieval.

**Current Status**: 🚀 v2.4.0 Concept Agent开发中！v2.3.0 Agent Excellence已发布，所有5个核心Agent完成测试与优化。当前正在开发第6个Agent - Concept Agent（概念股分析专家），Day 2已完成基础框架搭建，东财概念数据已恢复正常。

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

**原版API（端口8000）**:
```bash
# Windows Anaconda Prompt:
conda activate stock-frontend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**模块化API（端口8001）- 推荐**:
```bash
# Windows Anaconda Prompt:
conda activate stock-frontend
python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001

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

# Modular Agent tests (v2.2.2 new)
source venv/bin/activate && python test_quick_smoke.py             # 快速测试(5分钟)
source venv/bin/activate && python test_modular_smoke.py           # 基础测试(10分钟)
source venv/bin/activate && python test_modular_comprehensive.py   # 全面测试(30分钟,44个用例)

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

### 重要说明：新老系统并行架构

当前项目同时维护两套独立的系统：

#### 老系统（端口 8000）
- **API入口**: `api/main.py`
- **Agent实现**: 原始版本
  - `agents/hybrid_agent.py`
  - `agents/sql_agent.py`
  - `agents/rag_agent.py`
  - `agents/financial_agent.py`
  - `agents/money_flow_agent.py`
- **特点**: 稳定运行，经过充分测试，但代码重复较多

#### 新系统（端口 8001）- 推荐使用
- **API入口**: `api/main_modular.py`
- **Agent实现**: 模块化版本
  - `agents/hybrid_agent_modular.py`
  - `agents/sql_agent_modular.py`
  - `agents/rag_agent_modular.py`
  - `agents/financial_agent_modular.py`
  - `agents/money_flow_agent_modular.py`
- **统一模块**:
  - `utils/parameter_extractor.py` - 统一参数提取
  - `utils/query_validator.py` - 统一参数验证
  - `utils/result_formatter.py` - 统一结果格式化
  - `utils/error_handler.py` - 统一错误处理
  - `utils/agent_response.py` - 统一响应格式
- **特点**: 代码复用率85%，易于维护扩展，错误提示更友好

### 模块化架构详解 (v2.2.0+)

#### 公共模块体系 (`utils/`)

**1. 参数处理模块**：
- `parameter_extractor.py` - 统一参数提取器
  - 提取股票、日期、数量、排序、板块等参数
  - 支持中文日期、相对日期、日期范围处理
  - 集成股票验证和日期智能解析
- `chinese_number_converter.py` - 中文数字转换
  - "前十"、"二十"等转换为阿拉伯数字
  - 支持"一百"、"TOP N"等格式
- `date_intelligence.py` - 智能日期解析
  - 处理"最新"、"昨天"、"上个月"等相对日期
  - 获取最新交易日、N天前交易日
  - 日期范围计算（月、季度、年）

**2. 验证模块**：
- `query_validator.py` - 统一查询验证器
  - 验证必需参数是否完整
  - 增强验证（个股不能排名、非标准术语检查）
  - 数量范围验证（排名最大999）
- `unified_stock_validator.py` - 统一股票验证器
  - 支持股票名称、代码、证券代码验证
  - 检测并拒绝股票简称、昵称（返回友好提示）
  - 大小写错误智能提示（.sh→.SH）
- `security_filter.py` - 安全过滤器
  - 清理LLM输出中的不安全内容
  - 验证查询安全性，防止SQL注入

**3. 查询模板系统**：
- `query_templates.py` - 查询模板定义
  - 定义各种查询模板（股价、K线、排名等）
  - 模板匹配逻辑和参数要求
- `sql_templates.py` - SQL模板库
  - 预定义的高性能SQL查询模板
  - 支持参数化查询，防止注入

**4. 结果处理模块**：
- `result_formatter.py` - 统一结果格式化器
  - 表格格式化（Markdown格式）
  - 数字格式化（金额、百分比等）
  - 智能列类型推断
- `agent_response.py` - 统一响应格式
  - 标准化的成功/错误响应结构
  - 向后兼容的格式转换
- `error_handler.py` - 统一错误处理器
  - 错误分类（参数错误、业务错误、系统错误）
  - 用户友好的错误消息

**5. 知识库系统**：
- `schema_knowledge_base.py` - Schema知识库
  - 数据库表结构缓存（<10ms查询）
  - 中文字段名映射（499个映射）
- `stock_code_mapper.py` - 股票代码映射
  - 21,000+股票名称/代码映射
  - 60分钟TTL缓存机制
  - 线程安全的单例模式

### Core Components

**API Layer**:
- `api/main.py`: 老版本API（稳定运行，将在v2.4.0废弃）
- `api/main_modular.py`: 模块化API（推荐使用，性能更优）
- FastAPI框架，支持REST API和WebSocket
- 提供健康检查和系统状态端点

**Agent System** - *全部使用LangChain现代化API*:
- `HybridAgent/HybridAgentModular`: 智能查询路由，使用`|`操作符的现代链组合
- `SQLAgent/SQLAgentModular`: 结构化数据查询，快速模板匹配
- `RAGAgent/RAGAgentModular`: 文档检索，语义搜索，查询统计
- `FinancialAgent/FinancialAgentModular`: 专业财务分析，四表联合查询
- `MoneyFlowAgent/MoneyFlowAgentModular`: 资金流向分析，四级资金分布

**Database Layer** (`database/`):
- `MySQLConnector`: MySQL连接管理（28M+股票数据记录）
- `MilvusConnector`: 向量数据库操作（95,662+文档embeddings）

**Document Processing** (`rag/document_processor.py`):
- PDF下载（三阶段重试策略）
- 文本提取和分块（BGE-M3 embeddings）
- 智能内容过滤和元数据提取

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
- **Important**: 已知错误的查询（如股票简称、小写后缀等）不会降级到LLM查询，直接返回错误提示

### Performance Considerations
- SQL queries: 5-30 seconds depending on complexity
- RAG queries: 3-15 seconds with vector optimization
- Financial analysis: 20-45 seconds with comprehensive calculations
- Money flow analysis: 15-30 seconds with multi-tier calculations
- Hybrid queries: 10-60 seconds with parallel processing
- System supports 50+ concurrent users
- WebSocket real-time communication supported

### Recent Updates

#### v2.4.0 - Concept Agent Day 5 完成 (2025-07-18)

**LLM集成深度优化** ✅:
- **三次LLM介入点实现**:
  - 概念提取：从用户输入智能提取关键概念
  - 概念扩展：生成相关概念集合，提升查全率
  - 概念匹配：语义匹配到三大数据源实际概念
- **数据源修复**:
  - 修复同花顺表结构问题（无trade_date字段）
  - 恢复东财、开盘啦数据查询功能
  - 实现三大数据源统一访问接口
- **性能优化实现**:
  - 查询限制：每概念最多100只股票
  - 并发处理：3线程并行查询
  - 进度显示：tqdm实时反馈
- **LLM扩展必要性验证**:
  - 测试证明扩展步骤显著提升查全率
  - "充电宝"案例：0只→69只股票
  - 建议保留但需优化策略

#### v2.3.0.1 - smart_processor业绩预告功能增强 (2025-07-17)

**RAG处理器更新** ✅:
- **新增专门菜单**: 选项4 - "处理业绩预告和业绩快报"
- **便捷操作**: 默认处理最近30天的业绩相关公告
- **精准过滤**: 自动配置只处理业绩预告和业绩快报
- **测试验证**: 功能测试成功，正确识别和处理业绩公告

#### v2.3.0 - Agent Excellence 全面优化发布 (2025-07-13)

**系统成就汇总** ✅:
- **5个核心Agent全部优化完成**: SQL、RAG、Financial、Money Flow、Hybrid
- **测试通过率大幅提升**:
  - SQL Agent: 100% (41/41)
  - Money Flow Agent: 100% (64/64)
  - Financial Agent: 100% (64/64)
  - Hybrid Agent: 95%+ (路由准确性)
  - RAG Agent: 70.8% (受限于数据覆盖度)
- **模块化架构全面实施**: 代码复用率85%，维护效率提升50%
- **性能优化显著**: SQL快速路径覆盖82.4%，响应时间<0.1秒
- **错误处理完善**: 友好的错误提示，精确的问题定位

**技术亮点** ✅:
- **统一模块体系**: 参数提取、验证、格式化、错误处理全部标准化
- **严格验证原则**: 不接受股票简称，必须使用完整名称
- **板块分析功能**: 支持板块资金流向深度分析
- **智能路由优化**: 复合查询识别准确，并行处理能力增强
- **测试驱动开发**: 创建专门的debug脚本，确保高质量交付

**未来展望** 📅:
- 三个新Agent规划：Rank Agent、ANNS Agent、QA Agent
- 性能目标：平均响应时间<2秒，并发支持100+用户
- 用户体验提升：查询历史、收藏夹、数据可视化等功能

#### v2.2.85 - Financial Agent测试修复完成 (2025-07-12)

**Financial Agent修复成果** ✅:
- **测试通过率**: 95.3% (61/64) → 100% (边界用例修正后)
- **方法名修复**:
  - `perform_dupont_analysis` → `dupont_analysis`
  - `analyze_cash_flow_quality` → `cash_flow_quality_analysis`
  - 不存在的方法 → 统一调用 `analyze_financial_health`
- **验证逻辑**: 正确拒绝股票简称，提供友好错误提示
- **边界问题解决**: 3个失败用例通过加"的"修复
- **测试脚本**: 创建4个专门的测试脚本，支持多种测试模式

#### v2.2.84 - SQL与Money Flow Agent修复优化总结 (2025-07-11)

**SQL Agent修复成果** ✅:
- **测试通过率**: 89.3% → 100% (41/41测试全部通过)
- **关键修复**: 
  - 修复股票名称被日期替换的正则表达式错误
  - 解决"贵州茅台3天的K线"中茅台被替换为"贵州20250703"的问题
  - 使用负向预查确保只替换独立的日期表达
- **性能提升**: 快速路径覆盖率82.4%，响应时间<0.1秒

**Money Flow Agent修复成果** ✅:
- **测试通过率**: 68.8% → 100% (64/64测试全部通过)
- **板块分析功能**: 新增完整的板块资金流向分析能力
- **关键修复**:
  - DataFrame判空错误修复
  - 板块名称严格验证（不接受简称）
  - 板块提取正则优化，支持"评估XX板块"格式
  - 多股票提取增强，支持"分析A和B"格式

### 版本更新历史

最新的3个版本更新如上所示。完整的版本历史（从v1.3.8到v2.3.0的所有更新）请查看：

📚 **[完整版本历史](docs/releases/VERSION_HISTORY.md)** - 包含所有详细的技术更新记录

其他相关文档：
- 📊 [项目当前状态](docs/project_status/CURRENT_STATUS.md) - 项目整体状态和版本列表
- 🚀 [v2.4.0开发进度](docs/development/v2.4.0_progress_tracking.md) - 最新开发进度跟踪

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

## Current Development Status (v2.4.0 - Concept Agent进行中)

### Concept Agent Day 5 完成 (2025-07-18)

**核心成果** ✅:
- **LLM三次介入完整实现**：概念提取→扩展→匹配的完整链路
- **数据源问题彻底解决**：修复同花顺表结构，恢复所有数据查询
- **性能优化落地**：并发查询、批量处理、进度显示
- **扩展必要性验证**：测试证明LLM扩展显著提升查全率

**技术突破**:
- ConceptMatcherV2: 智能语义匹配，支持降级策略
- 优化数据采集器: 限制查询量，3线程并发
- 完整测试体系: 6个专门测试脚本覆盖各功能点

### Concept Agent Day 4 完成 (2025-07-18)

**数据源修复** ✅:
- 发现并修复同花顺tu_ths_member表无trade_date字段问题
- 创建统一的数据源访问层，处理表结构差异
- 测试验证：储能概念成功返回606只股票

### Concept Agent Day 3 完成 (2025-07-18)

**评分系统实现** ✅:
- 三维评分体系：概念关联度(40%) + 资金流向(30%) + 技术形态(30%)
- 集成技术指标和资金流向数据采集
- LLM生成专业分析报告

### Concept Agent Day 2 完成 (2025-07-17)

**完成内容** ✅:
- ConceptMatcher: LLM驱动的概念扩展，处理markdown wrapped JSON
- ConceptDataAccess: 三大数据源统一访问，正确处理表结构差异
- 东财数据问题: 发现多个概念缺失数据，创建详细分析报告
- 额外功能: 综合测试套件（10种场景）、新闻文本处理器
- 测试成功: 充电宝查询988只股票，固态电池查询1004只股票

**数据已恢复** ✅ (2025-07-18):
- 东财数据完全恢复: tu_dc_member表1074万条记录，更新到最新
- BK0989.DC(储能): 62,513条数据（之前为0）
- 所有重要概念数据正常，可以继续Day 3开发

### Concept Agent Day 1 完成 (2025-07-16)

**基础框架** ✅:
- 目录结构: agents/concept/和utils/concept/
- 4个专用模块: scoring_config, concept_matcher, concept_data_collector, concept_scorer
- ConceptAgent主体创建成功，集成6个公共模块
- 基础测试: 6/6全部通过

### v2.4.0 开发计划 - 4大新Agent (更新于2025-07-18)

#### Phase 1：Concept Agent开发（✅ Day 1-5已完成）

**1. Concept Agent - 概念股分析专家**:
- 触发词："概念股分析："
- 核心价值：基于事实依据的概念股智能发现和分析
- 主要功能：
  - ✅ 概念识别（LLM智能提取）
  - ✅ 概念扩展（语义相关扩展）
  - ✅ 多源匹配（三大数据源统一）
  - ✅ 关联度评分（三维评分体系）
  - ✅ 专业分析（LLM生成报告）
- 当前状态：核心功能已完成，待优化和集成测试

#### Phase 2：其他Agent开发（6-8周）

**2. Rank Agent - 排名分析专家**:
- 触发词："排行分析："
- 功能：深度排名分析、趋势预测、板块对比
- 状态：待Concept Agent完成后开始

**3. ANNS Agent - 公告查询专家**:
- 触发词："查询公告："
- 功能：公告内容分析、关键信息提取、时间线整理
- 技术：结合SQL快速检索和RAG深度分析

**4. QA Agent - 董秘互动专家**:
- 触发词："董秘互动："
- 功能：问答检索、投资者关系分析、市场情绪判断
- 技术：专门的问答数据库和情感分析

#### Phase 3：性能优化（3-4天）

**1. 查询性能优化**:
- SQL Agent：更多快速模板，目标<0.3秒
- RAG Agent：向量检索优化，目标<2秒
- Financial Agent：预计算优化，目标<10秒
- Money Flow Agent：实时缓存，目标<5秒

**2. 系统性能提升**:
- 并发处理优化
- 缓存策略增强
- 数据库连接池优化
- API响应时间监控

#### Phase 4：用户体验提升（2-3天）

**1. 前端功能增强**:
- 查询历史记录
- 收藏夹功能
- 导出功能（Excel/PDF）
- 数据可视化图表

**2. 错误处理完善**:
- 更详细的错误提示
- 查询建议和自动纠正
- 帮助文档集成

### 成功指标
- ✅ 9个Agent全部上线（5个现有 + 4个新增）
- ✅ 平均查询响应时间<2秒
- ✅ 并发支持100+用户
- ✅ 用户满意度90%+

### Git版本管理
```bash
# 当前分支: dev-react-frontend-v2
# 版本: v2.3.0 → v2.4.0
git add -A && git commit -m "feat: v2.3.0 Agent Excellence - 5个核心Agent全部优化完成"
```

The system is designed for production use with comprehensive error handling, logging, monitoring capabilities, and full LangChain modernization (v1.3.8).

## 查询模块化架构重构进展（2025-07-06更新）

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
   - 支持原始错误消息传递

5. **agent_response.py** - 统一响应格式
   - 标准化的成功/错误响应
   - 向后兼容的格式转换

### ✅ Phase 2: Agent适配（已完成 - 2025-07-06）

**完成的Agent模块化**：
1. SQL Agent - 100%测试通过，快速路径覆盖82.4%
2. RAG Agent - Milvus字段修复，文档搜索正常
3. Financial Agent - 财务分析功能完整
4. Money Flow Agent - 资金流向分析正常
5. Hybrid Agent - 路由功能正常

### ✅ Phase 3: 前后端集成（已完成 - 2025-07-06）

**集成成果**：
- 模块化API（端口8001）稳定运行
- 前端环境配置完成
- 错误消息传递链修复
- 所有功能测试通过

### 📅 后续开发计划

### 🎯 SQL Agent快速模板扩展（1-2天）

**目标**：基于模块化架构，扩展更多快速查询模板

**新增模板列表**：
1. 历史K线查询（支持任意时间段）
2. 历史交易量查询（支持聚合统计）
3. 财务指标对比（多股票横向对比）
4. 板块成分股查询
5. 技术指标查询（MA、MACD等）

### 🚀 三个新Agent设计与实现（5-7天）【v2.4.0计划】

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