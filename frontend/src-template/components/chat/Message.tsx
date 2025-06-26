import React from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';

export interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export const Message: React.FC<MessageProps> = ({ role, content, timestamp }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-semibold ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-claude-primary text-white'
        }`}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        <div
          className={`inline-block max-w-[70%] px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-claude-background'
              : 'bg-white border border-claude-border'
          }`}
        >
          {isUser ? (
            <p className="text-sm">{content}</p>
          ) : (
            <MarkdownRenderer content={content} />
          )}
        </div>
        {timestamp && (
          <div className="text-xs text-claude-text-secondary mt-1 px-1">
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
};