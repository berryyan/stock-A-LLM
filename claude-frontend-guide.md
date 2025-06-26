# Claude.ai风格前端开发指南

## 一、核心设计要素

### 1. 整体布局结构
```
┌─────────────────────────────────────────────────────────┐
│                    顶部导航栏 (60px)                      │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│   侧边栏      │          主内容区域                       │
│   (260px)    │         (弹性宽度)                       │
│              │                                          │
│  - 对话列表   │    ┌─────────────┬──────────────┐      │
│  - 新建对话   │    │   对话区域   │   文档/详情   │      │
│  - 历史记录   │    │   (50%)     │    (50%)     │      │
│              │    └─────────────┴──────────────┘      │
└──────────────┴──────────────────────────────────────────┘
```

### 2. 设计规范

#### 颜色方案
```css
/* 主色调 */
--primary-color: #10a37f;        /* Claude绿色 */
--primary-hover: #0d8968;
--background: #f7f7f8;           /* 浅灰背景 */
--surface: #ffffff;              /* 白色卡片 */
--border-color: #e5e5e7;         /* 边框颜色 */
--text-primary: #202123;         /* 主文字 */
--text-secondary: #6e6e80;       /* 次要文字 */

/* 深色模式 */
--dark-background: #2d2d30;
--dark-surface: #1e1e1e;
--dark-border: #3e3e42;
```

#### 字体系统
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', 
             'Noto Sans', 'Helvetica', 'Arial', sans-serif;

/* 字号规范 */
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
```

### 3. 关键组件描述

#### 3.1 侧边栏
- **宽度**: 260px
- **背景**: 浅灰色(#f7f7f8)，深色模式下为深灰(#2d2d30)
- **功能区域**:
  - 顶部: "New Chat"按钮，圆角按钮，hover时颜色加深
  - 中间: 对话历史列表，每项包含标题和时间戳
  - 底部: 用户信息、设置按钮

#### 3.2 对话区域
- **消息布局**: 
  - 用户消息: 右对齐，背景色#f7f7f8，最大宽度70%
  - AI回复: 左对齐，白色背景，带细边框
  - 头像: 用户和AI都有圆形头像（32px）
  
#### 3.3 输入框
- **样式**: 底部固定，带圆角边框
- **功能**: 
  - 支持多行输入，自动调整高度
  - 右侧发送按钮，输入时激活
  - 支持文件上传图标

#### 3.4 分屏显示
- **触发**: 当查询涉及文档或详细数据时
- **动画**: 从右侧滑入，平滑过渡
- **内容**: 支持Markdown渲染、代码高亮、表格展示

## 二、信息分布设计原则

### Claude.ai的左右分屏逻辑

#### 左侧（对话区）始终显示：
1. **用户提问**：完整的用户输入
2. **AI主要回答**：
   - 文字解释和分析
   - 简短的代码片段（<50行）
   - 总结性内容
   - 引导性说明
   - 错误提示和建议

#### 右侧（Artifacts区）触发显示：
1. **完整代码文件**（>50行或完整功能模块）
2. **结构化文档**：
   - 技术文档
   - API说明
   - 项目README
3. **数据可视化**：
   - 图表
   - 表格数据
   - JSON/CSV数据
4. **可交互内容**：
   - React组件
   - HTML页面
   - SVG图形

#### 触发右侧显示的判断逻辑：
```javascript
const shouldShowArtifact = (content) => {
  // 代码长度超过阈值
  if (content.type === 'code' && content.lines > 50) return true;
  
  // 特定类型的内容
  if (['react', 'html', 'svg', 'mermaid'].includes(content.type)) return true;
  
  // 结构化数据
  if (content.type === 'data' && content.format in ['json', 'csv', 'table']) return true;
  
  // 用户明确要求
  if (content.metadata?.showAsArtifact) return true;
  
  return false;
};
```

### 股票分析系统的应用场景：

#### 左侧对话区显示：
- 查询结果的文字说明（"贵州茅台今日收盘价1835.2元，涨幅2.3%"）
- 分析总结（"从财务数据看，该公司..."）
- 查询状态和进度提示

#### 右侧文档区显示：
- 详细的K线图表
- 财务报表数据表格
- 年报/公告PDF内容
- 多只股票对比图表
- SQL查询结果表格

## 三、Markdown渲染技术方案

### Claude.ai使用的技术栈：

1. **核心库**：`react-markdown` - React的Markdown渲染器
2. **语法高亮**：`react-syntax-highlighter` 或 `prism-react-renderer`
3. **数学公式**：`remark-math` + `rehype-katex`
4. **增强插件**：
   - `remark-gfm` - GitHub风格Markdown
   - `remark-breaks` - 支持换行
   - `rehype-raw` - 支持HTML

### 完整的Markdown渲染实现：

```jsx
// MarkdownRenderer.jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';

const MarkdownRenderer = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex, rehypeRaw]}
      components={{
        // 自定义代码块渲染
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';
          
          if (!inline && language) {
            return (
              <div className="code-block-wrapper">
                <div className="code-block-header">
                  <span className="language-tag">{language}</span>
                  <button className="copy-button" onClick={() => copyCode(children)}>
                    Copy
                  </button>
                </div>
                <SyntaxHighlighter
                  style={oneDark}
                  language={language}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    borderRadius: '0 0 8px 8px',
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            );
          }
          
          return (
            <code className="inline-code" {...props}>
              {children}
            </code>
          );
        },
        
        // 自定义表格渲染
        table({ children }) {
          return (
            <div className="table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          );
        },
        
        // 自定义链接
        a({ href, children }) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer" className="markdown-link">
              {children}
              <svg className="external-link-icon" viewBox="0 0 24 24">
                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"></path>
                <path d="M15 3h6v6"></path>
                <path d="M10 14L21 3"></path>
              </svg>
            </a>
          );
        },
        
        // 自定义引用块
        blockquote({ children }) {
          return (
            <blockquote className="markdown-blockquote">
              <div className="quote-bar"></div>
              <div className="quote-content">{children}</div>
            </blockquote>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
```

### 样式设计（Claude风格）：

```css
/* markdown-styles.css */

/* 基础文本样式 */
.markdown-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #202123;
}

/* 代码块样式 */
.code-block-wrapper {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #1e1e1e;
}

.code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #2d2d30;
  border-bottom: 1px solid #3e3e42;
}

.language-tag {
  font-size: 12px;
  color: #cccccc;
  text-transform: uppercase;
}

.copy-button {
  padding: 4px 12px;
  font-size: 12px;
  color: #cccccc;
  background: transparent;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-button:hover {
  background: #3e3e42;
  color: #ffffff;
}

/* 行内代码 */
.inline-code {
  padding: 2px 6px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  background: #f3f4f6;
  border-radius: 3px;
  color: #0969da;
}

/* 表格样式 */
.table-wrapper {
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-table {
  min-width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.markdown-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  background: #f6f8fa;
  border: 1px solid #d1d5db;
}

.markdown-table td {
  padding: 12px;
  border: 1px solid #d1d5db;
}

.markdown-table tr:nth-child(even) {
  background: #f9fafb;
}

/* 链接样式 */
.markdown-link {
  color: #10a37f;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.markdown-link:hover {
  border-bottom-color: #10a37f;
}

.external-link-icon {
  width: 12px;
  height: 12px;
  stroke: currentColor;
  stroke-width: 2;
  fill: none;
}

/* 引用块样式 */
.markdown-blockquote {
  display: flex;
  margin: 16px 0;
  padding: 0;
}

.quote-bar {
  width: 4px;
  background: #10a37f;
  border-radius: 2px;
  flex-shrink: 0;
}

.quote-content {
  padding: 8px 16px;
  color: #6e6e80;
  flex: 1;
}

/* 标题样式 */
.markdown-content h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 24px 0 16px;
  line-height: 1.3;
}

.markdown-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 12px;
  line-height: 1.3;
}

.markdown-content h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 16px 0 8px;
  line-height: 1.3;
}

/* 列表样式 */
.markdown-content ul {
  margin: 12px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 6px 0;
}

/* 深色模式适配 */
[data-theme="dark"] .markdown-content {
  color: #e3e3e3;
}

[data-theme="dark"] .inline-code {
  background: #3e3e42;
  color: #79c0ff;
}

[data-theme="dark"] .markdown-table th {
  background: #2d2d30;
  border-color: #3e3e42;
}

[data-theme="dark"] .markdown-table td {
  border-color: #3e3e42;
}

[data-theme="dark"] .markdown-table tr:nth-child(even) {
  background: #1e1e1e;
}
```

## 二、具体实现代码

### 1. React组件结构
```jsx
// App.jsx
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import DocumentViewer from './components/DocumentViewer';
import './styles/claude-theme.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [showDocument, setShowDocument] = useState(false);
  const [documentContent, setDocumentContent] = useState(null);

  return (
    <div className="app-container">
      <Sidebar 
        conversations={conversations}
        currentChat={currentChat}
        onSelectChat={setCurrentChat}
        onNewChat={createNewChat}
      />
      <div className="main-content">
        <ChatArea 
          chat={currentChat}
          onSendMessage={handleSendMessage}
          onShowDocument={handleShowDocument}
        />
        {showDocument && (
          <DocumentViewer 
            content={documentContent}
            onClose={() => setShowDocument(false)}
          />
        )}
      </div>
    </div>
  );
}
```

### 2. 核心CSS样式
```css
/* claude-theme.css */
.app-container {
  display: flex;
  height: 100vh;
  background-color: var(--background);
}

.sidebar {
  width: 260px;
  background-color: var(--surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  position: relative;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.document-viewer {
  width: 50%;
  background: var(--surface);
  border-left: 1px solid var(--border-color);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

/* 消息样式 */
.message {
  display: flex;
  padding: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.5;
}

.message.user .message-content {
  background-color: var(--background);
}

.message.assistant .message-content {
  background-color: var(--surface);
  border: 1px solid var(--border-color);
}

/* 输入框样式 */
.input-container {
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: var(--surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 12px;
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  max-height: 200px;
}
```

### 3. 与后端API集成
```javascript
// api/client.js
class StockAnalysisAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async query(question, queryType = 'hybrid') {
    const response = await fetch(`${this.baseURL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        query_type: queryType
      })
    });
    return response.json();
  }

  async streamQuery(question, onChunk) {
    const response = await fetch(`${this.baseURL}/api/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      onChunk(chunk);
    }
  }
}
```

## 三、关键交互细节

### 1. 消息发送流程
```javascript
const handleSendMessage = async (message) => {
  // 1. 添加用户消息到界面
  addMessage({ role: 'user', content: message });
  
  // 2. 显示加载状态
  setIsLoading(true);
  
  // 3. 调用API
  try {
    const response = await api.query(message);
    
    // 4. 添加AI回复
    addMessage({ 
      role: 'assistant', 
      content: response.answer,
      sources: response.sources 
    });
    
    // 5. 如果有文档内容，显示在右侧
    if (response.sources?.documents) {
      setDocumentContent(response.sources.documents);
      setShowDocument(true);
    }
  } catch (error) {
    // 错误处理
  } finally {
    setIsLoading(false);
  }
};
```

### 2. 流式响应处理
```javascript
const handleStreamResponse = async (message) => {
  let assistantMessage = { role: 'assistant', content: '' };
  addMessage(assistantMessage);
  
  await api.streamQuery(message, (chunk) => {
    assistantMessage.content += chunk;
    updateMessage(assistantMessage);
  });
};
```

### 3. 分屏文档显示
- 当查询返回文档、表格或详细数据时自动触发
- 支持Markdown渲染（使用react-markdown）
- 代码块语法高亮（使用prism.js）
- 表格美化显示
- 支持关闭和调整宽度

## 四、高级功能建议

### 1. 快捷键支持
- `Ctrl/Cmd + N`: 新建对话
- `Ctrl/Cmd + K`: 快速搜索
- `Ctrl/Cmd + Enter`: 发送消息

### 2. 主题切换
```javascript
const toggleTheme = () => {
  const theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  document.body.dataset.theme = theme;
  localStorage.setItem('theme', theme);
};
```

### 3. 消息编辑和重新生成
- 支持编辑已发送的消息
- 重新生成AI回复
- 保存对话历史到本地

## 五、与Claude Code集成的完整指令

在使用Claude Code时，你可以使用以下详细指令：

```
我想创建一个React前端应用，完全模仿Claude.ai的界面设计和交互逻辑：

## 基础架构
1. 使用React + TypeScript + Vite
2. 安装依赖：react-markdown, remark-gfm, react-syntax-highlighter, rehype-katex, remark-math

## 布局设计
1. 左侧260px宽的侧边栏，显示对话历史
2. 主区域分为对话区和文档查看区（可选显示）
3. 使用Claude的配色方案（主色#10a37f）
4. 底部固定输入框，支持多行和自动调整高度
5. 消息显示用户头像，AI回复带边框

## 核心功能
1. Markdown渲染：
   - 使用react-markdown渲染所有AI回复
   - 支持代码高亮（使用react-syntax-highlighter）
   - 支持表格、列表、引用块等GFM特性
   - 代码块显示语言标签和复制按钮
   - 数学公式渲染（KaTeX）

2. 信息分布逻辑：
   - 左侧对话区：显示用户问题、AI文字回答、短代码片段
   - 右侧文档区：当返回以下内容时自动显示
     * 长代码（>50行）
     * 数据表格（sources.table_data）
     * 图表数据（sources.chart_data）
     * PDF文档内容（sources.documents）
   - 实现平滑的滑入动画

3. API集成：
   - 基础URL: http://localhost:8000
   - 查询端点: POST /query
   - 请求格式: {
       "question": "用户输入",
       "query_type": "hybrid",
       "top_k": 5
     }
   - 响应格式: {
       "success": boolean,
       "answer": "Markdown格式的回答",
       "query_type": string,
       "sources": {
         "sql_data": [],
         "documents": [],
         "table_data": [],
         "chart_data": {}
       }
     }

4. 流式响应（如果后端支持）：
   - 使用EventSource或fetch流式API
   - 逐字显示AI回复
   - 显示打字光标效果

5. 股票数据特殊处理：
   - 识别股票代码（如600519.SH）
   - 表格数据自动美化显示
   - 支持K线图等金融图表展示

请生成完整的项目结构，包括：
- 主要组件（App, Sidebar, ChatArea, MessageList, InputBox, DocumentViewer, MarkdownRenderer）
- 完整的样式文件（支持亮色/深色主题）
- API服务类
- 类型定义文件
- 示例数据用于开发测试
```

### 补充说明：股票分析系统的特殊需求

```
针对股票分析系统，还需要特别处理：

1. 数据可视化组件：
   - 使用recharts或echarts显示K线图、成交量图
   - 财务数据对比图表
   - 资金流向图

2. 表格增强：
   - 支持排序、筛选
   - 数值格式化（千分位、百分比、涨跌颜色）
   - 固定表头

3. 实时数据：
   - WebSocket连接支持（如果后端提供）
   - 数据自动刷新
   - 显示最后更新时间

4. 查询模板：
   - 预设常用查询（"今日涨幅榜"、"资金流向"等）
   - 查询历史记录
   - 智能搜索建议
```