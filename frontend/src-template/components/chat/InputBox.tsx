import React, { useState, useRef, KeyboardEvent } from 'react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const InputBox: React.FC<InputBoxProps> = ({
  onSend,
  disabled = false,
  placeholder = "Type your question about stocks, financial reports, or market analysis..."
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <div className="border-t border-claude-border p-4 bg-white">
      <div className="max-w-3xl mx-auto">
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-claude-border rounded-lg focus:outline-none focus:ring-2 focus:ring-claude-primary resize-none max-h-32"
              style={{ minHeight: '48px' }}
            />
            <button
              onClick={() => {/* TODO: Add file upload */}}
              className="absolute right-2 bottom-3 p-1 text-claude-text-secondary hover:text-claude-text-primary transition-colors"
              title="Attach file"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>
          </div>
          <button
            onClick={handleSend}
            disabled={!message.trim() || disabled}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              message.trim() && !disabled
                ? 'bg-claude-primary hover:bg-claude-primary-hover text-white'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            Send
          </button>
        </div>
        <div className="mt-2 text-xs text-claude-text-secondary text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};