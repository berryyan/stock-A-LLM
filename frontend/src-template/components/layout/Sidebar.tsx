import React from 'react';

interface ChatItem {
  id: string;
  title: string;
  timestamp: string;
}

interface SidebarProps {
  chats: ChatItem[];
  currentChatId?: string;
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
}) => {
  return (
    <aside className="w-sidebar bg-claude-surface border-r border-claude-border flex flex-col h-full">
      {/* Header with New Chat button */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full px-4 py-3 bg-claude-primary hover:bg-claude-primary-hover text-white rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Chat
        </button>
      </div>

      {/* Chat History */}
      <nav className="flex-1 overflow-y-auto px-2">
        {chats.length === 0 ? (
          <div className="text-claude-text-secondary text-sm p-4 text-center">
            No previous chats
          </div>
        ) : (
          <div className="space-y-1">
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  currentChatId === chat.id
                    ? 'bg-claude-background'
                    : 'hover:bg-claude-background/50'
                }`}
              >
                <div className="text-sm font-medium truncate">{chat.title}</div>
                <div className="text-xs text-claude-text-secondary">
                  {chat.timestamp}
                </div>
              </button>
            ))}
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-claude-border">
        <div className="flex items-center gap-2 text-sm text-claude-text-secondary">
          <div className="w-8 h-8 rounded-full bg-claude-primary/10 flex items-center justify-center">
            <span className="text-xs font-semibold text-claude-primary">SA</span>
          </div>
          <span>Stock Analysis</span>
        </div>
      </div>
    </aside>
  );
};