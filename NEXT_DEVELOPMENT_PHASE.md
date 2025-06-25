# 下一步开发计划 - Stock Analysis System

**文档版本**: v3.1  
**更新日期**: 2025-06-26  
**当前版本**: v1.4.3-stable (准备合并到主分支)  
**当前分支**: dev-phase2-technical-analysis → main → dev-react-frontend-v2  
**重大决策**: 采用React前端驱动的测试和开发策略

## 📋 目录

1. [Phase 1: React MVP + 核心功能测试](#phase-1-react-mvp-核心功能测试)
2. [Phase 2: 高优先级后端优化](#phase-2-高优先级后端优化)
3. [Phase 3: 前端增强 + 技术分析](#phase-3-前端增强-技术分析)
4. [Git版本管理策略](#git版本管理策略)
5. [React前端开发详细指南](#react前端开发详细指南)
6. [测试策略规范](#测试策略规范)
7. [已完成功能总结](#已完成功能总结)

## Phase 1: React MVP + 核心功能测试（第1周）

### Day 1-3: React基础框架搭建
**目标**: 快速实现与HTML版本功能对等的React界面

#### 必须完成的任务：
1. **项目初始化**
   ```bash
   # 在新分支 dev-react-frontend-v2 上执行
   npm create vite@latest stock-analysis-frontend -- --template react-ts
   cd stock-analysis-frontend
   npm install
   
   # 核心依赖安装
   npm install react-markdown remark-gfm axios
   npm install -D @types/react @types/react-dom
   ```

2. **基础组件开发**
   - `src/components/ChatInterface.tsx` - 主聊天界面
   - `src/components/MessageList.tsx` - 消息列表展示
   - `src/components/InputBox.tsx` - 多行输入框
   - `src/components/SimpleMarkdownRenderer.tsx` - 基础Markdown渲染
   - `src/services/api.ts` - API调用封装

3. **核心功能实现**
   - 与后端API通信 (http://localhost:8000)
   - 消息发送和接收
   - 基础Markdown渲染（标题、列表、代码块、表格）
   - 错误处理和loading状态

4. **样式要求**
   - 模仿Claude.ai的基础布局
   - 响应式设计
   - 清晰的视觉层级

### Day 4-7: 使用新React界面进行完整测试

#### Day 4: SQL查询功能测试
- **测试内容**: 
  - 贵州茅台最新股价
  - A股市值排名前10
  - 涨跌幅排行榜
  - 历史数据查询
- **重点关注**: 数据格式化显示、表格渲染、响应时间

#### Day 5: RAG和财务分析测试
- **测试内容**:
  - 公告文档检索
  - 财务健康度分析（AAA-CCC评级）
  - 杜邦分析（ROE分解）
  - 现金流质量分析
  - 多期财务对比
- **重点关注**: 长文本显示、Markdown格式化、数据准确性

#### Day 6: 资金流向和混合查询测试
- **测试内容**:
  - 30天资金流向分析
  - 主力资金监控
  - 混合查询路由
  - 复杂查询场景
- **重点关注**: 图表数据展示需求、性能表现

#### Day 7: 问题汇总和修复
- 整理测试发现的所有问题
- 区分前端问题和后端问题
- 紧急修复阻塞性bug
- 更新测试报告

## Phase 2: 高优先级后端优化（第2-3周）

### Week 2: 数据库Schema中文映射系统 ❌
**问题现状**:
- SQL Agent每次查询都需要重新查询数据库表结构
- Hybrid Agent无法准确判断查询是否需要SQL
- 消耗额外的token和查询时间

**具体实现计划**:
1. **创建映射配置文件** `config/db_schema_mapping.py`
   ```python
   DB_SCHEMA = {
       "daily": {
           "description": "股票日线行情数据",
           "fields": {
               "ts_code": {"cn": "股票代码", "type": "str"},
               "trade_date": {"cn": "交易日期", "type": "date"},
               "open": {"cn": "开盘价", "type": "float"},
               "close": {"cn": "收盘价", "type": "float"},
               # ... 完整字段映射
           }
       },
       # ... 其他表映射
   }
   ```

2. **实现缓存管理器** `utils/schema_cache_manager.py`
   - 启动时加载Schema到内存
   - 提供快速查询接口
   - 定期更新机制（每24小时）

3. **集成到Hybrid Agent**
   - 修改路由判断逻辑
   - 基于Schema快速判断查询类型
   - 减少LLM调用次数

**预期效果**:
- 减少50%的数据库结构查询
- 提升路由准确率至95%以上
- 响应速度提升30%

### Week 3: RAG查询智能降级机制 ❌
**具体实现计划**:
1. **创建降级处理器** `rag/fallback_handler.py`
   - 检测空结果、错误、超时
   - 实现多级降级策略
   - 记录失败模式

2. **降级策略**:
   - Level 1: 扩大搜索范围（降低相似度阈值）
   - Level 2: 关键词分词重组
   - Level 3: 返回相关推荐
   - Level 4: 引导用户重新表述

3. **失败日志分析**
   - 创建失败查询数据库
   - 定期分析失败原因
   - 优化RAG索引策略

## Phase 3: 前端增强 + 技术分析（第4-6周）

### Week 4: React前端完善
**从SimpleMarkdownRenderer升级到完整版**:

1. **安装额外依赖**
   ```bash
   # 代码高亮和数学公式
   npm install react-syntax-highlighter remark-math rehype-katex
   npm install -D @types/react-syntax-highlighter
   
   # 数据可视化
   npm install recharts
   ```

2. **升级组件**
   - `FullMarkdownRenderer.tsx` - 完整Markdown渲染（代码高亮、复制按钮、KaTeX）
   - `DocumentViewer.tsx` - 右侧文档查看区
   - `StockChart.tsx` - K线图组件
   - `MoneyFlowChart.tsx` - 资金流向图
   - `Sidebar.tsx` - 左侧对话历史

3. **高级功能**
   - 长代码自动移到右侧显示
   - 表格数据增强（排序、筛选）
   - 股票代码特殊样式
   - 深色/浅色主题切换

### Week 5-6: Phase 2技术分析系统

#### Week 5: 技术指标计算模块
**创建** `utils/technical_indicators.py`:
```python
class TechnicalIndicators:
    def calculate_ma(self, prices, period): pass
    def calculate_ema(self, prices, period): pass
    def calculate_macd(self, prices): pass
    def calculate_rsi(self, prices, period=14): pass
    def calculate_bollinger_bands(self, prices, period=20): pass
```

#### Week 6: TechnicalAnalysisAgent开发
**创建** `agents/technical_agent.py`:
- 趋势分析（上升/下降/横盘）
- K线形态识别
- 支撑阻力位计算
- 买卖信号生成

**API集成**:
```python
# 新增端点
POST /technical-analysis
{
    "ts_code": "600519.SH",
    "period": 30,
    "indicators": ["MA", "MACD", "RSI"]
}

```

## Git版本管理策略

### 当前状态
- **当前分支**: dev-phase2-technical-analysis
- **目标**: 合并到main，创建新的React开发分支

### 执行步骤

#### Step 1: 创建稳定版本标签
```bash
# 为当前版本创建标签
git tag -a v1.4.3-stable -m "稳定版本：财务分析增强+WebSocket恢复+股票映射器"
git push origin v1.4.3-stable
```

#### Step 2: 合并到主分支
```bash
# 确保所有更改已提交
git add .
git commit -m "docs: 更新开发计划v3.1，整合React前端改版方案"

# 切换到主分支并合并
git checkout main
git merge dev-phase2-technical-analysis -m "feat: 合并v1.4.3稳定版本

- 财务分析功能增强（日志优化、北交所限制）  
- 多期财务对比修复
- 开发计划更新（React前端改版）"

git push origin main
```

#### Step 3: 创建新的开发分支
```bash
# 创建React前端开发分支
git checkout -b dev-react-frontend-v2
git push -u origin dev-react-frontend-v2
```

### 分支管理策略
```
main (主分支)
  ├── v1.4.3-stable (标签)
  └── dev-react-frontend-v2 (新开发分支)
      ├── 前端项目初始化
      ├── 后端优化
      └── 技术分析系统
```

## React前端开发详细指南

### 快速启动指南（重启Claude Code后）

#### 1. 环境准备
```bash
# 切换到React开发分支
git checkout dev-react-frontend-v2

# 如果前端项目已创建
cd stock-analysis-frontend
npm install
npm run dev

# 如果需要新建项目
npm create vite@latest stock-analysis-frontend -- --template react-ts
```

#### 2. 项目结构
```
stock-analysis-frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── InputBox.tsx
│   │   ├── SimpleMarkdownRenderer.tsx
│   │   └── (后续组件...)
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── styles/
│   │   └── global.css
│   └── App.tsx
├── package.json
└── vite.config.ts
```

#### 3. API接口定义
```typescript
// src/types/index.ts
interface QueryRequest {
  question: string;
  query_type?: 'sql' | 'rag' | 'hybrid' | 'financial';
  top_k?: number;
}

interface QueryResponse {
  success: boolean;
  answer?: string;
  error?: string;
  query_type?: string;
  sources?: {
    sql_data?: any[];
    documents?: any[];
    table_data?: any[];
    chart_data?: any;
  };
}
```

#### 4. 开发顺序提醒
1. **Day 1**: 先实现基础消息发送和显示
2. **Day 2**: 添加SimpleMarkdownRenderer
3. **Day 3**: 完善错误处理和加载状态
4. **Day 4-7**: 使用新界面进行系统测试

### 测试环境配置

#### 后端API启动（Windows）
```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动API服务
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发服务器
```bash
cd stock-analysis-frontend
npm run dev
# 访问 http://localhost:5173
```

#### 测试数据准备
```javascript
// 测试查询示例
const testQueries = [
  "贵州茅台最新股价",
  "分析茅台的财务健康度", 
  "茅台最近30天资金流向",
  "贵州茅台最新公告"
];
```

## 测试策略规范

### React前端测试重点
1. **功能完整性**: 确保所有API端点都能正确调用
2. **错误处理**: 网络错误、API错误的友好提示
3. **数据展示**: 表格、长文本、Markdown格式
4. **性能表现**: 大数据量时的渲染性能
5. **用户体验**: 加载状态、交互反馈

### 问题记录模板
```markdown
## 问题 #1
- **类型**: 前端/后端/集成
- **描述**: 具体问题描述
- **复现步骤**: 1. 2. 3.
- **期望结果**: 
- **实际结果**:
- **优先级**: P0/P1/P2
- **解决方案**:
```

## 已完成功能总结（v1.4.3-stable）

### 核心查询系统 ✅
- SQL查询：股价、市值、财务指标
- RAG查询：文档语义搜索（95,662+向量）
- 混合查询：智能路由和组合分析

### 专业分析功能 ✅
- 财务健康度评分（AAA-CCC评级）
- 杜邦分析（ROE三因素分解）
- 现金流质量分析（A-D级评估）
- 多期财务对比（8期趋势分析）
- 资金流向监控（30天主力资金）

### 系统特性 ✅
- 智能日期解析v2.0
- 股票代码映射器
- WebSocket实时通信
- 错误处理机制
- Windows兼容性100%

### 技术栈
- **后端**: FastAPI + LangChain + MySQL + Milvus
- **模型**: DeepSeek Chat + BGE-M3 Embedding  
- **前端**: HTML/JS (当前) → React/TypeScript (计划)
- **部署**: Windows/Linux兼容

---

**重要提醒**: 
1. 开始React开发前先完成Git版本管理
2. 严格按照3天完成MVP的时间要求
3. 测试过程中同步修复发现的问题
4. 保持文档实时更新
python check_available_dates.py
```

#### 2. 需要用户在Windows执行的测试
```bash
# Windows Anaconda环境启动API
(stock_analysis_env) python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 综合功能测试（需要API运行）
(stock_analysis_env) python baseline_test.py
(stock_analysis_env) python comprehensive_verification.py
(stock_analysis_env) python test_financial_agent.py
(stock_analysis_env) python test_money_flow_analysis.py
```

#### 3. 网页版测试（需要用户手动测试）
- 访问 http://localhost:8000
- 按照 docs/testing/WEB_FUNCTIONAL_TEST_GUIDE.md 执行测试
- API文档测试：http://localhost:8000/docs

### Bash超时配置策略
```python
# 短时间命令（< 30秒）
bash_result = Bash(command="git status")

# 中等时间命令（< 2分钟）
bash_result = Bash(command="python quick_test.py", timeout=120000)

# 长时间命令（< 10分钟）
bash_result = Bash(command="python comprehensive_test.py", timeout=600000)
```

## 测试策略规范

### 三层测试体系

#### 1. 单元测试（Claude Code执行）
- 数据库连接验证
- 工具函数测试
- 模块导入检查
- **执行方式**: Claude Code直接运行

#### 2. 集成测试（Windows API环境）
- API端点测试
- Agent功能验证
- 端到端流程测试
- **执行方式**: 提示用户在Windows运行

#### 3. 用户验收测试（网页界面）
- 功能完整性验证
- 用户体验测试
- 性能基准验证
- **执行方式**: 提示用户手动测试

### 测试提示模板
```python
# Claude Code使用示例
if test_type == "integration":
    print("⚠️ 此测试需要API运行")
    print("请在Windows环境执行：")
    print("1. 启动API: python -m uvicorn api.main:app --reload")
    print("2. 运行测试: python {test_file}")
elif test_type == "web":
    print("🌐 此为网页版测试")
    print("请打开浏览器访问 http://localhost:8000")
    print("按照测试指南执行手动测试")
```

## Phase 2 技术面分析系统

### 开发概述
- **目标**: 构建专业的技术面分析系统，与已完成的基本面分析形成互补
- **预计时间**: 3周
- **优先级**: 最高

### Week 1: 技术指标计算模块 (utils/technical_indicators.py)

#### 核心指标实现
1. **趋势指标**
   - SMA/EMA（简单/指数移动平均）
   - MACD（平滑异同移动平均线）
   - 布林带（Bollinger Bands）

2. **动量指标**
   - RSI（相对强弱指标）
   - KDJ（随机指标）
   - ROC（变动率）

3. **成交量指标**
   - OBV（能量潮）
   - 成交量加权平均价（VWAP）
   - 量比指标

4. **波动率指标**
   - ATR（真实波幅）
   - 标准差
   - 历史波动率

### Week 2: TechnicalAnalysisAgent开发

#### 核心功能
1. **趋势分析**
   - 主趋势判断（上升/下降/横盘）
   - 趋势强度评估
   - 趋势转折点识别

2. **形态识别**
   - 经典K线形态（锤子线、十字星等）
   - 图表形态（头肩顶、双底等）
   - 突破形态识别

3. **支撑阻力分析**
   - 动态支撑/阻力位计算
   - 重要价格区间标记
   - 突破概率评估

4. **交易信号生成**
   - 买入/卖出信号
   - 信号强度评级
   - 风险提示

### Week 3: API集成和测试

#### 集成任务
1. **API端点开发**
   ```python
   POST /technical-analysis
   {
       "ts_code": "600519.SH",
       "analysis_type": "comprehensive",
       "period": 30
   }
   ```

2. **Hybrid Agent集成**
   - 添加TECHNICAL查询类型
   - 智能路由到TechnicalAgent

3. **前端界面更新**
   - 添加技术分析快捷按钮
   - 图表展示支持（可选）

## 后续开发路线图

### Phase 3: 文档智能分析 (2-3周)
**目标**: 深度解读财报和公告内容
- 年报季报关键信息提取
- 主题投资机会发现（AI、新能源、生物医药）
- 政策影响分析
- 行业趋势识别
- 事件驱动分析

**新增组件**:
- DocumentAnalysisAgent
- ThemeDiscoveryEngine
- PolicyImpactAnalyzer

### Phase 4: 综合决策支持 (2-3周)
**目标**: 多维度投资决策系统
- 综合评分系统（基本面70% + 技术面20% + 消息面10%）
- 投资组合优化建议
- 风险分散策略
- 动态再平衡提醒
- 历史回测分析

**新增组件**:
- PortfolioAgent
- RiskAnalysisEngine
- BacktestingSystem

### Phase 5: 估值分析系统 (1-2周)
**目标**: 专业估值和选股
- PE/PB历史分位数
- PEG估值合理性
- DCF模型（可选）
- 相对估值分析
- 股息率分析

**新增组件**:
- ValuationAgent
- DividendAnalyzer

### 其他改进任务

#### 短期任务（1周内）
- [ ] 性能监控仪表板
- [ ] API文档完善
- [ ] 部署指南更新
- [ ] Claude Code使用最佳实践文档

#### 中长期任务
- [ ] Redis缓存层实现
- [ ] 更多查询模板
- [ ] 实时数据推送
- [ ] CI/CD流程集成
- [ ] 多语言支持（英文版）

## 已完成功能总结

### v1.4.2-final 功能清单 ✅

#### 核心查询系统
- **SQL查询**: 股价、市值、财务指标查询
- **RAG查询**: 文档语义搜索（95,662+向量）
- **混合查询**: 智能路由和组合分析

#### Phase 1: 深度财务分析 ✅
- **财务健康度评分**: AAA-CCC专业评级系统
- **杜邦分析**: ROE三因素分解
- **现金流质量**: A-D级质量评估
- **多期对比**: 同比环比趋势分析

#### Phase 2: 资金流向分析 ✅
- **主力资金监控**: 大单+超大单净流向
- **超大单行为识别**: 建仓/减仓/洗盘模式
- **四级资金分布**: 机构/大户/中户/散户
- **专业评估报告**: 流向强度和一致性评分

#### 智能日期解析 v2.0 ✅
- **自然语言识别**: "最新"、"最近"、"去年同期"
- **时间点vs时间段**: 精准区分查询意图
- **专业交易日计算**: 考虑节假日和停牌
- **多层缓存优化**: 1小时TTL缓存

