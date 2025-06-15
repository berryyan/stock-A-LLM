# 股票分析系统 - 目录结构说明

本文档详细说明了项目的目录结构和各个文件的用途。

## 📁 根目录结构

```
stock_analysis_system/
├── config/                 # 系统配置
├── database/              # 数据库连接器
├── rag/                   # RAG（检索增强生成）系统
├── agents/                # 智能代理
├── models/                # 模型和嵌入
├── api/                   # API服务
├── utils/                 # 工具函数
├── scripts/               # 独立脚本工具
├── archive/               # 归档的历史文件
├── docs/                  # 项目文档
├── data/                  # 数据存储（Git忽略）
├── tests/                 # 单元测试（待完善）
├── logs/                  # 日志文件（Git忽略）
└── [项目文件]            # 配置和文档文件
```

## 📂 核心模块详解

### 🔧 config/ - 配置管理
```
config/
├── __init__.py
└── settings.py            # 环境变量和系统配置
```
- 管理所有系统配置
- 从.env文件加载环境变量
- 定义数据库连接、API密钥等

### 🗄️ database/ - 数据库连接
```
database/
├── __init__.py
├── mysql_connector.py     # MySQL连接和查询
└── milvus_connector.py    # Milvus向量数据库连接
```
- MySQL：存储结构化数据（股价、财务等）
- Milvus：存储文档向量（公告、报告等）

### 📚 rag/ - RAG系统
```
rag/
├── __init__.py
├── document_processor.py  # 文档处理（PDF下载、解析、分块）
└── vector_store.py       # 向量存储管理（计划中）
```
- 实现三阶段PDF下载策略
- 文本提取和智能分块
- 向量化和存储

### 🤖 agents/ - 智能代理
```
agents/
├── __init__.py
├── sql_agent.py          # SQL查询代理
├── rag_agent.py          # RAG查询代理
└── hybrid_agent.py       # 混合查询代理
```
- SQL Agent：处理结构化数据查询
- RAG Agent：处理文档内容查询
- Hybrid Agent：智能路由和整合

### 🧠 models/ - 模型配置
```
models/
├── __init__.py
├── embedding_model.py    # BGE-M3嵌入模型
├── llm_models.py        # LLM配置（DeepSeek等）
└── bge-m3/              # BGE-M3模型文件
```
- 嵌入模型：文本向量化
- LLM模型：自然语言理解和生成

### 🌐 api/ - API服务
```
api/
├── __init__.py
└── main.py              # FastAPI主程序
```
- RESTful API接口
- Swagger文档
- 健康检查端点

### 🛠️ utils/ - 工具函数
```
utils/
├── __init__.py
├── logger.py                    # 日志系统
├── helpers.py                   # 辅助函数
├── performance_tracker.py       # 性能跟踪
└── auto_performance_logger.py   # 自动性能日志
```

## 📜 scripts/ - 独立脚本工具

### 📊 scripts/analysis/ - 数据分析
```
scripts/analysis/
├── db_analyzer.py               # 数据库表结构分析
└── announcement_analyzer.py     # 公告标题模式分析
```

### 🔧 scripts/maintenance/ - 系统维护
```
scripts/maintenance/
├── batch_process_manager.py     # 批量处理管理
└── milvus_dedup_script_v2.py   # 向量数据去重
```

### 🔨 scripts/tools/ - 通用工具
```
scripts/tools/
├── load_milvus_collection.py    # Milvus集合加载
└── [其他工具脚本]
```

### 🧪 scripts/tests/ - 测试脚本
```
scripts/tests/
├── test_api.py                  # API测试
├── test_agents.py               # Agent测试
└── [其他测试]
```

### 🐛 scripts/debugging/ - 调试工具
```
scripts/debugging/
├── diagnose_agent.py            # Agent问题诊断
├── check_sql_syntax.py          # SQL语法检查
└── [其他调试工具]
```

### ⚙️ scripts/utils/ - 实用工具
```
scripts/utils/
├── system_check.py              # 系统健康检查
└── verify_api.py                # API验证
```

### 📦 scripts/setup/ - 设置脚本
```
scripts/setup/
└── install_dependencies.py      # 依赖安装
```

## 🗃️ archive/ - 归档目录

```
archive/
├── fixes/                       # 一次性修复脚本
│   ├── sql_agent_fixes/        # SQL Agent相关修复
│   ├── api_response_fixes/     # API响应格式修复
│   ├── timeout_fixes/          # 超时问题修复
│   ├── import_fixes/           # 导入问题修复
│   └── enum_fixes/             # 枚举类型修复
└── old_versions/               # 旧版本文件
    └── smart_processor_v1-v5/  # 处理器历史版本
```

## 📖 docs/ - 文档目录

```
docs/
├── project_status/             # 项目状态历史
│   ├── project_status_20250607.md
│   ├── project_status_20250608.md
│   ├── project_status_20250614.md
│   └── project_status_20250615.md
├── examples/                   # 使用示例
├── API.md                      # API文档
└── deployment.md               # 部署指南
```

## 💾 data/ - 数据目录（Git忽略）

```
data/
├── pdfs/                       # PDF文件存储
│   └── cache/                  # 下载的PDF缓存
├── milvus/                     # Milvus数据
├── logs/                       # 运行日志
└── processing_progress.json    # 处理进度
```

## 📋 项目根目录文件

### 核心脚本
- `smart_processor_v5_1.py` - 智能文档处理器（最新版）
- `batch_process_manager.py` - 批量处理管理器
- `milvus_dedup_script_v2.py` - Milvus去重工具
- `rag_query_interface.py` - RAG查询交互界面
- `project_git_prepare.py` - Git准备工具
- `backup_project.py` - 项目备份工具
- `analyze_scripts.py` - 脚本分析工具

### 配置文件
- `.env` - 环境变量（Git忽略）
- `.env.example` - 环境变量示例
- `requirements.txt` - Python依赖
- `.gitignore` - Git忽略规则
- `setup.py` - 包安装配置

### 文档文件
- `README.md` - 项目说明
- `LICENSE` - 许可证
- `DIRECTORY_STRUCTURE.md` - 本文档

## 🔑 重要说明

1. **Git忽略的目录**：
   - `data/` - 包含大量数据文件
   - `logs/` - 运行时日志
   - `stock_analysis_env/` - Python虚拟环境
   - `__pycache__/` - Python缓存
   - `*.log` - 所有日志文件

2. **核心功能入口**：
   - API服务：`python -m uvicorn api.main:app`
   - 批量处理：`python batch_process_manager.py`
   - RAG查询：`python rag_query_interface.py`

3. **开发流程**：
   - 新功能开发在相应模块目录
   - 工具脚本放在scripts/相应子目录
   - 测试脚本统一放在scripts/tests/
   - 文档更新在docs/目录

---

最后更新：2025-06-15