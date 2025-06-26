import React, { useState } from 'react';

function App() {
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { role: 'user', content: input }]);
      // TODO: Call API
      setMessages(prev => [...prev, { role: 'assistant', content: 'This is a demo response. The API integration is coming soon!' }]);
      setInput('');
    }
  };

  return (
    <div className="flex h-screen bg-claude-background">
      {/* Sidebar */}
      <aside className="w-sidebar bg-claude-surface border-r border-claude-border">
        <div className="p-4">
          <button className="w-full px-4 py-3 bg-claude-primary hover:bg-claude-primary-hover text-white rounded-lg transition-colors">
            New Chat
          </button>
        </div>
        <nav className="p-2">
          <div className="text-claude-text-secondary text-sm p-2">
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
              <div className="text-center text-claude-text-secondary py-20">
                <h1 className="text-2xl font-semibold mb-2">
                  Stock Analysis System
                </h1>
                <p>Ask me about stock prices, financial reports, or market analysis</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-semibold ${
                      msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-claude-primary text-white'
                    }`}>
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className={`flex-1 ${msg.role === 'user' ? 'flex justify-end' : ''}`}>
                      <div className={`inline-block max-w-[70%] px-4 py-2 rounded-lg ${
                        msg.role === 'user' ? 'bg-claude-surface border border-claude-border' : 'bg-white border border-claude-border'
                      }`}>
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-claude-border p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your question..."
                className="flex-1 px-4 py-3 border border-claude-border rounded-lg focus:outline-none focus:ring-2 focus:ring-claude-primary"
              />
              <button 
                onClick={handleSend}
                className="px-6 py-3 bg-claude-primary hover:bg-claude-primary-hover text-white rounded-lg transition-colors"
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