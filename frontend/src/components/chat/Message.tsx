import React from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';
import { Message as MessageType } from '../../types';

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

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
        <div className="text-xs text-claude-text-secondary mt-1 px-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};