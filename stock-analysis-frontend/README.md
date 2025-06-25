# 股票分析系统 - React前端

这是股票分析系统的React前端界面，提供了现代化的聊天式交互体验。

## 功能特性

- 🚀 React 18 + TypeScript + Vite
- 💬 聊天式交互界面
- 📊 支持财务分析、技术分析、资金流向查询
- 🎨 响应式设计，支持移动端
- 📝 Markdown渲染支持
- 🔄 WebSocket实时通信（备用）

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

默认运行在 http://localhost:5173

### 3. 确保后端API运行

在启动前端之前，请确保后端API服务正在运行：

```bash
# 在项目根目录
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构

```
src/
├── components/
│   ├── ChatInterface.tsx    # 主聊天界面
│   ├── MessageList.tsx      # 消息列表
│   ├── InputBox.tsx         # 输入框
│   └── SimpleMarkdownRenderer.tsx  # Markdown渲染器
├── services/
│   └── api.ts              # API服务层
├── types/
│   └── index.ts            # TypeScript类型定义
├── App.tsx                 # 主应用组件
├── App.css                 # 样式文件
└── main.tsx               # 入口文件
```

## 开发说明

### API代理配置

开发环境下，Vite会自动代理API请求到后端服务器：
- `/api/*` → `http://localhost:8000/api/*`
- `/health` → `http://localhost:8000/health`
- `/ws` → `ws://localhost:8000/ws`

### 查询类型自动检测

系统会根据查询内容自动选择合适的查询类型：
- 财务相关 → `financial`
- 公告/报告 → `rag`
- 股价/排名 → `sql`
- 综合查询 → `hybrid`

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录下。

## 测试查询示例

- "分析贵州茅台的财务健康度"
- "茅台最新股价"
- "A股市值排名前10"
- "贵州茅台最新公告"
- "分析茅台的投资价值"

## 注意事项

1. 确保后端API服务正常运行
2. 首次查询可能需要较长时间（模型加载）
3. 复杂查询可能需要30-60秒响应时间