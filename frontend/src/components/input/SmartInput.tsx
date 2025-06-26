import React, { useState, useRef, useEffect, useCallback } from 'react';

interface SmartInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const SmartInput: React.FC<SmartInputProps> = ({
  value,
  onChange,
  onSend,
  isLoading = false,
  placeholder = "输入你的问题..."
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isComposing, setIsComposing] = useState(false);
  
  // 计算字数
  const charCount = value.length;
  const showCharCount = charCount > 1000;
  
  // 自动调整高度
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // 重置高度以获取正确的scrollHeight
    textarea.style.height = 'auto';
    
    // 计算新高度
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 56), 240);
    textarea.style.height = `${newHeight}px`;
    
    // 根据高度决定是否显示滚动条
    textarea.style.overflowY = textarea.scrollHeight > 240 ? 'auto' : 'hidden';
  }, []);
  
  // 监听内容变化调整高度
  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);
  
  // 处理输入变化
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };
  
  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // 处理中文输入法状态
    // 注意：中文输入法的处理效果因输入法而异，该功能未完全验证
    // 某些输入法可能仍会在输入过程中触发Enter事件
    if (isComposing) return;
    
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSend();
      }
    }
  };
  
  // 处理中文输入法
  // 使用CompositionEvent API尝试检测输入法状态
  // 但不同输入法的行为可能不一致
  const handleCompositionStart = () => {
    setIsComposing(true);
  };
  
  const handleCompositionEnd = () => {
    setIsComposing(false);
  };
  
  // 发送按钮是否激活
  const canSend = value.trim().length > 0 && !isLoading;
  
  return (
    <div>
      <div className="flex gap-3 p-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            placeholder={placeholder}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-transparent border-0 rounded-lg focus:outline-none resize-none transition-all duration-200"
            style={{
              minHeight: '56px',
              maxHeight: '240px',
              lineHeight: '24px'
            }}
          />
        
        {/* 字数统计 */}
        {showCharCount && (
          <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white px-1">
            {charCount} 字
          </div>
        )}
      </div>
      
      {/* 发送按钮 */}
      <button 
        onClick={onSend}
        disabled={!canSend}
        className={`px-3 py-2 rounded-lg transition-all duration-200 flex items-center justify-center min-w-[80px] ${
          canSend
            ? 'bg-claude-primary hover:bg-claude-primary-hover text-white'
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
        title={canSend ? "发送消息 (Enter)" : "请输入内容"}
      >
        {isLoading ? (
          <div className="flex items-center gap-1.5">
            <span className="typing-dot w-1.5 h-1.5 bg-white rounded-full"></span>
            <span className="typing-dot w-1.5 h-1.5 bg-white rounded-full"></span>
            <span className="typing-dot w-1.5 h-1.5 bg-white rounded-full"></span>
          </div>
        ) : (
          <svg 
            className="w-5 h-5" 
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" />
          </svg>
        )}
      </button>
      </div>
      
      {/* 工具栏 - Claude.ai风格 */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-100">
        <button className="text-gray-500 hover:text-gray-700 p-1">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>
        
        <div className="text-xs text-gray-500">
          按 Enter 发送，Shift+Enter 换行
        </div>
      </div>
    </div>
  );
};