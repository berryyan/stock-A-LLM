# Claude.ai前端界面完整实现指南：技术架构与交互细节全解析

本指南整合了Claude.ai前端界面的所有设计理念、技术架构和实现细节。通过本文档，Claude Code将能够完整理解并精确复现这个优雅而强大的聊天界面系统。

## 第一部分：设计理念与整体架构

### 1.1 核心设计原则

Claude.ai的界面设计遵循"简约而不简单"的理念。每个元素都经过精心设计，确保功能强大的同时保持视觉上的优雅和使用上的直观。

**三大设计支柱**：
1. **信息层次清晰**：通过空间布局和视觉权重引导用户注意力
2. **交互反馈即时**：每个操作都有明确的视觉和动画反馈
3. **适应性强**：从手机到大屏幕都能提供最佳体验

### 1.2 整体布局结构

```
┌─────────────────────────────────────────────────────────────┐
│                    顶部导航栏 (60px)                           │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   侧边栏      │              主内容区域                        │
│   (260px)    │            (弹性宽度)                         │
│              │                                              │
│  ▪ 对话列表   │    ┌─────────────────┬──────────────────┐   │
│  ▪ 新建对话   │    │    对话区域      │   文档/详情区     │   │
│  ▪ 历史记录   │    │  (50%或100%)    │     (50%)        │   │
│              │    └─────────────────┴──────────────────┘   │
└──────────────┴──────────────────────────────────────────────┘
```

这个布局采用CSS Grid实现，确保了各个区域的独立性和灵活性：

```css
.app-container {
  display: grid;
  grid-template-rows: 60px 1fr;
  grid-template-columns: 260px 1fr auto;
  height: 100vh;
  position: relative;
}
```

## 第二部分：布局系统的技术实现

### 2.1 侧边栏的多态设计

侧边栏不是简单的显示/隐藏，而是实现了三种状态的智能切换：

```javascript
const SidebarStates = {
  EXPANDED: 'expanded',    // 260px - 完整显示所有信息
  COLLAPSED: 'collapsed',  // 60px - 仅显示图标，悬停展开
  HIDDEN: 'hidden'        // 0px - 完全隐藏（移动端）
};

const Sidebar = () => {
  const [state, setState] = useState(SidebarStates.EXPANDED);
  const [isHovering, setIsHovering] = useState(false);
  const { isMobile } = useResponsive();
  
  // 计算实际宽度
  const effectiveWidth = useMemo(() => {
    if (state === SidebarStates.HIDDEN) return 0;
    if (state === SidebarStates.COLLAPSED && !isHovering) return 60;
    return 260;
  }, [state, isHovering]);
  
  // 自动适应屏幕尺寸
  useEffect(() => {
    if (isMobile) {
      setState(SidebarStates.HIDDEN);
    } else {
      setState(SidebarStates.EXPANDED);
    }
  }, [isMobile]);
  
  return (
    <aside 
      className="sidebar"
      style={{
        width: effectiveWidth,
        transition: 'width 300ms cubic-bezier(0.4, 0, 0.2, 1)'
      }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="sidebar-header">
        <button className="new-chat-button">
          <PlusIcon />
          <span className={state === SidebarStates.COLLAPSED ? 'hidden' : ''}>
            New Chat
          </span>
        </button>
      </div>
      
      <div className="chat-history">
        {/* 对话历史列表 */}
      </div>
      
      <div className="sidebar-footer">
        {/* 用户信息和设置 */}
      </div>
    </aside>
  );
};
```

### 2.2 主内容区的智能布局

主内容区需要处理两种模式：单列对话模式和分屏详情模式。

```javascript
const MainContent = () => {
  const [isDocumentVisible, setIsDocumentVisible] = useState(false);
  const [splitRatio, setSplitRatio] = useState(50); // 初始50/50分割
  
  return (
    <div className="main-content">
      <div 
        className="chat-area"
        style={{
          width: isDocumentVisible ? `${100 - splitRatio}%` : '100%'
        }}
      >
        <ChatMessages />
        <InputArea />
      </div>
      
      {isDocumentVisible && (
        <DocumentViewer 
          width={`${splitRatio}%`}
          onResize={setSplitRatio}
        />
      )}
    </div>
  );
};
```

### 2.3 内容居中的精确控制

不分屏时，对话内容需要优雅地居中显示：

```css
.chat-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.chat-content {
  width: 100%;
  max-width: 768px; /* 最佳阅读宽度 */
  padding: 0 24px;
  margin: 0 auto;
}

/* 根据屏幕大小调整 */
@media (max-width: 1024px) {
  .chat-content {
    max-width: 100%;
    padding: 0 20px;
  }
}

@media (max-width: 768px) {
  .chat-content {
    padding: 0 16px;
  }
}
```

## 第三部分：消息系统的视觉设计

### 3.1 消息组件的完整实现

每条消息都包含丰富的视觉和交互元素：

```jsx
const Message = ({ message, isUser }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div 
      className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="message-content">
        <Avatar type={isUser ? 'user' : 'assistant'} />
        
        <div className="message-body">
          {isUser ? (
            <div className="user-message-text">{message.content}</div>
          ) : (
            <MarkdownRenderer 
              content={message.content}
              onCodeExpand={handleCodeExpand}
            />
          )}
          
          {/* 悬停时显示的操作按钮 */}
          {isHovered && (
            <div className="message-actions">
              <button onClick={() => copyToClipboard(message.content)}>
                <CopyIcon />
              </button>
              {isUser && (
                <button onClick={() => setIsEditing(true)}>
                  <EditIcon />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* 时间戳 */}
      <div className="message-timestamp">
        {formatTime(message.timestamp)}
      </div>
    </div>
  );
};
```

### 3.2 消息样式的细节处理

```css
/* 基础消息样式 */
.message-wrapper {
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  position: relative;
}

/* 用户消息 - 右对齐 */
.message-wrapper.user {
  align-items: flex-end;
}

.message-wrapper.user .message-content {
  flex-direction: row-reverse;
}

.message-wrapper.user .message-body {
  background-color: #f7f7f8;
  border-radius: 20px 20px 4px 20px;
  padding: 12px 16px;
  max-width: 70%;
  margin-right: 12px;
}

/* AI消息 - 左对齐 */
.message-wrapper.assistant .message-body {
  background-color: #ffffff;
  border: 1px solid #e5e5e7;
  border-radius: 4px 20px 20px 20px;
  padding: 16px;
  max-width: 100%;
  margin-left: 12px;
}

/* 头像样式 */
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 600;
}

.avatar.user {
  background-color: #10a37f;
  color: white;
}

.avatar.assistant {
  background-color: #ffffff;
  border: 1px solid #e5e5e7;
}

/* 消息间距的智能调整 */
.message-wrapper + .message-wrapper {
  margin-top: 20px;
}

/* 同一发言者的连续消息减少间距 */
.message-wrapper.user + .message-wrapper.user,
.message-wrapper.assistant + .message-wrapper.assistant {
  margin-top: 8px;
}

/* 操作按钮的渐显效果 */
.message-actions {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.message-wrapper:hover .message-actions {
  opacity: 1;
}
```

## 第四部分：输入系统的智能设计

### 4.1 自适应输入框的完整实现

输入框需要处理多种复杂情况：自动高度、快捷键、粘贴处理等。

```javascript
const SmartTextarea = ({ onSubmit, onTyping }) => {
  const textareaRef = useRef(null);
  const [value, setValue] = useState('');
  const [height, setHeight] = useState('auto');
  const [isComposing, setIsComposing] = useState(false);
  
  // 自动调整高度
  useEffect(() => {
    if (textareaRef.current) {
      // 先重置高度以获取准确的scrollHeight
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const newHeight = Math.min(scrollHeight, 200); // 最大200px
      setHeight(`${newHeight}px`);
    }
  }, [value]);
  
  // 处理键盘事件
  const handleKeyDown = (e) => {
    // 中文输入法组合时不处理
    if (isComposing) return;
    
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  // 处理提交
  const handleSubmit = () => {
    const trimmedValue = value.trim();
    if (trimmedValue) {
      onSubmit(trimmedValue);
      setValue('');
      // 重置高度
      setHeight('44px');
    }
  };
  
  // 处理粘贴
  const handlePaste = (e) => {
    const pastedText = e.clipboardData.getData('text');
    // 处理大量文本粘贴
    if (pastedText.length > 5000) {
      if (window.confirm('粘贴的文本较长，是否继续？')) {
        // 允许粘贴
      } else {
        e.preventDefault();
      }
    }
  };
  
  return (
    <div className="input-container">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            onTyping && onTyping(e.target.value);
          }}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          onPaste={handlePaste}
          placeholder="Send a message..."
          style={{ height }}
          className="smart-textarea"
          rows={1}
        />
        
        <div className="input-actions">
          <button 
            className="attach-button"
            onClick={() => {/* 处理文件上传 */}}
          >
            <AttachIcon />
          </button>
          
          <button 
            className={`send-button ${value.trim() ? 'active' : ''}`}
            onClick={handleSubmit}
            disabled={!value.trim()}
          >
            <SendIcon />
          </button>
        </div>
      </div>
      
      {/* 字数统计 */}
      {value.length > 1000 && (
        <div className="char-count">
          {value.length} / 10000
        </div>
      )}
    </div>
  );
};
```

### 4.2 输入框的视觉细节

```css
.input-container {
  position: fixed;
  bottom: 0;
  left: 260px; /* 考虑侧边栏 */
  right: 0;
  padding: 20px;
  background: linear-gradient(
    to top, 
    var(--background-primary) 0%, 
    var(--background-primary) 85%, 
    transparent 100%
  );
  pointer-events: none; /* 允许滚动穿透 */
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: var(--surface);
  border: 1px solid var(--border-default);
  border-radius: 24px;
  padding: 8px 16px;
  pointer-events: all; /* 恢复交互 */
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
}

.smart-textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  min-height: 24px;
  max-height: 200px;
  overflow-y: auto;
}

/* 自定义滚动条 */
.smart-textarea::-webkit-scrollbar {
  width: 6px;
}

.smart-textarea::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 3px;
}

/* 按钮样式 */
.send-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.send-button:not(.active) {
  background: var(--border-default);
  cursor: not-allowed;
}

.send-button.active:hover {
  background: var(--primary-hover);
  transform: scale(1.05);
}
```

## 第五部分：智能分屏系统

### 5.1 分屏触发的判断逻辑

系统需要智能判断何时显示右侧文档区：

```javascript
const ContentAnalyzer = {
  // 分析是否需要分屏显示
  shouldShowDocument(message) {
    const triggers = {
      // 长代码检测
      hasLongCode: () => {
        const codeBlocks = this.extractCodeBlocks(message.content);
        return codeBlocks.some(block => block.lines > 50);
      },
      
      // 结构化数据检测
      hasStructuredData: () => {
        if (!message.metadata) return false;
        return ['table', 'json', 'csv'].includes(message.metadata.format);
      },
      
      // 图表数据检测
      hasChartData: () => {
        return message.metadata?.chartData !== undefined;
      },
      
      // 文档引用检测
      hasDocumentReference: () => {
        return message.metadata?.documents?.length > 0;
      },
      
      // 交互组件检测
      hasInteractiveContent: () => {
        return message.metadata?.hasArtifact && 
               ['react', 'html', 'svg'].includes(message.metadata.artifactType);
      }
    };
    
    return Object.values(triggers).some(trigger => trigger());
  },
  
  // 提取代码块
  extractCodeBlocks(content) {
    const codeBlockRegex = /```[\s\S]*?```/g;
    const blocks = content.match(codeBlockRegex) || [];
    
    return blocks.map(block => {
      const lines = block.split('\n').length - 2; // 减去```标记
      const language = block.match(/```(\w+)/)?.[1] || 'text';
      return { lines, language, content: block };
    });
  },
  
  // 生成预览内容
  generatePreview(content, maxLines = 10) {
    const lines = content.split('\n');
    if (lines.length <= maxLines) return content;
    
    return {
      preview: lines.slice(0, maxLines).join('\n'),
      totalLines: lines.length,
      hasMore: true
    };
  }
};
```

### 5.2 分屏动画的实现

```javascript
const DocumentViewer = ({ content, isVisible, onClose }) => {
  const [width, setWidth] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef(null);
  
  // 处理拖动调整宽度
  const handleDragStart = (e) => {
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = width;
    
    const handleDragMove = (e) => {
      const deltaX = startX - e.clientX;
      const containerWidth = window.innerWidth - 260; // 减去侧边栏
      const deltaPercent = (deltaX / containerWidth) * 100;
      const newWidth = Math.min(70, Math.max(30, startWidth + deltaPercent));
      setWidth(newWidth);
    };
    
    const handleDragEnd = () => {
      setIsDragging(false);
      document.removeEventListener('mousemove', handleDragMove);
      document.removeEventListener('mouseup', handleDragEnd);
    };
    
    document.addEventListener('mousemove', handleDragMove);
    document.addEventListener('mouseup', handleDragEnd);
  };
  
  return (
    <div 
      className={`document-viewer ${isVisible ? 'visible' : ''}`}
      style={{
        width: `${width}%`,
        transform: `translateX(${isVisible ? 0 : 100}%)`,
        transition: isDragging ? 'none' : 'transform 350ms cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      {/* 拖动手柄 */}
      <div 
        ref={dragRef}
        className="resize-handle"
        onMouseDown={handleDragStart}
      >
        <div className="handle-indicator" />
      </div>
      
      {/* 文档头部 */}
      <div className="document-header">
        <h3 className="document-title">
          {content.title || 'Document'}
        </h3>
        <button onClick={onClose} className="close-button">
          <CloseIcon />
        </button>
      </div>
      
      {/* 文档内容 */}
      <div className="document-content">
        {renderDocumentContent(content)}
      </div>
    </div>
  );
};
```

### 5.3 内容预览卡片设计

```jsx
const ContentPreviewCard = ({ content, onExpand }) => {
  const preview = ContentAnalyzer.generatePreview(content);
  
  return (
    <div className="content-preview-card">
      <div className="preview-header">
        <CodeIcon />
        <span className="preview-title">
          {content.language || 'Code'} • {preview.totalLines} lines
        </span>
      </div>
      
      <div className="preview-body">
        <pre className="preview-code">
          <code>{preview.preview}</code>
        </pre>
        
        {preview.hasMore && (
          <div className="preview-fade" />
        )}
      </div>
      
      <button 
        className="expand-button"
        onClick={() => onExpand(content)}
      >
        <span>View Full Code</span>
        <ArrowRightIcon />
      </button>
    </div>
  );
};
```

## 第六部分：Markdown渲染系统

### 6.1 完整的Markdown渲染器

```jsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';

const MarkdownRenderer = ({ content, theme = 'light' }) => {
  const [expandedCodeBlocks, setExpandedCodeBlocks] = useState(new Set());
  
  const components = {
    // 代码块处理
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const codeString = String(children).replace(/\n$/, '');
      const lineCount = codeString.split('\n').length;
      
      // 行内代码
      if (inline) {
        return (
          <code className="inline-code" {...props}>
            {children}
          </code>
        );
      }
      
      // 代码块
      const blockId = `${language}-${codeString.substring(0, 20)}`;
      const isExpanded = expandedCodeBlocks.has(blockId);
      const shouldShowPreview = lineCount > 50 && !isExpanded;
      
      return (
        <div className="code-block-wrapper">
          <div className="code-block-header">
            <span className="language-tag">{language || 'plaintext'}</span>
            <div className="code-block-actions">
              <span className="line-count">{lineCount} lines</span>
              <CopyButton text={codeString} />
            </div>
          </div>
          
          {shouldShowPreview ? (
            <ContentPreviewCard
              content={{ language, code: codeString, lineCount }}
              onExpand={() => {
                setExpandedCodeBlocks(new Set([...expandedCodeBlocks, blockId]));
              }}
            />
          ) : (
            <SyntaxHighlighter
              style={theme === 'dark' ? oneDark : oneLight}
              language={language}
              PreTag="div"
              customStyle={{
                margin: 0,
                borderRadius: '0 0 8px 8px',
                fontSize: '14px',
                lineHeight: '1.5'
              }}
              showLineNumbers={lineCount > 10}
              {...props}
            >
              {codeString}
            </SyntaxHighlighter>
          )}
        </div>
      );
    },
    
    // 表格增强
    table({ children }) {
      return (
        <div className="table-container">
          <div className="table-wrapper">
            <table className="markdown-table">{children}</table>
          </div>
        </div>
      );
    },
    
    // 链接处理
    a({ href, children }) {
      const isExternal = href?.startsWith('http');
      
      return (
        <a 
          href={href} 
          target={isExternal ? '_blank' : undefined}
          rel={isExternal ? 'noopener noreferrer' : undefined}
          className="markdown-link"
        >
          {children}
          {isExternal && <ExternalLinkIcon />}
        </a>
      );
    },
    
    // 引用块美化
    blockquote({ children }) {
      return (
        <blockquote className="markdown-blockquote">
          <div className="quote-decoration" />
          <div className="quote-content">{children}</div>
        </blockquote>
      );
    },
    
    // 图片处理
    img({ src, alt }) {
      return (
        <figure className="markdown-image">
          <img src={src} alt={alt} loading="lazy" />
          {alt && <figcaption>{alt}</figcaption>}
        </figure>
      );
    },
    
    // 复选框列表
    input({ type, checked, ...props }) {
      if (type === 'checkbox') {
        return (
          <input 
            type="checkbox" 
            checked={checked} 
            readOnly 
            className="task-checkbox"
            {...props}
          />
        );
      }
      return <input type={type} {...props} />;
    }
  };
  
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

// 复制按钮组件
const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };
  
  return (
    <button 
      className="copy-button"
      onClick={handleCopy}
      aria-label="Copy code"
    >
      {copied ? (
        <>
          <CheckIcon />
          <span>Copied!</span>
        </>
      ) : (
        <>
          <CopyIcon />
          <span>Copy</span>
        </>
      )}
    </button>
  );
};
```

### 6.2 Markdown样式系统

```css
/* 基础文本样式 */
.markdown-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
  word-wrap: break-word;
}

/* 标题层次 */
.markdown-content h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 24px 0 16px;
  line-height: 1.25;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
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
  line-height: 1.4;
}

/* 段落和列表 */
.markdown-content p {
  margin: 0 0 16px;
}

.markdown-content ul,
.markdown-content ol {
  margin: 0 0 16px;
  padding-left: 24px;
}

.markdown-content li {
  margin: 4px 0;
}

.markdown-content li > p {
  margin: 0;
}

/* 代码样式 */
.inline-code {
  padding: 2px 6px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
  font-size: 14px;
  background: var(--code-bg);
  border-radius: 3px;
  color: var(--code-text);
}

.code-block-wrapper {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #1e1e1e;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  font-weight: 500;
}

.code-block-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.line-count {
  font-size: 12px;
  color: #999999;
}

/* 表格样式 */
.table-container {
  margin: 16px 0;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
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
  background: var(--background-secondary);
  border: 1px solid var(--border-default);
  white-space: nowrap;
}

.markdown-table td {
  padding: 12px;
  border: 1px solid var(--border-default);
}

.markdown-table tr:nth-child(even) {
  background: var(--background-secondary);
}

/* 链接样式 */
.markdown-link {
  color: var(--primary-color);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.markdown-link:hover {
  border-bottom-color: var(--primary-color);
}

.markdown-link svg {
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
  position: relative;
}

.quote-decoration {
  width: 4px;
  background: var(--primary-color);
  border-radius: 2px;
  flex-shrink: 0;
}

.quote-content {
  padding: 8px 16px;
  color: var(--text-secondary);
  flex: 1;
}

.quote-content > *:last-child {
  margin-bottom: 0;
}

/* 图片样式 */
.markdown-image {
  margin: 16px 0;
  text-align: center;
}

.markdown-image img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markdown-image figcaption {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 任务列表样式 */
.task-checkbox {
  margin-right: 8px;
  cursor: not-allowed;
}

/* 深色模式适配 */
[data-theme="dark"] .markdown-content {
  color: var(--text-primary);
}

[data-theme="dark"] .inline-code {
  background: var(--code-bg);
  color: var(--code-text);
}

[data-theme="dark"] .code-block-wrapper {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .markdown-table th {
  background: var(--background-secondary);
  border-color: var(--border-default);
}

[data-theme="dark"] .markdown-table td {
  border-color: var(--border-default);
}

[data-theme="dark"] .markdown-table tr:nth-child(even) {
  background: var(--background-secondary);
}

[data-theme="dark"] .markdown-image img {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}
```

## 第七部分：深色模式的完整实现

### 7.1 主题管理系统

```javascript
// 主题管理器 - 处理所有主题相关逻辑
class ThemeManager {
  constructor() {
    this.themes = {
      light: lightTheme,
      dark: darkTheme
    };
    
    // 初始化
    this.currentTheme = this.initializeTheme();
    this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // 立即应用主题，防止闪烁
    this.applyThemeImmediately();
    
    // 设置监听器
    this.setupListeners();
  }
  
  initializeTheme() {
    // 优先级：URL参数 > 用户偏好 > 系统偏好 > 默认值
    const urlParams = new URLSearchParams(window.location.search);
    const urlTheme = urlParams.get('theme');
    if (urlTheme && this.themes[urlTheme]) {
      return urlTheme;
    }
    
    const savedTheme = localStorage.getItem('theme-preference');
    if (savedTheme && this.themes[savedTheme]) {
      return savedTheme;
    }
    
    return this.mediaQuery.matches ? 'dark' : 'light';
  }
  
  applyThemeImmediately() {
    // 立即应用主题，防止页面闪烁
    document.documentElement.dataset.theme = this.currentTheme;
    
    // 应用CSS变量
    const themeColors = this.themes[this.currentTheme];
    Object.entries(themeColors).forEach(([key, value]) => {
      document.documentElement.style.setProperty(`--${key}`, value);
    });
  }
  
  setupListeners() {
    // 监听系统主题变化
    this.mediaQuery.addEventListener('change', (e) => {
      // 只有用户没有明确选择时才跟随系统
      if (!localStorage.getItem('theme-preference')) {
        this.setTheme(e.matches ? 'dark' : 'light', false);
      }
    });
    
    // 监听其他标签页的主题变化
    window.addEventListener('storage', (e) => {
      if (e.key === 'theme-preference' && e.newValue) {
        this.setTheme(e.newValue, false);
      }
    });
  }
  
  setTheme(theme, isUserPreference = true) {
    if (!this.themes[theme] || theme === this.currentTheme) return;
    
    // 准备过渡
    this.prepareTransition();
    
    // 更新当前主题
    this.currentTheme = theme;
    
    // 应用主题
    requestAnimationFrame(() => {
      this.applyTheme(theme);
      
      if (isUserPreference) {
        localStorage.setItem('theme-preference', theme);
      }
      
      this.updateSystemUI(theme);
      this.notifyThemeChange(theme, isUserPreference);
      
      // 清理过渡
      setTimeout(() => this.cleanupTransition(), 300);
    });
  }
  
  prepareTransition() {
    document.documentElement.classList.add('theme-transitioning');
    
    // 防止图片闪烁
    document.querySelectorAll('img').forEach(img => {
      img.style.transition = 'opacity 300ms';
    });
  }
  
  cleanupTransition() {
    document.documentElement.classList.remove('theme-transitioning');
    
    document.querySelectorAll('img').forEach(img => {
      img.style.transition = '';
    });
  }
  
  applyTheme(theme) {
    // 更新data属性
    document.documentElement.dataset.theme = theme;
    
    // 批量更新CSS变量
    const themeColors = this.themes[theme];
    const root = document.documentElement;
    
    // 使用CSS.supports检查CSS变量支持
    if (CSS && CSS.supports && CSS.supports('--custom-property', 'value')) {
      // 批量更新以提高性能
      requestAnimationFrame(() => {
        Object.entries(themeColors).forEach(([key, value]) => {
          root.style.setProperty(`--${key}`, value);
        });
      });
    }
  }
  
  updateSystemUI(theme) {
    // 更新浏览器主题颜色
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.content = theme === 'dark' ? '#212121' : '#ffffff';
    }
    
    // 更新状态栏样式（iOS）
    const metaStatusBar = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]');
    if (metaStatusBar) {
      metaStatusBar.content = theme === 'dark' ? 'black-translucent' : 'default';
    }
    
    // 更新Windows磁贴颜色
    const metaTileColor = document.querySelector('meta[name="msapplication-TileColor"]');
    if (metaTileColor) {
      metaTileColor.content = theme === 'dark' ? '#212121' : '#10a37f';
    }
  }
  
  notifyThemeChange(theme, isUserPreference) {
    // 触发自定义事件
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme, isUserPreference, timestamp: Date.now() }
    }));
  }
  
  // 获取当前主题
  getTheme() {
    return this.currentTheme;
  }
  
  // 切换主题
  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }
}

// React Hook for theme
const useTheme = () => {
  const [theme, setTheme] = useState(() => themeManager.getTheme());
  
  useEffect(() => {
    const handleThemeChange = (e) => {
      setTheme(e.detail.theme);
    };
    
    window.addEventListener('themechange', handleThemeChange);
    return () => window.removeEventListener('themechange', handleThemeChange);
  }, []);
  
  return {
    theme,
    setTheme: (newTheme) => themeManager.setTheme(newTheme),
    toggleTheme: () => themeManager.toggleTheme()
  };
};
```

### 7.2 完整的主题配色系统

```javascript
// 精心设计的主题配色
const lightTheme = {
  // 背景层次 - 创造深度感
  'background-primary': '#ffffff',
  'background-secondary': '#f7f7f8', 
  'background-tertiary': '#ececf1',
  'background-elevated': '#ffffff',
  'background-overlay': 'rgba(0, 0, 0, 0.5)',
  'background-hover': 'rgba(0, 0, 0, 0.02)',
  
  // 文字层次 - 确保可读性
  'text-primary': '#202123',
  'text-secondary': '#6e6e80',
  'text-tertiary': '#acacbe',
  'text-quaternary': '#d1d1db',
  'text-inverse': '#ffffff',
  'text-link': '#10a37f',
  
  // 边框系统
  'border-default': '#e5e5e7',
  'border-light': '#f3f3f6',
  'border-medium': '#d1d1db',
  'border-heavy': '#acacbe',
  'border-focus': '#10a37f',
  
  // 品牌色
  'primary-color': '#10a37f',
  'primary-hover': '#0d8968',
  'primary-active': '#0a6d53',
  'primary-light': 'rgba(16, 163, 127, 0.1)',
  'primary-lighter': 'rgba(16, 163, 127, 0.05)',
  
  // 语义色
  'error-color': '#ef4444',
  'error-light': '#fee2e2',
  'warning-color': '#f59e0b',
  'warning-light': '#fef3c7',
  'success-color': '#10b981',
  'success-light': '#d1fae5',
  'info-color': '#3b82f6',
  'info-light': '#dbeafe',
  
  // 阴影系统
  'shadow-xs': '0 1px 2px rgba(0, 0, 0, 0.05)',
  'shadow-sm': '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
  'shadow-md': '0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)',
  'shadow-lg': '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',
  'shadow-xl': '0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)',
  
  // 特殊用途
  'code-bg': '#f6f8fa',
  'code-text': '#0969da',
  'code-border': '#d1d5db',
  'scrollbar-track': '#f3f3f6',
  'scrollbar-thumb': '#d1d1db',
  'scrollbar-thumb-hover': '#acacbe'
};

const darkTheme = {
  // 背景层次 - 避免纯黑，使用温暖的灰色
  'background-primary': '#212121',
  'background-secondary': '#2d2d30',
  'background-tertiary': '#3e3e42',
  'background-elevated': '#2d2d30',
  'background-overlay': 'rgba(0, 0, 0, 0.7)',
  'background-hover': 'rgba(255, 255, 255, 0.02)',
  
  // 文字层次 - 避免纯白，减少眼睛疲劳
  'text-primary': '#ececf1',
  'text-secondary': '#c5c5d2',
  'text-tertiary': '#8e8ea0',
  'text-quaternary': '#6e6e80',
  'text-inverse': '#202123',
  'text-link': '#14b885',
  
  // 边框系统 - 更柔和的对比
  'border-default': '#3e3e42',
  'border-light': '#2d2d30',
  'border-medium': '#4e4e52',
  'border-heavy': '#6e6e80',
  'border-focus': '#10a37f',
  
  // 品牌色 - 在暗色背景下调整亮度
  'primary-color': '#10a37f',
  'primary-hover': '#14b885',
  'primary-active': '#18c48d',
  'primary-light': 'rgba(16, 163, 127, 0.15)',
  'primary-lighter': 'rgba(16, 163, 127, 0.08)',
  
  // 语义色 - 为暗色背景优化
  'error-color': '#f87171',
  'error-light': 'rgba(248, 113, 113, 0.1)',
  'warning-color': '#fbbf24',
  'warning-light': 'rgba(251, 191, 36, 0.1)',
  'success-color': '#34d399',
  'success-light': 'rgba(52, 211, 153, 0.1)',
  'info-color': '#60a5fa',
  'info-light': 'rgba(96, 165, 250, 0.1)',
  
  // 阴影系统 - 使用内发光创造深度
  'shadow-xs': '0 0 0 1px rgba(255, 255, 255, 0.05)',
  'shadow-sm': '0 1px 2px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
  'shadow-md': '0 4px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
  'shadow-lg': '0 10px 15px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
  'shadow-xl': '0 20px 25px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
  
  // 特殊用途
  'code-bg': '#1e1e1e',
  'code-text': '#79c0ff',
  'code-border': '#3e3e42',
  'scrollbar-track': '#2d2d30',
  'scrollbar-thumb': '#4e4e52',
  'scrollbar-thumb-hover': '#6e6e80'
};
```

### 7.3 主题切换动画

```css
/* 主题过渡基础样式 */
.theme-transitioning,
.theme-transitioning *,
.theme-transitioning *::before,
.theme-transitioning *::after {
  transition: 
    background-color 300ms cubic-bezier(0.4, 0, 0.2, 1),
    color 300ms cubic-bezier(0.4, 0, 0.2, 1),
    border-color 300ms cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1),
    fill 300ms cubic-bezier(0.4, 0, 0.2, 1),
    stroke 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
  transition-delay: 0s !important;
}

/* 防止特定元素闪烁 */
.theme-transitioning img,
.theme-transitioning video,
.theme-transitioning iframe,
.theme-transitioning canvas {
  transition: 
    opacity 300ms cubic-bezier(0.4, 0, 0.2, 1),
    filter 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* 代码高亮不参与过渡 */
.theme-transitioning pre,
.theme-transitioning pre *,
.theme-transitioning code {
  transition: none !important;
}

/* 输入框特殊处理 */
.theme-transitioning input,
.theme-transitioning textarea,
.theme-transitioning select {
  transition: 
    background-color 300ms cubic-bezier(0.4, 0, 0.2, 1),
    border-color 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}
```

### 7.4 组件级别的主题适配

```jsx
// 主题切换器组件
const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  const [isAnimating, setIsAnimating] = useState(false);
  
  const handleToggle = () => {
    setIsAnimating(true);
    toggleTheme();
    
    // 动画结束后重置状态
    setTimeout(() => setIsAnimating(false), 300);
  };
  
  return (
    <button
      className={`theme-toggle ${isAnimating ? 'animating' : ''}`}
      onClick={handleToggle}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <div className="toggle-icons">
        <SunIcon className={theme === 'light' ? 'active' : ''} />
        <MoonIcon className={theme === 'dark' ? 'active' : ''} />
      </div>
    </button>
  );
};
```

```css
/* 主题切换器样式 */
.theme-toggle {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-default);
  background: var(--background-secondary);
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--background-tertiary);
  transform: scale(1.05);
}

.theme-toggle.animating {
  animation: togglePulse 0.3s ease-out;
}

@keyframes togglePulse {
  0% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(0.9) rotate(180deg); }
  100% { transform: scale(1) rotate(360deg); }
}

.toggle-icons {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-icons svg {
  position: absolute;
  width: 20px;
  height: 20px;
  transition: opacity 0.3s, transform 0.3s;
}

.toggle-icons svg:not(.active) {
  opacity: 0;
  transform: scale(0.8) rotate(-90deg);
}

.toggle-icons svg.active {
  opacity: 1;
  transform: scale(1) rotate(0deg);
}
```

## 第八部分：响应式设计系统

### 8.1 断点系统和设备适配

```scss
// 断点定义 - 基于常见设备尺寸
$breakpoints: (
  'mobile-small': 375px,    // iPhone SE
  'mobile': 768px,          // 标准手机横屏/平板竖屏
  'tablet': 1024px,         // 平板横屏/小笔记本
  'desktop': 1440px,        // 标准桌面
  'wide': 1920px,           // 大屏幕
  'ultra-wide': 2560px      // 超宽屏
);

// 响应式工具函数
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (max-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

@mixin respond-between($min, $max) {
  @media (min-width: map-get($breakpoints, $min)) and (max-width: map-get($breakpoints, $max)) {
    @content;
  }
}

// 设备特定样式
@mixin device-specific {
  // iOS安全区域
  @supports (padding: env(safe-area-inset-left)) {
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  // 高分辨率屏幕
  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    // 为Retina屏幕优化
  }
}
```

### 8.2 响应式布局实现

```javascript
// 响应式Hook - 提供设备信息
const useResponsive = () => {
  const [state, setState] = useState(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
    device: getDeviceType(window.innerWidth),
    orientation: getOrientation()
  }));
  
  useEffect(() => {
    let timeoutId;
    
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        setState({
          width: window.innerWidth,
          height: window.innerHeight,
          device: getDeviceType(window.innerWidth),
          orientation: getOrientation()
        });
      }, 150);
    };
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);
    
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);
  
  return {
    ...state,
    isMobile: state.device === 'mobile',
    isTablet: state.device === 'tablet',
    isDesktop: state.device === 'desktop',
    isLandscape: state.orientation === 'landscape',
    isPortrait: state.orientation === 'portrait'
  };
};

// 设备类型判断
const getDeviceType = (width) => {
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  if (width < 1440) return 'desktop';
  return 'wide';
};

// 方向判断
const getOrientation = () => {
  return window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
};
```

### 8.3 移动端特殊处理

```jsx
// 移动端布局组件
const MobileLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  
  // 处理虚拟键盘
  useEffect(() => {
    const handleViewportChange = () => {
      const height = window.visualViewport?.height || window.innerHeight;
      const keyboardHeight = window.innerHeight - height;
      setKeyboardHeight(keyboardHeight);
    };
    
    window.visualViewport?.addEventListener('resize', handleViewportChange);
    return () => {
      window.visualViewport?.removeEventListener('resize', handleViewportChange);
    };
  }, []);
  
  return (
    <div 
      className="mobile-layout"
      style={{
        paddingBottom: keyboardHeight > 0 ? `${keyboardHeight}px` : 'env(safe-area-inset-bottom)'
      }}
    >
      {/* 移动端头部 */}
      <MobileHeader onMenuClick={() => setSidebarOpen(true)} />
      
      {/* 侧边栏覆盖层 */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          >
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 20 }}
              className="mobile-sidebar"
              onClick={(e) => e.stopPropagation()}
            >
              <Sidebar onClose={() => setSidebarOpen(false)} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 主内容 */}
      <main className="mobile-main">
        {children}
      </main>
    </div>
  );
};
```

### 8.4 分屏在不同设备的适配

```javascript
// 响应式分屏组件
const ResponsiveDocumentViewer = ({ content, isVisible }) => {
  const { isMobile, isTablet, width } = useResponsive();
  
  // 移动端：全屏显示
  if (isMobile) {
    return (
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25 }}
            className="mobile-document-viewer"
          >
            <div className="mobile-document-header">
              <h3>{content.title}</h3>
              <button onClick={onClose}>
                <CloseIcon />
              </button>
            </div>
            <div className="mobile-document-content">
              {content.body}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    );
  }
  
  // 平板：自动隐藏侧边栏
  if (isTablet) {
    return (
      <TabletDocumentViewer 
        content={content}
        isVisible={isVisible}
        defaultWidth={60} // 默认60%宽度
      />
    );
  }
  
  // 桌面：标准分屏
  return (
    <DesktopDocumentViewer 
      content={content}
      isVisible={isVisible}
      defaultWidth={50} // 默认50%宽度
    />
  );
};
```

## 第九部分：股票系统的特殊适配

### 9.1 金融数据的展示组件

```jsx
// 股票数据卡片
const StockDataCard = ({ stockData }) => {
  const { price, change, changePercent, volume, marketCap } = stockData;
  const isPositive = change >= 0;
  
  return (
    <div className="stock-data-card">
      <div className="stock-price-section">
        <span className="current-price">{formatPrice(price)}</span>
        <div className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
          <span className="change-amount">{formatChange(change)}</span>
          <span className="change-percent">({formatPercent(changePercent)})</span>
        </div>
      </div>
      
      <div className="stock-metrics">
        <div className="metric">
          <span className="metric-label">成交量</span>
          <span className="metric-value">{formatVolume(volume)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">市值</span>
          <span className="metric-value">{formatMarketCap(marketCap)}</span>
        </div>
      </div>
    </div>
  );
};

// K线图组件
const StockChart = ({ data, type = 'candlestick' }) => {
  const chartRef = useRef(null);
  const { theme } = useTheme();
  
  useEffect(() => {
    if (!chartRef.current || !data) return;
    
    const chart = echarts.init(chartRef.current, theme);
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%'
      },
      xAxis: {
        type: 'category',
        data: data.dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        splitNumber: 20,
        min: 'dataMin',
        max: 'dataMax'
      },
      yAxis: {
        scale: true,
        splitArea: {
          show: true
        }
      },
      series: [
        {
          name: '股价',
          type: 'candlestick',
          data: data.values,
          itemStyle: {
            color: '#ef4444',
            color0: '#10b981',
            borderColor: '#ef4444',
            borderColor0: '#10b981'
          }
        }
      ]
    };
    
    chart.setOption(option);
    
    // 响应式调整
    const resizeObserver = new ResizeObserver(() => {
      chart.resize();
    });
    resizeObserver.observe(chartRef.current);
    
    return () => {
      chart.dispose();
      resizeObserver.disconnect();
    };
  }, [data, theme]);
  
  return <div ref={chartRef} className="stock-chart" />;
};

// 财务数据表格
const FinancialTable = ({ data, onCellClick }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);
  
  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };
  
  return (
    <div className="financial-table-wrapper">
      <table className="financial-table">
        <thead>
          <tr>
            {Object.keys(data[0] || {}).map(key => (
              <th key={key} onClick={() => handleSort(key)}>
                {formatColumnName(key)}
                {sortConfig.key === key && (
                  <SortIcon direction={sortConfig.direction} />
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, index) => (
            <tr key={index}>
              {Object.entries(row).map(([key, value]) => (
                <td 
                  key={key}
                  onClick={() => onCellClick && onCellClick(value, key, row)}
                  className={getValueClass(value, key)}
                >
                  {formatCellValue(value, key)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### 9.2 股票数据样式系统

```css
/* 股票数据卡片样式 */
.stock-data-card {
  background: var(--background-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.stock-price-section {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.current-price {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
}

.price-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 18px;
  font-weight: 500;
}

.price-change.positive {
  color: #ef4444;
}

.price-change.negative {
  color: #10b981;
}

.stock-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.metric-value {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

/* K线图样式 */
.stock-chart {
  width: 100%;
  height: 400px;
  min-height: 300px;
}

@media (max-width: 768px) {
  .stock-chart {
    height: 300px;
    min-height: 250px;
  }
}

/* 财务表格样式 */
.financial-table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--border-default);
  border-radius: 8px;
}

.financial-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.financial-table th {
  position: sticky;
  top: 0;
  background: var(--background-secondary);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border-default);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.financial-table th:hover {
  background: var(--background-tertiary);
}

.financial-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-light);
}

.financial-table tr:hover {
  background: var(--background-hover);
}

/* 数值格式化样式 */
.value-positive {
  color: #ef4444;
}

.value-negative {
  color: #10b981;
}

.value-neutral {
  color: var(--text-primary);
}

/* 涨跌幅标识 */
.change-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.change-indicator::before {
  content: '';
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
}

.change-indicator.up::before {
  border-bottom: 6px solid #ef4444;
}

.change-indicator.down::before {
  border-top: 6px solid #10b981;
}
```

### 9.3 实时数据更新系统

```javascript
// WebSocket管理器
class RealtimeDataManager {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.subscribers = new Map();
  }
  
  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.onConnect();
      };
      
      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      this.ws.onclose = () => {
        this.onDisconnect();
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, delay);
  }
  
  subscribe(channel, callback) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    
    this.subscribers.get(channel).add(callback);
    
    // 发送订阅消息
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        channel
      }));
    }
    
    // 返回取消订阅函数
    return () => {
      const callbacks = this.subscribers.get(channel);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(channel);
          // 发送取消订阅消息
          if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
              type: 'unsubscribe',
              channel
            }));
          }
        }
      }
    };
  }
  
  handleMessage(data) {
    const { channel, payload } = data;
    const callbacks = this.subscribers.get(channel);
    
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(payload);
        } catch (error) {
          console.error('Error in subscriber callback:', error);
        }
      });
    }
  }
  
  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// React Hook for realtime data
const useRealtimeData = (channel, initialData = null) => {
  const [data, setData] = useState(initialData);
  const [isConnected, setIsConnected] = useState(false);
  const managerRef = useRef(null);
  
  useEffect(() => {
    if (!managerRef.current) {
      managerRef.current = new RealtimeDataManager('ws://localhost:8000/ws');
      managerRef.current.onConnect = () => setIsConnected(true);
      managerRef.current.onDisconnect = () => setIsConnected(false);
      managerRef.current.connect();
    }
    
    const unsubscribe = managerRef.current.subscribe(channel, (newData) => {
      setData(newData);
    });
    
    return () => {
      unsubscribe();
    };
  }, [channel]);
  
  return { data, isConnected };
};
```

## 第十部分：完整项目结构和集成指南

### 10.1 推荐的项目结构

```
claude-ai-frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   ├── chat/
│   │   │   ├── ChatArea.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── Message.tsx
│   │   │   └── InputBox.tsx
│   │   ├── document/
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── CodeBlock.tsx
│   │   │   └── ContentPreview.tsx
│   │   ├── markdown/
│   │   │   ├── MarkdownRenderer.tsx
│   │   │   └── components/
│   │   ├── stock/
│   │   │   ├── StockDataCard.tsx
│   │   │   ├── StockChart.tsx
│   │   │   ├── FinancialTable.tsx
│   │   │   └── MarketOverview.tsx
│   │   └── common/
│   │       ├── Avatar.tsx
│   │       ├── Button.tsx
│   │       ├── Icon.tsx
│   │       └── Loading.tsx
│   ├── hooks/
│   │   ├── useTheme.ts
│   │   ├── useResponsive.ts
│   │   ├── useRealtimeData.ts
│   │   ├── useLocalStorage.ts
│   │   └── useDebounce.ts
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── stockApi.ts
│   │   │   └── types.ts
│   │   ├── websocket/
│   │   │   └── RealtimeDataManager.ts
│   │   └── storage/
│   │       └── ConversationStorage.ts
│   ├── contexts/
│   │   ├── ThemeContext.tsx
│   │   ├── ChatContext.tsx
│   │   └── AppContext.tsx
│   ├── styles/
│   │   ├── base/
│   │   │   ├── reset.css
│   │   │   ├── variables.css
│   │   │   └── typography.css
│   │   ├── themes/
│   │   │   ├── light.css
│   │   │   └── dark.css
│   │   ├── components/
│   │   │   └── [component styles]
│   │   └── main.css
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── contentAnalyzer.ts
│   │   └── constants.ts
│   ├── types/
│   │   ├── index.ts
│   │   ├── chat.ts
│   │   ├── stock.ts
│   │   └── api.ts
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 10.2 核心依赖配置

```json
{
  "name": "claude-ai-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write src"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "remark-math": "^6.0.0",
    "rehype-katex": "^7.0.0",
    "rehype-raw": "^7.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "katex": "^0.16.9",
    "framer-motion": "^11.0.0",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "axios": "^1.6.5",
    "date-fns": "^3.2.0",
    "clsx": "^2.1.0",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@types/react-syntax-highlighter": "^15.5.11",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "@typescript-eslint/parser": "^6.19.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "postcss": "^8.4.33",
    "prettier": "^3.2.4",
    "sass": "^1.70.0",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.12"
  }
}
```

### 10.3 主应用组件集成

```tsx
// App.tsx - 完整的应用入口
import React, { useState, useEffect, useCallback } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { ChatProvider } from './contexts/ChatContext';
import { Layout } from './components/layout/Layout';
import { ChatArea } from './components/chat/ChatArea';
import { DocumentViewer } from './components/document/DocumentViewer';
import { useResponsive } from './hooks/useResponsive';
import { StockAnalysisAPI } from './services/api/client';
import { ContentAnalyzer } from './utils/contentAnalyzer';
import './styles/main.css';

const api = new StockAnalysisAPI();

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [documentContent, setDocumentContent] = useState(null);
  const [isDocumentVisible, setIsDocumentVisible] = useState(false);
  const { isMobile } = useResponsive();
  
  // 处理消息发送
  const handleSendMessage = useCallback(async (content: string) => {
    if (!activeConversation) return;
    
    // 添加用户消息
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    
    setActiveConversation(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }));
    
    try {
      // 调用API
      const response = await api.query(content);
      
      // 添加AI回复
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        metadata: response.sources,
        timestamp: new Date()
      };
      
      setActiveConversation(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage]
      }));
      
      // 检查是否需要显示文档
      if (ContentAnalyzer.shouldShowDocument(aiMessage)) {
        setDocumentContent(aiMessage.metadata);
        setIsDocumentVisible(true);
      }
    } catch (error) {
      console.error('Failed to get response:', error);
      // 显示错误消息
    }
  }, [activeConversation]);
  
  // 创建新对话
  const createNewConversation = useCallback(() => {
    const newConversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversation(newConversation);
    setDocumentContent(null);
    setIsDocumentVisible(false);
  }, []);
  
  // 初始化
  useEffect(() => {
    // 加载保存的对话
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      setConversations(JSON.parse(savedConversations));
    } else {
      createNewConversation();
    }
  }, []);
  
  // 保存对话
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
  }, [conversations]);
  
  return (
    <ThemeProvider>
      <ChatProvider>
        <Layout
          conversations={conversations}
          activeConversation={activeConversation}
          onSelectConversation={setActiveConversation}
          onNewConversation={createNewConversation}
        >
          <div className="app-content">
            <ChatArea
              conversation={activeConversation}
              onSendMessage={handleSendMessage}
              showDocument={isDocumentVisible && !isMobile}
            />
            
            <DocumentViewer
              content={documentContent}
              isVisible={isDocumentVisible}
              onClose={() => setIsDocumentVisible(false)}
              isMobile={isMobile}
            />
          </div>
        </Layout>
      </ChatProvider>
    </ThemeProvider>
  );
}

export default App;
```

### 10.4 API集成示例

```typescript
// services/api/client.ts
import axios, { AxiosInstance } from 'axios';
import { QueryRequest, QueryResponse, FinancialAnalysisRequest } from './types';

export class StockAnalysisAPI {
  private client: AxiosInstance;
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 300000, // 5分钟超时
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // 请求拦截器
    this.client.interceptors.request.use(
      config => {
        // 添加认证token等
        return config;
      },
      error => Promise.reject(error)
    );
    
    // 响应拦截器
    this.client.interceptors.response.use(
      response => response.data,
      error => {
        // 统一错误处理
        if (error.response) {
          console.error('API Error:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }
  
  // 通用查询
  async query(question: string, options?: Partial<QueryRequest>): Promise<QueryResponse> {
    return this.client.post('/query', {
      question,
      query_type: 'hybrid',
      top_k: 5,
      ...options
    });
  }
  
  // 财务分析
  async financialAnalysis(request: FinancialAnalysisRequest) {
    return this.client.post('/financial-analysis', request);
  }
  
  // 获取系统状态
  async getStatus() {
    return this.client.get('/status');
  }
  
  // 健康检查
  async healthCheck() {
    return this.client.get('/health');
  }
}
```

## 第十一部分：Claude Code实施指南

### 11.1 分阶段实施计划

当使用Claude Code实现这个界面时，建议按以下顺序进行：

#### 第一阶段：基础架构（Day 1）
1. 创建项目结构
2. 安装所有依赖
3. 设置TypeScript配置
4. 创建基础样式系统（CSS变量、reset样式）
5. 实现主题管理器

#### 第二阶段：核心布局（Day 2）
1. 实现Layout组件
2. 创建Sidebar（三态切换）
3. 实现响应式系统
4. 添加路由结构（如需要）

#### 第三阶段：消息系统（Day 3-4）
1. 创建Message组件
2. 实现MessageList虚拟滚动
3. 创建InputBox智能输入
4. 添加消息操作（复制、编辑）

#### 第四阶段：Markdown渲染（Day 5）
1. 集成react-markdown
2. 实现自定义组件
3. 添加代码高亮
4. 处理特殊内容

#### 第五阶段：分屏系统（Day 6）
1. 实现DocumentViewer
2. 添加拖动调整
3. 实现内容分析器
4. 添加动画效果

#### 第六阶段：API集成（Day 7）
1. 创建API客户端
2. 实现数据流
3. 添加错误处理
4. 实现加载状态

#### 第七阶段：股票特性（Day 8-9）
1. 创建股票组件
2. 集成图表库
3. 实现实时更新
4. 添加数据格式化

#### 第八阶段：优化完善（Day 10）
1. 性能优化
2. 添加过渡动画  
3. 完善响应式
4. 测试修复

### 11.2 关键实施要点

1. **始终从移动端开始设计**，然后扩展到桌面
2. **使用TypeScript**确保类型安全
3. **组件化思维**，保持组件的独立性和可复用性
4. **性能优先**，使用虚拟滚动、懒加载等技术
5. **渐进增强**，先实现基础功能，再添加高级特性

### 11.3 测试清单

- [ ] 深色/浅色主题切换流畅
- [ ] 移动端体验完整
- [ ] 长对话列表性能良好
- [ ] Markdown渲染正确
- [ ] 分屏拖动顺畅
- [ ] API错误处理完善
- [ ] 股票数据显示正常
- [ ] 键盘快捷键工作
- [ ] 无障碍支持完整

## 结语

这个完整的实现指南涵盖了Claude.ai前端界面的所有技术细节。通过遵循这个指南，你将能够创建一个功能完整、体验优秀的聊天界面。记住，优秀的用户界面不仅仅是功能的堆砌，更是对细节的极致追求。每一个动画、每一个交互、每一个像素都应该经过精心设计，共同创造出流畅自然的用户体验。

祝你实现成功！