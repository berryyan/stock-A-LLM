import React, { useState, useRef, useEffect } from 'react';
import { Message } from './components/chat/Message';
import { DocumentViewer } from './components/document/DocumentViewer';
import { Message as MessageType } from './types';
import stockAPI from './services/api';

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documentView, setDocumentView] = useState<{content: any; type: string} | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() && !isLoading) {
      const userMessage: MessageType = {
        id: Date.now().toString(),
        role: 'user',
        content: input.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await stockAPI.query(userMessage.content);
        
        const assistantMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.answer,
          timestamp: new Date().toISOString(),
          sources: response.sources,
        };

        setMessages(prev => [...prev, assistantMessage]);
      } catch (error: any) {
        console.error('Query failed:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          config: error.config
        });
        
        let errorContent = '抱歉，查询失败。';
        if (error.response) {
          errorContent += ` 错误状态: ${error.response.status}`;
          if (error.response.data?.detail) {
            errorContent += ` - ${error.response.data.detail}`;
          }
        } else if (error.request) {
          errorContent += ' 无法连接到API服务器。';
        } else {
          errorContent += ` ${error.message}`;
        }
        
        const errorMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: errorContent,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen bg-claude-background">
      {/* Sidebar - 支持折叠 */}
      <aside className={`${sidebarCollapsed ? 'w-12' : 'w-sidebar'} bg-claude-surface border-r border-claude-border transition-all duration-300 relative`}>
        {/* 折叠按钮 */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-6 w-6 h-6 bg-white border border-claude-border rounded-full flex items-center justify-center hover:bg-gray-50 z-10"
          title={sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'}
        >
          <svg className={`w-3 h-3 transition-transform ${sidebarCollapsed ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        {sidebarCollapsed ? (
          /* 折叠状态 - 只显示图标 */
          <div className="p-2">
            <button 
              onClick={() => {
                setMessages([]);
                setSidebarCollapsed(false);
              }}
              className="w-8 h-8 flex items-center justify-center text-claude-primary hover:bg-gray-100 rounded"
              title="New Chat"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        ) : (
          /* 展开状态 - 完整侧边栏 */
          <>
            <div className="p-4">
              <button 
                onClick={() => {
                  setMessages([]);
                }}
                className="w-full px-4 py-3 bg-claude-primary hover:bg-claude-primary-hover text-white rounded-lg transition-colors"
              >
                New Chat
              </button>
            </div>
            <nav className="p-2">
              <div className="text-claude-text-secondary text-sm p-2">
                No previous chats
              </div>
            </nav>
          </>
        )}
      </aside>

      {/* Main Content */}
      <main className={`flex-1 flex flex-col transition-all duration-300 ${documentView ? 'mr-[50%]' : ''}`}>
        {/* Chat Area - 调整最大宽度和内边距 */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className={`mx-auto ${documentView ? 'max-w-full px-6' : 'max-w-4xl'}`}>
            {messages.length === 0 ? (
              <div className="text-center text-claude-text-secondary py-20">
                <h1 className="text-2xl font-semibold mb-2">
                  Stock Analysis System
                </h1>
                <p>Ask me about stock prices, financial reports, or market analysis</p>
                <div className="mt-8 space-y-2 text-sm">
                  <p className="font-semibold">Try asking:</p>
                  <p>"贵州茅台最新股价是多少？"</p>
                  <p>"分析一下茅台的财务健康度"</p>
                  <p>"查询贵州茅台最新的公告"</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <Message 
                    key={msg.id} 
                    message={msg}
                    onViewSource={(content, type) => {
                      setDocumentView({ content, type });
                      // 打开文档时自动折叠侧边栏
                      if (!sidebarCollapsed) {
                        setSidebarCollapsed(true);
                      }
                    }}
                  />
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-claude-primary text-white flex items-center justify-center text-sm font-semibold">
                      AI
                    </div>
                    <div className="flex-1">
                      <div className="inline-block px-4 py-2 rounded-lg bg-white border border-claude-border">
                        <span className="inline-flex gap-1">
                          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area - 调整布局以适应分屏 */}
        <div className="border-t border-claude-border p-4 bg-white">
          <div className={`mx-auto ${documentView ? 'max-w-full px-6' : 'max-w-4xl'}`}>
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="输入你的问题..."
                disabled={isLoading}
                rows={1}
                className="flex-1 px-4 py-3 border border-claude-border rounded-lg focus:outline-none focus:ring-2 focus:ring-claude-primary resize-none"
                style={{
                  minHeight: '48px',
                  maxHeight: '200px',
                  overflowY: input.split('\n').length > 4 ? 'auto' : 'hidden',
                }}
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  input.trim() && !isLoading
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
      </main>
      
      {/* Document Viewer */}
      {documentView && (
        <DocumentViewer
          content={documentView.content}
          type={documentView.type as any}
          onClose={() => setDocumentView(null)}
        />
      )}
    </div>
  );
}

export default App;