import React, { useEffect, useRef } from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';
import type { DocumentViewerProps } from '../../types';

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ content, type, onClose }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 滑入动画
    if (containerRef.current) {
      containerRef.current.style.transform = 'translateX(0)';
    }
  }, []);

  const handleClose = () => {
    if (containerRef.current) {
      containerRef.current.style.transform = 'translateX(100%)';
      setTimeout(onClose, 300);
    }
  };

  const renderContent = () => {
    switch (type) {
      case 'markdown':
        return (
          <div className="prose prose-sm max-w-none">
            {typeof content === 'string' ? (
              <MarkdownRenderer content={content} />
            ) : (
              <pre className="whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>
            )}
          </div>
        );
      
      case 'table':
        return (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                {content.headers && (
                  <tr>
                    {content.headers.map((header: string, index: number) => (
                      <th
                        key={index}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                )}
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {content.rows && content.rows.map((row: any[], rowIndex: number) => (
                  <tr key={rowIndex}>
                    {row.map((cell: any, cellIndex: number) => (
                      <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      
      case 'document':
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">
                {content.metadata?.title || '文档'}
              </h3>
              <div className="text-sm text-gray-600 space-y-1">
                {content.metadata?.source && (
                  <div>来源: {content.metadata.source}</div>
                )}
                {content.metadata?.date && (
                  <div>日期: {content.metadata.date}</div>
                )}
                {content.metadata?.page && (
                  <div>页码: {content.metadata.page}</div>
                )}
              </div>
            </div>
            <div className="prose prose-sm max-w-none">
              <MarkdownRenderer content={content.content || String(content)} />
            </div>
          </div>
        );
      
      case 'chart':
        // 预留图表渲染位置
        return (
          <div className="bg-gray-100 rounded-lg p-8 text-center text-gray-500">
            <p>图表功能开发中...</p>
            <pre className="mt-4 text-left text-xs overflow-auto">
              {JSON.stringify(content, null, 2)}
            </pre>
          </div>
        );
      
      default:
        return (
          <div className="prose prose-sm max-w-none">
            <pre className="overflow-auto">
              {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div
      ref={containerRef}
      className="fixed right-0 top-0 h-full w-1/2 border-l border-claude-border shadow-xl transform translate-x-full transition-transform duration-300 ease-out z-50"
      style={{
        backgroundColor: '#303030',  // 深色主题：右分屏背景色
        color: '#FFFFFF',           // 深色主题：右分屏文字颜色
        transform: 'translateX(100%)'
      }}
    >
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b border-claude-border">
        <h2 className="text-lg font-semibold text-white">
          {type === 'table' ? '数据表格' : 
           type === 'document' ? '源文档' : 
           type === 'chart' ? '数据图表' : '详细信息'}
        </h2>
        <button
          onClick={handleClose}
          className="p-2 hover:bg-[#1E1E1E] rounded-lg transition-colors text-gray-300 hover:text-white"
          aria-label="关闭"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* 内容区 */}
      <div className="h-full overflow-y-auto pb-20 p-6">
        {renderContent()}
      </div>
    </div>
  );
};