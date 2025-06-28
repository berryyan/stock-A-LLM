import { useState, useRef, useEffect } from 'react';
import { Message } from './components/chat/Message';
import { DocumentViewer } from './components/document/DocumentViewer';
import { SmartInput } from './components/input/SmartInput';
import { useStreamingResponse } from './hooks/useStreamingResponse';
import type { Message as MessageType } from './types';
import stockAPI from './services/api';

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documentView, setDocumentView] = useState<{content: any; type: string} | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 使用流式响应Hook
  const { isStreaming, startStreaming, stopStreaming } = useStreamingResponse({
    onComplete: () => {
      console.log('流式响应完成');
    }
  });

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
      
      // 添加空的助手消息作为占位符
      const assistantMessageId = (Date.now() + 1).toString();
      const assistantMessage: MessageType = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true,
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      try {
        const response = await stockAPI.query(userMessage.content);
        
        // 检查响应是否包含错误
        if (!response || response.success === false) {
          throw new Error(response?.error || 'Invalid response from API');
        }
        
        // 使用流式显示响应内容
        const fullContent = response.answer;
        
        startStreaming(fullContent, (streamedText) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: streamedText, isStreaming: true }
                : msg
            )
          );
        });
        
        // 流式完成后更新消息状态和sources
        setTimeout(() => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, sources: response.sources, isStreaming: false }
                : msg
            )
          );
        }, Math.ceil(fullContent.length / 3) * 30 + 100); // 根据内容长度计算完成时间

      } catch (error: any) {
        console.error('Query failed:', error);
        
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
          errorContent = `⚠️ ${error.message || '发生未知错误'}`;
        }
        
        // 更新错误消息
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, content: errorContent, isStreaming: false, isError: true }
              : msg
          )
        );
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleViewDocument = (doc: {content: any; type: string}) => {
    console.log('Viewing document:', doc);
    setDocumentView(doc);
    // 打开文档时自动折叠侧边栏
    setSidebarCollapsed(true);
  };

  const quickActions = [
    { id: 1, label: '茅台财务分析', query: '分析贵州茅台的财务健康度' },
    { id: 2, label: '茅台资金流向', query: '茅台最近的主力资金流向' },
    { id: 3, label: '平安技术分析', query: '平安银行的技术走势分析' },
    { id: 4, label: '市值排行榜', query: 'A股市值排名前10' },
  ];

  const handleQuickAction = (query: string) => {
    setInput(query);
    handleSend();
  };

  // 以下是原有的渲染部分，保持不变...
  return (
    <div className="flex h-screen bg-claude-background">
      {/* 侧边栏 */}
      <aside className={`${sidebarCollapsed ? 'w-0' : 'w-sidebar'} bg-claude-surface border-r border-claude-border transition-all duration-300 relative`}>
        {/* 折叠按钮 */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-6 w-6 h-6 bg-claude-surface border border-claude-border rounded-full flex items-center justify-center hover:bg-claude-primary-hover transition-colors z-10"
        >
          <svg 
            className={`w-4 h-4 transition-transform ${sidebarCollapsed ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        {!sidebarCollapsed && (
          <div className="p-4">
            <h1 className="text-2xl font-semibold mb-2">AI 股票分析</h1>
            <p className="text-sm text-claude-text-secondary">智能投资决策助手</p>
            
            {/* 快速操作 */}
            <div className="mt-8 space-y-2">
              <h3 className="text-xs text-claude-text-secondary mb-2">快速查询</h3>
              {quickActions.map(action => (
                <button
                  key={action.id}
                  onClick={() => handleQuickAction(action.query)}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-claude-primary-hover text-sm transition-colors"
                  disabled={isLoading}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex">
        {/* 聊天区域 */}
        <div className={`flex-1 flex flex-col ${documentView ? 'w-1/2' : 'w-full'}`}>
          {/* 聊天消息区域 */}
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto py-8 px-4" style={{ maxWidth: '768px' }}>
              {messages.length === 0 ? (
                <div className="text-center py-20">
                  <h2 className="text-2xl font-semibold mb-2">👋 你好，我是AI股票分析助手</h2>
                  <p className="text-claude-text-secondary">
                    我可以帮你分析股票财务数据、技术走势、资金流向等
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <Message 
                    key={message.id} 
                    message={message} 
                    onViewDocument={handleViewDocument}
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* 输入区域 */}
          <div className="border-t border-claude-border">
            <div className="mx-auto p-4" style={{ maxWidth: '768px' }}>
              <SmartInput
                value={input}
                onChange={setInput}
                onKeyPress={handleKeyPress}
                disabled={isLoading || isStreaming}
                placeholder={isLoading ? "AI正在思考中..." : "输入你的问题..."}
              />
              
              {/* 流式响应时显示停止按钮 */}
              {isStreaming && (
                <button
                  onClick={stopStreaming}
                  className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  停止生成
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 文档查看器 */}
        {documentView && (
          <div className="w-1/2 border-l border-claude-border">
            <DocumentViewer
              content={documentView.content}
              type={documentView.type}
              onClose={() => {
                setDocumentView(null);
                setSidebarCollapsed(false);
              }}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;