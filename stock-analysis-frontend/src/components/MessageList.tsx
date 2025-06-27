import React, { useEffect, useRef } from 'react';
import { Message } from '../types';
import SimpleMarkdownRenderer from './SimpleMarkdownRenderer';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.type}`}
        >
          <div className="message-avatar">
            {message.type === 'user' ? '👤' : '🤖'}
          </div>
          <div className={`message-content ${message.isError ? 'error' : ''}`}>
            {message.type === 'user' ? (
              <p>{message.content}</p>
            ) : (
              <>
                <SimpleMarkdownRenderer content={message.content} />
                {message.isStreaming && (
                  <span className="typing-cursor"></span>
                )}
              </>
            )}
          </div>
        </div>
      ))}
      
      {isLoading && messages[messages.length - 1]?.isStreaming !== true && (
        <div className="message assistant">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;