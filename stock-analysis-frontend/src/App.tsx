import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import TestStreaming from './components/TestStreaming';
import './App.css';

function App() {
  const [showTest, setShowTest] = useState(false);
  
  return (
    <div className="app">
      {/* 测试模式切换按钮 */}
      <div style={{ 
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        zIndex: 1000 
      }}>
        <button 
          onClick={() => setShowTest(!showTest)}
          style={{
            padding: '8px 16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          {showTest ? '返回聊天' : '测试流式显示'}
        </button>
      </div>
      
      {/* 根据状态显示不同组件 */}
      {showTest ? <TestStreaming /> : <ChatInterface />}
    </div>
  );
}

export default App;