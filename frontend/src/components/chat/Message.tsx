import React, { useState } from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';
import { Avatar } from '../common/Avatar';
import type { Message as MessageType } from '../../types';

interface MessageProps {
  message: MessageType;
  onViewSource?: (source: any, type: string) => void;
  isLastFromSameSpeaker?: boolean;
}

export const Message: React.FC<MessageProps> = ({ message, onViewSource, isLastFromSameSpeaker = false }) => {
  const isUser = message.role === 'user';
  const [_isHovered, setIsHovered] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  
  // 检查是否有可查看的源数据（适配实际的API响应结构）
  const hasViewableSource = !isUser && message.sources && (
    message.sources.sql ||
    message.sources.rag ||
    message.sources.financial ||
    message.sources.money_flow ||
    // 兼容旧格式
    (message.sources.documents && message.sources.documents.length > 0) ||
    (message.sources.sql_data && message.sources.sql_data.length > 0) ||
    message.sources.table_data
  );

  // 动态计算消息间距
  // mb-3 = 0.75rem (12px) - 同一发言者的连续消息
  // mb-6 = 1.5rem (24px) - 不同发言者之间的消息
  const messageSpacing = isLastFromSameSpeaker ? 'mb-3' : 'mb-6';
  
  // 复制内容到剪贴板
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopySuccess(true);
      // 2秒后重置状态
      setTimeout(() => {
        setCopySuccess(false);
      }, 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  return (
    <div 
      className={`group ${messageSpacing}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 
        用户消息 - Claude.ai风格，头像和文本在同一个气泡内
        样式配置：
        - 最大宽度：95% (可调整以控制消息最大宽度)
        - 背景色：#F0EEE6 (米色气泡背景)
        - 圆角：8px (可调整气泡圆角大小)
        - 内边距：上下8px，右14px，左8px
      */}
      {isUser ? (
        <div className="inline-block" style={{ maxWidth: '95%' }}>
          <div 
            className="user-message-bubble flex gap-2.5"
            style={{
              width: 'fit-content',
              backgroundColor: '#141413',     // 深色主题：气泡背景色（深黑）
              padding: '10px 16px 10px 10px',
              borderRadius: '8px',
              wordBreak: 'normal',
              overflowWrap: 'break-word',
              alignItems: 'flex-start'        // 确保顶部对齐
            }}
          >
            {/* 用户头像容器 */}
            <div className="flex-shrink-0 flex items-center" style={{ 
              height: '24px',     // 与单行文字高度一致
              marginTop: '0'      // 确保无额外间距
            }}>
              <Avatar role="user" size={26} /> {/* 头像大小26px，标准型 */}
            </div>
            <div className="flex-grow flex items-center" style={{ minHeight: '24px' }}>
              <p className="text-[15px] leading-relaxed m-0 text-left" style={{ 
                color: '#F5F5F5',     // 深色主题：气泡文字颜色（浅白）
                wordBreak: 'normal',   // 正常换行，避免过早换行
                overflowWrap: 'break-word'  // 长单词自动换行
              }}>
                {message.content}
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* 
          AI消息 - Claude.ai风格，无头像无背景，像文档一样
          pl-12 = 3rem (48px) 左侧内边距，与侧边栏图标对齐
        */
        <div className="ai-message pl-12">
          <div className="prose prose-sm max-w-none">
            <MarkdownRenderer content={message.content} />
            {message.isStreaming && (
              <span className="inline-flex gap-1 ml-2">
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full"></span>
              </span>
            )}
          </div>
        </div>
      )}
      
      
      
      {/* 查看数据按钮和复制按钮 - AI消息底部 */}
      {!isUser && (hasViewableSource || !message.isStreaming) && (
        <div className="flex items-center gap-3 mt-3 pl-12">
          {/* 查看数据按钮组 */}
          {hasViewableSource && (
            <div className="flex gap-2">
          {/* SQL数据 */}
          {message.sources?.sql?.result && (
            <button
              onClick={() => {
                const sqlData = message.sources!.sql!.result;
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
                const content = financialData?.analysis_report || 
                              financialData?.financial_data || 
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
          
          {/* 复制按钮 - 与查看按钮同一行 */}
          {!message.isStreaming && (
            <button
              onClick={handleCopy}
              className="ml-auto action-button p-1.5 rounded border border-gray-200 hover:bg-gray-50 transition-all duration-200"
              title={copySuccess ? "已复制!" : "复制回复"}
            >
              {copySuccess ? (
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
};