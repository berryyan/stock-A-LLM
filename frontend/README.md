# Stock Analysis System - React Frontend

基于Claude.ai界面设计的股票分析系统前端。

## 项目初始化

### Windows环境（推荐）

1. 打开Anaconda Prompt
2. 激活环境：
   ```bash
   conda activate stock-frontend
   ```
3. 进入frontend目录：
   ```bash
   cd E:\PycharmProjects\stock_analysis_system\frontend
   ```
4. 运行初始化脚本：
   ```bash
   init-react-project.bat
   ```

### 手动初始化（如果脚本失败）

```bash
# 创建Vite项目
npm create vite@latest . -- --template react-ts

# 安装依赖
npm install

# 安装额外依赖
npm install react-markdown remark-gfm rehype-katex remark-math katex
npm install react-syntax-highlighter @types/react-syntax-highlighter
npm install axios react-router-dom clsx

# 安装Tailwind CSS
npm install -D tailwindcss postcss autoprefixer @tailwindcss/typography
npx tailwindcss init -p
```

## 开发

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/     # React组件
│   │   ├── layout/     # 布局组件
│   │   ├── chat/       # 聊天相关组件
│   │   ├── document/   # 文档查看组件
│   │   └── common/     # 通用组件
│   ├── services/       # API服务
│   ├── hooks/          # 自定义Hooks
│   ├── types/          # TypeScript类型定义
│   ├── utils/          # 工具函数
│   └── styles/         # 样式文件
├── public/             # 静态资源
└── package.json        # 项目配置
```

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **Markdown**: react-markdown + 插件
- **代码高亮**: react-syntax-highlighter
- **HTTP客户端**: Axios
- **路由**: React Router v6

## Claude.ai风格特性

- 260px固定宽度侧边栏
- 左右分屏显示（对话区/文档区）
- 完整的Markdown渲染支持
- 代码块语法高亮
- 数学公式支持（KaTeX）
- 流式响应效果
- 亮色/深色主题切换