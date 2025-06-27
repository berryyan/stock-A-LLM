import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-sm max-w-none prose-pre:p-0 prose-pre:bg-transparent">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
        code({ node, className, children, ...props }: any) {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';
          const inline = !match;

          if (!inline && language) {
            const CodeBlock = () => {
              const [copied, setCopied] = useState(false);
              
              const handleCopy = () => {
                navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              };
              
              return (
                <div className="relative group my-3">
                  {/* 语言标签和复制按钮栏 */}
                  <div className="absolute top-0 left-0 right-0 flex items-center justify-between bg-gray-800 rounded-t-md px-3 py-1.5 border-b border-gray-700">
                    <span className="text-xs font-medium text-gray-300">{language}</span>
                    <button
                      className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors"
                      onClick={handleCopy}
                    >
                      {copied ? (
                        <>
                          <svg className="w-3.5 h-3.5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-green-400">已复制</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span>复制代码</span>
                        </>
                      )}
                    </button>
                  </div>
                  <SyntaxHighlighter
                    style={oneDark as any}
                    language={language}
                    PreTag="div"
                    customStyle={{
                      margin: 0,
                      borderRadius: '0 0 0.375rem 0.375rem',
                      fontSize: '0.875rem',
                      padding: '2.5rem 1rem 1rem 1rem',
                      lineHeight: '1.5',
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                </div>
              );
            };
            
            return <CodeBlock />;
          }

          return (
            <code className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm font-mono text-gray-800 dark:text-gray-200" {...props}>
              {children}
            </code>
          );
        },

        table({ children }) {
          return (
            <div className="overflow-x-auto my-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                {children}
              </table>
            </div>
          );
        },

        thead({ children }) {
          return <thead className="bg-gray-50 dark:bg-gray-800">{children}</thead>;
        },

        th({ children }) {
          return (
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              {children}
            </th>
          );
        },

        td({ children }) {
          return (
            <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100 border-t border-gray-100 dark:border-gray-800">
              {children}
            </td>
          );
        },

        a({ href, children }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-claude-primary hover:text-claude-primary-hover underline decoration-1 underline-offset-2 hover:decoration-2 inline-flex items-center gap-1 transition-all"
            >
              {children}
              <svg
                className="w-3 h-3 opacity-60"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
          );
        },

        blockquote({ children }) {
          return (
            <blockquote className="border-l-4 border-claude-primary bg-gray-50 dark:bg-gray-900 pl-4 pr-4 py-3 my-4 rounded-r-md">
              <div className="text-gray-700 dark:text-gray-300 italic">
                {children}
              </div>
            </blockquote>
          );
        },
        
        ul({ children }) {
          return (
            <ul className="list-disc list-inside space-y-1 my-3 pl-4">
              {children}
            </ul>
          );
        },
        
        ol({ children }) {
          return (
            <ol className="list-decimal list-inside space-y-1 my-3 pl-4">
              {children}
            </ol>
          );
        },
        
        li({ children }) {
          return (
            <li className="text-gray-700 dark:text-gray-300">
              {children}
            </li>
          );
        },
        
        p({ children }) {
          return (
            <p className="my-3 leading-relaxed text-gray-700 dark:text-gray-300">
              {children}
            </p>
          );
        },
        
        h1({ children }) {
          return (
            <h1 className="text-2xl font-bold my-4 text-gray-900 dark:text-gray-100">
              {children}
            </h1>
          );
        },
        
        h2({ children }) {
          return (
            <h2 className="text-xl font-semibold my-3 text-gray-900 dark:text-gray-100">
              {children}
            </h2>
          );
        },
        
        h3({ children }) {
          return (
            <h3 className="text-lg font-semibold my-3 text-gray-900 dark:text-gray-100">
              {children}
            </h3>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
    </div>
  );
};