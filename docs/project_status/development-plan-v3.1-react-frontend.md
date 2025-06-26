# 股票分析系统开发计划 v3.1 - Claude.ai风格React前端改版

**版本**: v3.1  
**创建日期**: 2025-06-26  
**项目状态**: 开发中（dev-react-frontend-v2分支）

## 一、项目背景

当前系统(v1.4.3)已完成所有核心功能的开发，包括：
- ✅ Phase 1: 深度财务分析系统
- ✅ Phase 2: 资金流向分析系统
- ✅ 智能日期解析v2.0
- ✅ 股票代码智能映射
- ✅ WebSocket实时通信

但当前前端采用简单的HTML/JS实现，用户体验与现代Web应用存在差距。本次改版目标是创建一个完全模仿Claude.ai界面设计的React前端，提供专业级的用户体验。

## 二、核心目标

### 2.1 设计目标
- **界面风格**: 100%复刻Claude.ai的设计语言和交互逻辑
- **用户体验**: 流畅的对话式交互，智能的内容分发展示
- **技术架构**: React + TypeScript + Vite现代前端技术栈
- **开发模式**: WSL2+Windows双环境协同开发

### 2.2 功能目标
1. **完整的Markdown渲染**：代码高亮、表格美化、数学公式、引用块
2. **智能分屏显示**：对话区显示文字回答，文档区显示长代码/表格/图表
3. **流式响应**：逐字显示效果，打字光标动画
4. **数据可视化**：K线图、成交量图、资金流向图
5. **主题切换**：亮色/深色主题，响应式设计

## 三、开发计划详细

### Phase 0: 环境准备与备份（第1-2天）

#### Day 1: 环境备份
- [ ] WSL2 venv环境备份
  ```bash
  cd /mnt/e/PycharmProjects/stock_analysis_system
  pip freeze > requirements_backup_$(date +%Y%m%d).txt
  tar -czf venv_backup_$(date +%Y%m%d).tar.gz venv/
  ```
- [ ] Windows Anaconda环境备份
  ```bash
  conda env export > environment_backup_$(date +%Y%m%d).yml
  conda list > conda_packages_$(date +%Y%m%d).txt
  ```
- [ ] 创建环境文档记录当前配置

#### Day 2: 前端环境搭建
- [ ] Windows端：
  - 使用Anaconda创建node环境
  - 安装Node.js 18.x LTS
  - 安装VS Code及相关插件
- [ ] WSL2端：
  - 安装nvm (Node Version Manager)
  - 通过nvm安装Node.js 18.x
  - 配置npm镜像源
- [ ] 编写环境同步脚本

### Phase 1: Claude.ai风格React MVP（第3-7天）

#### Day 3-4: 基础架构搭建
- [ ] React项目初始化
  ```bash
  npm create vite@latest stock-analysis-frontend -- --template react-ts
  cd stock-analysis-frontend
  npm install
  ```
- [ ] 安装核心依赖
  ```bash
  npm install react-markdown remark-gfm rehype-katex remark-math
  npm install react-syntax-highlighter @types/react-syntax-highlighter
  npm install axios react-router-dom
  npm install -D tailwindcss postcss autoprefixer
  ```
- [ ] 项目结构设计
  ```
  src/
  ├── components/
  │   ├── layout/
  │   │   ├── Sidebar.tsx
  │   │   ├── MainContent.tsx
  │   │   └── Header.tsx
  │   ├── chat/
  │   │   ├── ChatArea.tsx
  │   │   ├── MessageList.tsx
  │   │   ├── Message.tsx
  │   │   └── InputBox.tsx
  │   ├── document/
  │   │   ├── DocumentViewer.tsx
  │   │   └── CodeBlock.tsx
  │   └── common/
  │       ├── MarkdownRenderer.tsx
  │       └── LoadingIndicator.tsx
  ├── services/
  │   ├── api.ts
  │   └── websocket.ts
  ├── styles/
  │   ├── claude-theme.css
  │   └── markdown.css
  └── types/
      └── index.ts
  ```

#### Day 5-6: 核心组件开发
- [ ] Claude.ai风格布局实现
  - 260px固定宽度侧边栏
  - 弹性主内容区
  - 底部固定输入框
- [ ] MarkdownRenderer组件
  - 代码块语法高亮
  - 表格美化显示
  - 数学公式渲染
  - 自定义链接样式
- [ ] 分屏逻辑实现
  - 内容类型智能判断
  - 滑入动画效果
  - 宽度调整功能

#### Day 7: API集成与测试
- [ ] API服务层开发
  - 封装/query接口调用
  - 处理sources数据分发
  - 错误处理机制
- [ ] WebSocket集成
  - 连接管理
  - 消息处理
  - 断线重连
- [ ] 功能测试
  - SQL查询测试
  - RAG查询测试
  - 财务分析测试
  - 资金流向测试

### Phase 2: 功能增强与优化（第8-14天）

#### Week 2: 高级功能实现
- [ ] 流式响应
  - EventSource或WebSocket流
  - 逐字显示效果
  - 打字光标动画
- [ ] 数据可视化
  - 集成recharts/echarts
  - K线图组件
  - 成交量图组件
  - 资金流向图组件
- [ ] 表格增强
  - 排序功能
  - 筛选功能
  - 数值格式化
  - 涨跌颜色标识

#### Week 2 (续): 用户体验优化
- [ ] 主题系统
  - 亮色/深色主题切换
  - 主题持久化存储
  - 自定义颜色方案
- [ ] 快捷键支持
  - Ctrl+N: 新建对话
  - Ctrl+K: 快速搜索
  - Ctrl+Enter: 发送消息
- [ ] 响应式设计
  - 移动端适配
  - 平板适配
  - 触摸手势支持

### Phase 3: 后端优化与技术分析（第15-21天）

#### Week 3: 后端优化
- [ ] 数据库Schema中文映射系统
  - 表结构缓存机制
  - 字段中文含义映射
  - 减少50%数据库查询
- [ ] RAG查询智能降级
  - 多级降级策略
  - 失败模式记录
  - 自动优化建议

#### Week 4: 技术分析系统
- [ ] 技术指标计算
  - MA/EMA/SMA
  - RSI/MACD/KDJ
  - BOLL/SAR
- [ ] TechnicalAnalysisAgent开发
  - 指标计算逻辑
  - 趋势分析
  - 买卖信号生成

## 四、技术规范

### 4.1 代码规范
- TypeScript严格模式
- ESLint + Prettier代码格式化
- 组件采用函数式写法 + Hooks
- 统一的错误处理机制

### 4.2 性能要求
- 首屏加载时间 < 3秒
- API响应展示 < 100ms
- 流畅的60fps动画
- 代码分割和懒加载

### 4.3 测试要求
- 单元测试覆盖率 > 80%
- E2E测试覆盖核心流程
- 性能测试基准建立
- 跨浏览器兼容性测试

## 五、部署计划

### 5.1 开发环境
- Windows: React开发服务器 (端口3000)
- WSL2: FastAPI服务器 (端口8000)
- 代理配置解决跨域问题

### 5.2 生产环境
- 前端：Nginx静态文件服务
- 后端：Gunicorn + Uvicorn
- 反向代理和负载均衡
- Docker容器化部署

## 六、风险管理

### 6.1 技术风险
- WebSocket在不同环境下的兼容性
- 大数据量渲染的性能问题
- 复杂Markdown内容的渲染准确性

### 6.2 缓解措施
- 建立完善的错误边界
- 实现渐进式数据加载
- 充分的测试覆盖

## 七、成功标准

1. **功能完整性**: 100%覆盖现有Web功能
2. **用户体验**: Claude.ai相似度 > 90%
3. **性能指标**: 所有操作响应时间 < 200ms
4. **代码质量**: 测试覆盖率 > 80%
5. **用户反馈**: 满意度评分 > 4.5/5

## 八、时间线总览

```
Week 1: 环境准备 + React MVP
Week 2: 功能增强 + 用户体验
Week 3: 后端优化 + 技术分析
Week 4: 测试完善 + 部署上线
```

---

**注**: 本计划为初版，将根据实际开发进度动态调整。每日更新进度，每周进行回顾和计划调整。