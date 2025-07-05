# 模块化系统测试指南

## 概述
本指南说明如何在Windows环境中测试v2.2.0模块化架构的股票分析系统。

## 前置条件
1. Windows操作系统
2. Python 3.8+ 已安装
3. 项目依赖已安装（`pip install -r requirements.txt`）
4. MySQL和Milvus数据库服务正常运行

## 测试步骤

### 1. 启动API服务（模块化版本）

在Windows命令提示符或PowerShell中：

```bash
# 进入项目目录
cd E:\PycharmProjects\stock_analysis_system

# 运行启动脚本
start_modular_api.bat
```

或者手动运行：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动API服务
python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001
```

服务启动后：
- API地址: http://localhost:8001
- API文档: http://localhost:8001/docs
- 网页界面: http://localhost:8001

### 2. 运行测试脚本

在另一个命令窗口中：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行测试脚本
python test_modular_api.py
```

### 3. 测试内容

#### 3.1 健康检查
- 验证服务是否正常启动
- 检查各个组件状态（SQL Agent、RAG Agent、Financial Agent、Money Flow Agent）

#### 3.2 查询接口测试
测试以下查询类型：
- SQL查询：股价、市值等结构化数据
- RAG查询：公告内容等文档检索
- 财务分析：财务健康度评分
- 资金流向：主力资金分析

#### 3.3 专业分析接口
- 财务分析接口：`/financial-analysis`
- 资金流向分析接口：`/money-flow-analysis`

### 4. 通过网页界面测试

1. 打开浏览器访问 http://localhost:8001
2. 在聊天界面输入查询，例如：
   - "贵州茅台的最新股价"
   - "比较贵州茅台和五粮液的市值"
   - "分析贵州茅台的财务健康度"
   - "贵州茅台的主力资金流向"

### 5. 查看API文档

访问 http://localhost:8001/docs 查看完整的API文档，包括：
- 所有接口的详细说明
- 请求/响应示例
- 在线测试功能

## 模块化架构优势

### 1. 代码复用
- 统一的参数提取器（ParameterExtractor）
- 统一的查询验证器（QueryValidator）
- 统一的结果格式化器（ResultFormatter）
- 统一的错误处理器（ErrorHandler）

### 2. 性能提升
- 参数提取缓存
- 减少重复验证
- 快速错误返回

### 3. 维护性改善
- 统一的错误处理和用户提示
- 模块化的代码结构
- 易于扩展和修改

## 常见问题

### Q1: 服务启动失败
**解决方案**：
1. 检查端口8001是否被占用
2. 确保虚拟环境已激活
3. 检查数据库连接配置（.env文件）

### Q2: 查询超时
**解决方案**：
1. 检查数据库服务是否正常
2. 确认网络连接正常
3. 查看日志文件了解详细错误

### Q3: 模块导入错误
**解决方案**：
1. 确保在项目根目录运行
2. 检查Python路径设置
3. 重新安装依赖：`pip install -r requirements.txt`

## 日志查看

日志文件位置：
- API日志：`logs/api_modular.log`
- 各Agent日志：`logs/sql_agent.log`、`logs/rag_agent.log`等

## 下一步计划

1. **生产环境验证**：在测试环境运行1周
2. **性能优化**：基于测试结果进行优化
3. **新功能开发**：
   - 技术指标查询
   - 4个新Agent（Rank、ANNS、QA、概念股）
4. **文档完善**：
   - API迁移指南
   - 最佳实践文档

---
更新时间：2025-07-05
版本：v2.2.0