import { useState, useRef, useEffect } from 'react';
import { Message } from './components/chat/Message';
import { DocumentViewer } from './components/document/DocumentViewer';
import { SmartInput } from './components/input/SmartInput';
import type { Message as MessageType } from './types';
import stockAPI from './services/api';

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documentView, setDocumentView] = useState<{content: any; type: string} | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = (smooth = true) => {
    if (messagesEndRef.current) {
      const chatContainer = messagesEndRef.current.parentElement?.parentElement;
      if (chatContainer) {
        const scrollHeight = chatContainer.scrollHeight;
        const height = chatContainer.clientHeight;
        const maxScrollTop = scrollHeight - height;
        chatContainer.scrollTo({
          top: maxScrollTop,
          behavior: smooth ? 'smooth' : 'auto'
        });
      }
    }
  };

  useEffect(() => {
    // 延迟滚动以确保DOM更新完成
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 100);
    return () => clearTimeout(timer);
  }, [messages]);
  
  // 发送消息时的滚动
  useEffect(() => {
    if (isLoading) {
      const timer = setTimeout(() => scrollToBottom(), 200);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

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
      
      // 立即滚动到顶部，为AI回复留出空间
      setTimeout(() => {
        const chatContainer = messagesEndRef.current?.parentElement?.parentElement;
        if (chatContainer) {
          chatContainer.scrollTo({
            top: 0,
            behavior: 'smooth'
          });
        }
      }, 100);

      try {
        const response = await stockAPI.query(userMessage.content);
        
        // 检查响应是否包含错误
        if (!response || response.success === false) {
          throw new Error(response?.error || 'Invalid response from API');
        }
        
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
        
        let errorContent = '⚠️ 抱歉，查询失败。';
        if (error.response) {
          // 处理HTTP错误
          if (error.response.data?.error) {
            errorContent = `⚠️ ${error.response.data.error}`;
          } else if (error.response.data?.detail) {
            errorContent = `⚠️ ${error.response.data.detail}`;
          } else {
            errorContent += ` 错误状态: ${error.response.status}`;
          }
        } else if (error.request) {
          errorContent = '⚠️ 无法连接到API服务器，请检查网络连接或确认服务是否启动。';
        } else {
          errorContent = `⚠️ ${error.message || '未知错误'}`;
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


  return (
    <div className="flex h-screen bg-claude-background">
      {/* 主容器 - 使用flex布局，背景色#262626（深色主题） */}
      {/* 
        侧边栏 - 支持折叠
        展开宽度：w-sidebar (260px)
        折叠宽度：w-12 (48px)
        背景色：bg-claude-surface (#ffffff)
        边框：border-claude-border (#e5e5e7)
      */}
      <aside className={`${sidebarCollapsed ? 'w-12' : 'w-sidebar'} bg-claude-surface border-r border-claude-border transition-all duration-300 relative`}>
        {/* 折叠按钮 */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-6 w-6 h-6 bg-[#303030] border border-[#404040] rounded-full flex items-center justify-center hover:bg-[#3a3a3a] z-10 transition-all duration-200 text-gray-400 hover:text-white shadow-md"
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
              className="w-8 h-8 flex items-center justify-center text-claude-primary hover:bg-[#1E1E1E] rounded"
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
        {/* Chat Area - Claude.ai风格的内容区域 */}
        <div className="flex-1 overflow-y-auto" style={{ paddingBottom: '200px' }}>
          <div className="mx-auto py-8" style={{ 
            maxWidth: '48rem',
            paddingLeft: '48px',
            paddingRight: '48px'
          }}>
            {messages.length === 0 ? (
              <div className="text-center text-claude-text-secondary py-20">
                <h1 className="text-2xl font-semibold mb-2">
                  智能股票分析系统
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
              <div>
                {messages.map((msg, index) => {
                  // 判断是否为相同发言者的连续消息
                  const isLastFromSameSpeaker = index > 0 && messages[index - 1].role === msg.role;
                  
                  return (
                    <Message 
                      key={msg.id} 
                      message={msg}
                      isLastFromSameSpeaker={isLastFromSameSpeaker}
                      onViewSource={(content, type) => {
                        setDocumentView({ content, type });
                        // 打开文档时自动折叠侧边栏
                        if (!sidebarCollapsed) {
                          setSidebarCollapsed(true);
                        }
                      }}
                    />
                  );
                })}
                {isLoading && (
                  <div className="mb-5">
                    <div className="inline-flex items-center gap-1 px-2 py-1">
                      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area - 无缝融合设计 */}
        <div className={`input-container fixed bottom-0 z-10 transition-all duration-300 ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`} 
             style={{ 
               left: sidebarCollapsed ? '48px' : '260px',
               right: documentView ? '50%' : '0'
             }}>
          {/* 
            顶部渐变背景创造融合效果 - 左右完全透明
            渐变高度：120px
            渐变色：rgb(250,250,250) 到 transparent
          */}
          <div 
            className="absolute inset-x-0 bottom-0 pointer-events-none"
            style={{
              background: 'linear-gradient(to top, rgb(38,38,38) 0%, rgb(38,38,38) 60%, transparent 100%)',  // 深色主题渐变
              height: '120px'
            }}
          />
          
          {/* 输入框包装器 - 减少底部留空 */}
          <div className="relative mx-auto px-6 pb-1" style={{ maxWidth: '48rem' }}>
            <div 
              className="input-wrapper rounded-2xl"
              style={{
                backgroundColor: '#303030',  // 深色主题：输入框背景色
                // 深色主题阴影效果
                boxShadow: '0 0 0 1px rgba(255, 255, 255, 0.1), 0 2px 4px rgba(0, 0, 0, 0.3), 0 4px 8px rgba(0, 0, 0, 0.2)'
              }}
            >
              <SmartInput
                value={input}
                onChange={setInput}
                onSend={handleSend}
                isLoading={isLoading}
              />
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