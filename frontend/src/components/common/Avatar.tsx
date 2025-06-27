import React from 'react';

interface AvatarProps {
  role: 'user' | 'assistant';
  size?: number;
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
        borderRadius: '50%',
        fontSize: `${size * 0.4}px`,
        backgroundColor: isUser ? '#3D3D3A' : undefined,
        color: isUser ? '#FFFFFF' : undefined,
      }}
    >
      {isUser ? '用' : 'AI'}
    </div>
  );
};