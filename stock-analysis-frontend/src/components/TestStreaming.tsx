import React, { useState, useRef } from 'react';

const TestStreaming: React.FC = () => {
  const [text, setText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const startStreaming = () => {
    const fullText = '这是一个测试流式响应的示例文本。每个字符将逐个显示，模拟打字效果。这样可以验证流式显示功能是否正常工作。';
    let currentIndex = 0;
    
    setText('');
    setIsStreaming(true);
    
    intervalRef.current = setInterval(() => {
      if (currentIndex < fullText.length) {
        setText(fullText.substring(0, currentIndex + 1));
        currentIndex++;
      } else {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setIsStreaming(false);
      }
    }, 50);
  };
  
  const stopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setText(text + '\n\n*(已中断)*');
    setIsStreaming(false);
  };
  
  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>流式响应测试组件</h2>
      
      <div style={{ 
        marginBottom: '20px', 
        padding: '20px', 
        border: '1px solid #ddd', 
        borderRadius: '8px',
        minHeight: '100px',
        backgroundColor: '#f9f9f9'
      }}>
        {text}
        {isStreaming && <span className="typing-cursor"></span>}
      </div>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <button 
          onClick={startStreaming} 
          disabled={isStreaming}
          style={{
            padding: '10px 20px',
            backgroundColor: isStreaming ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isStreaming ? 'not-allowed' : 'pointer'
          }}
        >
          开始流式显示
        </button>
        
        {isStreaming && (
          <button 
            onClick={stopStreaming}
            style={{
              padding: '10px 20px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            中断
          </button>
        )}
      </div>
      
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
        <p>状态：{isStreaming ? '正在流式显示...' : '空闲'}</p>
        <p>字符数：{text.length}</p>
      </div>
    </div>
  );
};

export default TestStreaming;