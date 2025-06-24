# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Stock Analysis System (v1.4.1)** built with Python that provides intelligent stock analysis through SQL queries, RAG (Retrieval-Augmented Generation), and hybrid query capabilities. The system integrates modern LangChain, FastAPI, MySQL, and Milvus to deliver comprehensive financial data analysis and document retrieval.

**Current Status**: ✅ 系统全面修复完成，所有核心功能100%正常运行。Windows兼容性问题已解决，RAG查询功能完全恢复，智能日期解析精准识别最新交易日，Bug修复验证100%通过。Phase 1 深度财务分析系统开发完成, 新增专业财务分析功能, 新增数据驱动的智能日期解析功能。

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
```bash
# Start the API server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start interactive RAG interface
python rag_query_interface.py

# Run system health check
python scripts/utils/system_check.py
```

### Testing
```bash
# Test database connections
python scripts/tests/test_databases.py

# Test API endpoints
python scripts/tests/test_api.py

# Test specific components
python scripts/tests/test_components.py

# Essential comprehensive tests (keep in root directory)
python baseline_test.py
python comprehensive_verification.py

# Test financial analysis features (v1.4.0 new)
python test_financial_agent.py
python test_advanced_financial_features.py

# Test intelligent date parsing features (v1.4.1 new)
python test_date_intelligence.py
python test_date_intelligence_integration.py

# Bug fix verification tests (v1.4.1 fixes)
python test_bug_fixes.py
python test_money_flow_analysis.py
python test_latest_trading_day_fix.py
python test_comprehensive_final.py

# Archived test scripts (in scripts/tests/)
python scripts/tests/test_optimized_rag.py
python scripts/tests/test_final_rag.py
python scripts/tests/test_rag_enhancements.py
python scripts/tests/test_simple_stats.py

# Performance testing
python scripts/tests/performance_test.py
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
- `FinancialAnalysisAgent`: **[v1.4.0 NEW]** 专业财务分析系统，支持四表联合查询和深度财务分析

**Database Layer** (`database/`):
- `MySQLConnector`: Manages connections to MySQL for structured financial data
- `MilvusConnector`: Handles vector database operations for document embeddings

**Document Processing** (`rag/document_processor.py`):
- PDF download with three-stage retry strategy for cninfo.com.cn
- Text extraction and chunking with BGE-M3 embeddings
- Intelligent content filtering and metadata extraction

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
The system supports three main query types:
- `sql`: For numerical data, rankings, and structured queries
- `rag`: For document content, explanations, and qualitative analysis  
- `hybrid`: Automatically routes or combines both approaches

### Error Handling
- All agents return standardized response format with `success`, `error`, and result fields
- Input validation prevents empty/whitespace queries from causing errors  
- Modern LangChain error handling with try-catch around `invoke()` calls
- Milvus collections are automatically loaded if needed
- PDF downloads use three-stage retry with session management

### Performance Considerations
- SQL queries: 5-30 seconds depending on complexity
- RAG queries: 3-15 seconds with vector optimization
- Hybrid queries: 10-45 seconds with parallel processing
- System supports 50+ concurrent users

### Recent Updates

#### v1.4.0 - Phase 1 深度财务分析系统 (2025-06-22)

**FinancialAnalysisAgent 核心功能** ✅:
- **四表联合分析**: 利润表(83字段) + 资产负债表(161字段) + 现金流量表(73字段) + 财务指标(143字段)
- **财务健康度评分**: 基于盈利能力、偿债能力、运营能力、成长能力四维度的智能评分系统(AAA-CCC评级)
- **杜邦分析功能**: ROE分解分析(净利率×资产周转率×权益乘数)，支持多期趋势分析
- **现金流质量分析**: 现金含量比率计算、稳定性评分、综合质量评级
- **多期财务对比**: 同比/环比增长率、趋势分析、波动性评估

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
- **SQL Agent集成**: 预处理"茅台最新股价"→"茅台2025-06-20股价"
- **RAG Agent集成**: 预处理"贵州茅台最新公告"→"贵州茅台2025-06-20公告"
- **Hybrid Agent支持**: 复合查询中的智能时间解析
- **缓存机制**: 1小时TTL缓存，避免重复数据库查询

**解析示例** ✅:
- "茅台最新股价" → 查询2025-06-20交易日数据
- "贵州茅台最新财务数据" → 查询20250331期最新报告
- "600519.SH最新公告" → 查询2025-06-20最新公告
- "比亚迪现在的股价如何" → 自动转换为最近交易日查询

**技术实现** ✅:
- 新增 `utils/date_intelligence.py` 智能日期解析模块
- 正则表达式模式匹配 + 股票代码识别
- SQLAlchemy参数化查询，防止SQL注入
- 统一错误处理和日志记录

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

### Testing Strategy
- Use the test-guide.md for comprehensive testing procedures
- API endpoints available at http://localhost:8000/docs
- Interactive testing via rag_query_interface.py
- Performance benchmarks in scripts/tests/

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
```

### Testing Protocol
1. Run `baseline_test.py` for quick functionality check
2. Run `comprehensive_verification.py` for full system validation
3. Check specific features with archived tests in `scripts/tests/`
4. Performance testing via dedicated scripts

The system is designed for production use with comprehensive error handling, logging, monitoring capabilities, and full LangChain modernization (v1.3.8).