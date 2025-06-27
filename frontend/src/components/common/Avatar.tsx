import React from 'react';

interface AvatarProps {
  role: 'user' | 'assistant';  // 角色类型：用户或AI助手
  size?: number;                // 头像大小（像素），默认32px
}

export const Avatar: React.FC<AvatarProps> = ({ role, size = 32 }) => {
  const isUser = role === 'user';
  
  return (
    <div 
      className={`
        flex-shrink-0 flex items-center justify-center font-semibold
        ${!isUser && 'bg-claude-primary text-white'}
      `}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',           // 圆形头像
        fontSize: `${size * 0.4}px`,   // 字体大小为头像大小的40%
        backgroundColor: isUser ? '#C2C0B6' : undefined,  // 深色主题：用户头像背景色（浅灰棕）
        color: isUser ? '#262626' : undefined,            // 深色主题：用户头像文字颜色（深灰）
      }}
    >
      {isUser ? '用' : 'AI'}
    </div>
  );
};