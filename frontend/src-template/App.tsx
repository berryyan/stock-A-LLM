import React from 'react';
import './styles/globals.css';

function App() {
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
          {/* Chat history will go here */}
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
            <div className="text-center text-claude-text-secondary py-20">
              <h1 className="text-2xl font-semibold mb-2">
                Stock Analysis System
              </h1>
              <p>Ask me about stock prices, financial reports, or market analysis</p>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-claude-border p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Type your question..."
                className="flex-1 px-4 py-3 border border-claude-border rounded-lg focus:outline-none focus:ring-2 focus:ring-claude-primary"
              />
              <button className="px-6 py-3 bg-claude-primary hover:bg-claude-primary-hover text-white rounded-lg transition-colors">
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