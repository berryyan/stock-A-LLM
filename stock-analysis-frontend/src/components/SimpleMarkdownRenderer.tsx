import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface SimpleMarkdownRendererProps {
  content: string;
}

const SimpleMarkdownRenderer: React.FC<SimpleMarkdownRendererProps> = ({ content }) => {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 表格样式
          table: ({ children }) => (
            <table className="markdown-table">
              {children}
            </table>
          ),
          // 代码块样式
          code: ({ inline, children }) => {
            if (inline) {
              return <code className="inline-code">{children}</code>;
            }
            return (
              <pre className="code-block">
                <code>{children}</code>
              </pre>
            );
          },
          // 链接在新窗口打开
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default SimpleMarkdownRenderer;