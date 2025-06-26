import React from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';
import { Message as MessageType } from '../../types';

interface MessageProps {
  message: MessageType;
  onViewSource?: (source: any, type: string) => void;
}

export const Message: React.FC<MessageProps> = ({ message, onViewSource }) => {
  const isUser = message.role === 'user';
  
  // 检查是否有可查看的源数据（适配实际的API响应结构）
  const hasViewableSource = !isUser && message.sources && (
    message.sources.sql ||
    message.sources.rag ||
    message.sources.financial ||
    message.sources.money_flow ||
    // 兼容旧格式
    message.sources.documents?.length > 0 ||
    message.sources.sql_data?.length > 0 ||
    message.sources.table_data
  );

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-semibold ${
          isUser ? 'bg-blue-500 text-white' : 'bg-claude-primary text-white'
        }`}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        <div
          className={`inline-block max-w-[70%] px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-claude-surface border border-claude-border'
              : 'bg-white border border-claude-border'
          }`}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <>
              <MarkdownRenderer content={message.content} />
              {message.isStreaming && (
                <span className="inline-flex gap-1 ml-2">
                  <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
                  <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
                  <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
                </span>
              )}
            </>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-claude-text-secondary mt-1 px-1">
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
          {hasViewableSource && (
            <div className="flex gap-2">
              {/* SQL数据 */}
              {message.sources?.sql?.result && (
                <button
                  onClick={() => {
                    const sqlData = message.sources!.sql!.result;
                    // SQL结果通常是格式化的文本
                    onViewSource?.(sqlData, 'markdown');
                  }}
                  className="text-claude-primary hover:underline text-xs"
                >
                  查看数据
                </button>
              )}
              
              {/* RAG文档 */}
              {message.sources?.rag?.documents && (
                <button
                  onClick={() => {
                    const docs = message.sources!.rag!.documents;
                    if (Array.isArray(docs) && docs.length > 0) {
                      onViewSource?.(docs[0], 'document');
                    }
                  }}
                  className="text-claude-primary hover:underline text-xs"
                >
                  查看文档
                </button>
              )}
              
              {/* 财务分析数据 */}
              {message.sources?.financial && (
                <button
                  onClick={() => {
                    const financialData = message.sources!.financial;
                    // 尝试提取分析报告或显示完整数据
                    const content = financialData.analysis_report || 
                                  financialData.financial_data || 
                                  JSON.stringify(financialData, null, 2);
                    onViewSource?.(content, 'markdown');
                  }}
                  className="text-claude-primary hover:underline text-xs"
                >
                  查看详情
                </button>
              )}
              
              {/* 资金流向数据 */}
              {message.sources?.money_flow && (
                <button
                  onClick={() => {
                    const moneyFlowData = message.sources!.money_flow;
                    onViewSource?.(moneyFlowData, 'table');
                  }}
                  className="text-claude-primary hover:underline text-xs"
                >
                  查看资金流向
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};