import React, { useState } from 'react';
import stockAPI from './services/api';

interface MessageType {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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
          content: response.answer || '没有收到回复',
          timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, assistantMessage]);
      } catch (error) {
        console.error('Query failed:', error);
        const errorMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '抱歉，查询失败。请检查API服务器是否正在运行。错误：' + (error as Error).message,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-4">
          <button 
            onClick={() => setMessages([])}
            className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg"
          >
            New Chat
          </button>
        </div>
        <nav className="p-2">
          <div className="text-gray-500 text-sm p-2">
            No previous chats
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-3xl mx-auto">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-20">
                <h1 className="text-2xl font-semibold mb-2 text-gray-900">
                  Stock Analysis System
                </h1>
                <p>Ask me about stock prices, financial reports, or market analysis</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold text-white ${
                      msg.role === 'user' ? 'bg-blue-500' : 'bg-green-600'
                    }`}>
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className={`flex-1 ${msg.role === 'user' ? 'flex justify-end' : ''}`}>
                      <div className={`inline-block max-w-[70%] px-4 py-2 rounded-lg ${
                        msg.role === 'user' ? 'bg-gray-100' : 'bg-white border border-gray-200'
                      }`}>
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-sm font-semibold">
                      AI
                    </div>
                    <div className="inline-block px-4 py-2 rounded-lg bg-white border border-gray-200">
                      <span>Loading...</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="输入你的问题..."
                disabled={isLoading}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className={`px-6 py-3 rounded-lg font-medium ${
                  input.trim() && !isLoading
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;