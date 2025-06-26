import { useState } from 'react';

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
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f7f7f8' }}>
      {/* Sidebar */}
      <aside style={{ width: '260px', backgroundColor: '#ffffff', borderRight: '1px solid #e5e5e7' }}>
        <div style={{ padding: '16px' }}>
          <button 
            onClick={() => setMessages([])}
            style={{ 
              width: '100%', 
              padding: '12px 16px', 
              backgroundColor: '#10a37f', 
              color: 'white', 
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#0d8968'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10a37f'}
          >
            New Chat
          </button>
        </div>
        <nav style={{ padding: '8px' }}>
          <div style={{ color: '#6e6e80', fontSize: '14px', padding: '8px' }}>
            No previous chats
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Chat Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          <div style={{ maxWidth: '768px', margin: '0 auto' }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#6e6e80', paddingTop: '80px' }}>
                <h1 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '8px', color: '#202123' }}>
                  Stock Analysis System
                </h1>
                <p>Ask me about stock prices, financial reports, or market analysis</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {messages.map((msg, idx) => (
                  <div key={idx} style={{ 
                    display: 'flex', 
                    gap: '12px',
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                  }}>
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: msg.role === 'user' ? '#3b82f6' : '#10a37f',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '14px',
                      fontWeight: '600',
                      flexShrink: 0
                    }}>
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div style={{ 
                      flex: 1,
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                    }}>
                      <div style={{
                        display: 'inline-block',
                        maxWidth: '70%',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        backgroundColor: msg.role === 'user' ? '#f7f7f8' : '#ffffff',
                        border: '1px solid #e5e5e7',
                        fontSize: '14px',
                        lineHeight: '1.5'
                      }}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div style={{ borderTop: '1px solid #e5e5e7', padding: '16px', backgroundColor: '#ffffff' }}>
          <div style={{ maxWidth: '768px', margin: '0 auto' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your question..."
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid #e5e5e7',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              <button 
                onClick={handleSend}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#10a37f',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#0d8968'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10a37f'}
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