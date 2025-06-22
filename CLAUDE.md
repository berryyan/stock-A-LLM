# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Stock Analysis System** built with Python that provides intelligent stock analysis through SQL queries, RAG (Retrieval-Augmented Generation), and hybrid query capabilities. The system integrates LangChain, FastAPI, MySQL, and Milvus to deliver comprehensive financial data analysis and document retrieval.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
# Windows:
stock_analysis_env\Scripts\activate
# Linux/Mac:
source stock_analysis_env/bin/activate

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

# Run comprehensive verification
python comprehensive_verification.py

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

**Agent System** (`agents/`):
- `HybridAgent`: Smart query router that automatically determines whether to use SQL or RAG
- `SQLAgent`: Handles structured data queries against MySQL database
- `RAGAgent`: Manages document retrieval and semantic search using Milvus

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
- Milvus collections are automatically loaded if needed
- PDF downloads use three-stage retry with session management

### Performance Considerations
- SQL queries: 5-30 seconds depending on complexity
- RAG queries: 3-15 seconds with vector optimization
- Hybrid queries: 10-45 seconds with parallel processing
- System supports 50+ concurrent users

### Recent Updates (2025-06-22)
- ✅ Added empty query validation to all agents (RAG, SQL, Hybrid)
- ✅ Updated deprecated LangChain LLMChain usage to new runnable chains
- ✅ Removed StdOutCallbackHandler to eliminate errors
- ✅ All agents now use modern LangChain patterns with `|` operator
- ✅ Improved error handling and input validation

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

The system is designed for production use with comprehensive error handling, logging, and monitoring capabilities.