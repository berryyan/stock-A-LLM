# 股票分析系统 (Stock Analysis System)

<div align="center">
  <h3>🚀 基于LangChain的智能股票分析系统</h3>
  <p>集成SQL查询、RAG检索、混合查询的一站式金融数据分析平台</p>
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![LangChain](https://img.shields.io/badge/LangChain-0.2.0-green.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)
</div>

## 📖 目录

- [功能特性](#-功能特性)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [使用指南](#-使用指南)
- [API文档](#-api文档)
- [项目结构](#-项目结构)
- [性能指标](#-性能指标)
- [开发指南](#-开发指南)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

## 🚀 功能特性

### 核心功能

#### 1. **SQL查询系统** 
- ✅ 实时股价查询和历史数据分析
- ✅ 涨跌幅排行和成交量统计
- ✅ 多股票对比和趋势分析
- ✅ 财务指标查询和计算
- ✅ 完整的中文自然语言支持

#### 2. **RAG查询系统**
- ✅ 95,662+份公告文档的语义搜索
- ✅ 财务报告深度内容分析
- ✅ 支持上下文理解的智能问答
- ✅ 多公司横向对比分析
- ✅ BGE-M3模型提供精准语义理解

#### 3. **混合查询系统**
- ✅ 智能判断查询意图并自动路由
- ✅ SQL和RAG结果智能整合
- ✅ 提供综合性的分析报告
- ✅ 支持复杂的多维度查询

#### 4. **文档处理系统**
- ✅ 三阶段智能PDF下载策略（解决巨潮网特殊问题）
- ✅ 100%的PDF下载成功率
- ✅ 智能文本提取和分块
- ✅ 批量处理和进度管理

### 技术亮点

- 🔥 **LangChain框架**：构建强大的AI应用
- 🔥 **向量数据库**：Milvus实现高效语义搜索
- 🔥 **双数据库架构**：MySQL结构化数据 + Milvus非结构化数据
- 🔥 **GPU加速**：支持CUDA加速的向量计算
- 🔥 **生产级稳定性**：完整的错误处理和日志系统

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户界面层                           │
│                  (API / CLI / Web)                      │
├─────────────────────────────────────────────────────────┤
│                     API服务层                           │
│                   (FastAPI)                             │
├─────────────────────────────────────────────────────────┤
│                    智能代理层                           │
│     ┌──────────┬───────────┬──────────────┐           │
│     │ SQL Agent│ RAG Agent │ Hybrid Agent │           │
│     └──────────┴───────────┴──────────────┘           │
├─────────────────────────────────────────────────────────┤
│                    模型层                               │
│     ┌─────────────┬──────────────────────┐            │
│     │ LLM (DeepSeek)│ Embedding (BGE-M3) │            │
│     └─────────────┴──────────────────────┘            │
├─────────────────────────────────────────────────────────┤
│                   数据存储层                            │
│     ┌──────────────┬────────────────────┐             │
│     │    MySQL     │      Milvus        │             │
│     │ (结构化数据) │  (向量数据)        │             │
│     └──────────────┴────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## 🔧 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Milvus 2.0+
- CUDA 11.0+ (可选，用于GPU加速)
- 16GB+ RAM
- 50GB+ 存储空间

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/YOUR_USERNAME/stock-analysis-system.git
cd stock-analysis-system
```

#### 2. 创建虚拟环境
```bash
python -m venv stock_analysis_env
# Windows
stock_analysis_env\Scripts\activate
# Linux/Mac
source stock_analysis_env/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接和API密钥
```

#### 5. 初始化数据库
```bash
# 确保MySQL和Milvus服务已启动
python scripts/setup/init_database.py
```

#### 6. 启动服务
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

## 📖 使用指南

### SQL查询示例

```python
# 查询实时股价
POST /api/query
{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
}

# 查询涨跌幅排行
{
    "question": "今天涨幅最大的10只股票",
    "query_type": "sql"
}

# 历史数据分析
{
    "question": "贵州茅台最近一个月的平均成交量",
    "query_type": "sql"
}
```

### RAG查询示例

```python
# 查询财务数据
POST /api/query
{
    "question": "贵州茅台2024年第一季度的营收情况",
    "query_type": "rag"
}

# 分析公司战略
{
    "question": "分析茅台的高端化战略",
    "query_type": "rag"
}

# 行业对比
{
    "question": "比较茅台和五粮液的毛利率",
    "query_type": "rag"
}
```

### 混合查询示例

```python
# 综合分析
POST /api/query
{
    "question": "分析贵州茅台的财务状况和股价表现",
    "query_type": "hybrid"
}

# 投资建议
{
    "question": "基于财务数据和市场表现，评估茅台的投资价值",
    "query_type": "hybrid"
}
```

### 命令行工具

```bash
# RAG交互查询
python rag_query_interface.py

# 批量处理公告
python batch_process_manager.py

# 系统健康检查
python scripts/utils/system_check.py

# 数据库分析
python scripts/analysis/db_analyzer.py
```

## 📚 API文档

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 欢迎页面 |
| `/health` | GET | 健康检查 |
| `/api/query` | POST | 执行查询 |
| `/api/status` | GET | 系统状态 |
| `/docs` | GET | Swagger文档 |
| `/redoc` | GET | ReDoc文档 |

### 查询请求格式

```json
{
    "question": "查询问题",
    "query_type": "sql|rag|hybrid",
    "filters": {
        "stock_code": "600519.SH",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    }
}
```

### 响应格式

```json
{
    "status": "success",
    "query_type": "sql",
    "question": "原始问题",
    "answer": "查询结果",
    "metadata": {
        "processing_time": 1.23,
        "data_sources": ["MySQL"],
        "confidence": 0.95
    }
}
```

## 📁 项目结构

```
stock_analysis_system/
├── config/                 # 系统配置
├── database/              # 数据库连接器
├── rag/                   # RAG系统实现
├── agents/                # 智能代理
├── models/                # 模型配置
├── api/                   # API服务
├── utils/                 # 工具函数
├── scripts/               # 独立脚本工具
│   ├── analysis/          # 数据分析工具
│   ├── maintenance/       # 系统维护脚本
│   ├── tools/            # 通用工具
│   ├── tests/            # 测试脚本
│   └── debugging/        # 调试工具
├── docs/                  # 项目文档
├── tests/                 # 单元测试
└── data/                 # 数据存储（Git忽略）
```

详细的目录结构说明请查看 [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)

## 📊 性能指标

### 查询性能
- **SQL查询**: 5-30秒（视复杂度而定）
- **RAG查询**: 3-15秒（向量搜索优化）
- **混合查询**: 10-45秒（并行处理）

### 处理能力
- **PDF处理速度**: 30秒/文档
- **向量化速度**: 100文档/分钟
- **并发支持**: 50+用户

### 数据规模
- **MySQL记录**: 2800万+条
- **向量文档**: 95,662+个
- **处理公司**: 500+家
- **PDF文档**: 5000+份

## 🛠️ 开发指南

### 环境设置

1. **安装开发依赖**
```bash
pip install -r requirements-dev.txt
```

2. **配置pre-commit**
```bash
pre-commit install
```

3. **运行测试**
```bash
pytest tests/
```

### 代码规范

- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 编写docstring文档
- 添加类型注解

### 添加新功能

1. 在相应模块目录创建新文件
2. 编写单元测试
3. 更新文档
4. 提交Pull Request

## ❓ 常见问题

### Q1: 如何处理PDF下载失败？
A: 系统已实现三阶段下载策略，会自动处理大小写和session问题。如仍有问题，检查`document_processor.log`。

### Q2: Milvus连接失败怎么办？
A: 确保Milvus服务运行正常，检查端口19530是否开放，运行`scripts/tools/load_milvus_collection.py`测试连接。

### Q3: 查询速度慢如何优化？
A: 可以通过以下方式优化：
- 启用Redis缓存
- 优化SQL查询语句
- 增加系统内存
- 使用GPU加速

### Q4: 如何添加新的数据源？
A: 在`database/`目录添加新的连接器，在`agents/`目录添加相应的Agent。

## 📝 更新日志

### v1.3 (2025-06-15)
- ✅ 完成项目结构重组
- ✅ 整理了39个工具脚本
- ✅ 归档了29个修复脚本
- ✅ 创建完整的文档体系

### v1.2 (2025-06-14)
- ✅ 解决PDF下载特殊问题
- ✅ 实现三阶段下载策略
- ✅ 优化日志系统

### v1.1 (2025-06-08)
- ✅ 修复Milvus集合加载问题
- ✅ 完成混合查询系统
- ✅ 系统全功能可用

### v1.0 (2025-06-07)
- ✅ 初始版本发布
- ✅ 实现基础RAG功能
- ✅ 完成SQL查询系统

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 贡献者公约

- 遵守代码规范
- 编写测试用例
- 更新相关文档
- 保持commit信息清晰

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 作者与致谢

### 作者
- [Your Name](https://github.com/yourusername)

### 致谢
- 🙏 [LangChain](https://github.com/langchain-ai/langchain) - 优秀的LLM应用框架
- 🙏 [Tushare](https://tushare.pro/) - 金融数据接口
- 🙏 [DeepSeek](https://www.deepseek.com/) - 强大的中文LLM
- 🙏 [BGE-M3](https://huggingface.co/BAAI/bge-m3) - 优秀的中文嵌入模型
- 🙏 所有贡献者和使用者

## 📞 联系方式

- 📧 Email: your.email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/stock-analysis-system/issues)
- 📖 Wiki: [项目Wiki](https://github.com/YOUR_USERNAME/stock-analysis-system/wiki)

---

<div align="center">
  <p>如果这个项目对你有帮助，请给个⭐️Star支持一下！</p>
  <p>Made with ❤️ by the Stock Analysis Team</p>
</div>