import React from 'react';
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
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';

          if (!inline && language) {
            return (
              <div className="relative group my-2">
                <div className="absolute top-0 right-0 flex items-center gap-2 px-2 py-1 text-xs text-gray-400 bg-gray-800 rounded-bl">
                  <span>{language}</span>
                  <button
                    className="hover:text-white transition-colors"
                    onClick={() => {
                      navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                    }}
                  >
                    Copy
                  </button>
                </div>
                <SyntaxHighlighter
                  style={oneDark}
                  language={language}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    padding: '1rem',
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            );
          }

          return (
            <code className="px-1 py-0.5 bg-gray-100 rounded text-sm font-mono" {...props}>
              {children}
            </code>
          );
        },

        table({ children }) {
          return (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
                {children}
              </table>
            </div>
          );
        },

        thead({ children }) {
          return <thead className="bg-gray-50">{children}</thead>;
        },

        th({ children }) {
          return (
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {children}
            </th>
          );
        },

        td({ children }) {
          return <td className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">{children}</td>;
        },

        a({ href, children }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-claude-primary hover:underline inline-flex items-center gap-1"
            >
              {children}
              <svg
                className="w-3 h-3"
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
            <blockquote className="border-l-4 border-claude-primary pl-4 my-4 italic text-gray-700">
              {children}
            </blockquote>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
    </div>
  );
};