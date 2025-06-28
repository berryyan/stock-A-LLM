// 在浏览器控制台执行此代码来添加测试功能

// 创建测试按钮
const testButton = document.createElement('button');
testButton.textContent = '测试流式显示';
testButton.style.cssText = `
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 10000;
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
`;

// 创建测试容器
const testContainer = document.createElement('div');
testContainer.style.cssText = `
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10001;
  display: none;
`;

testContainer.innerHTML = `
  <h2>流式响应测试</h2>
  <div id="test-display" style="
    margin: 20px 0;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 4px;
    min-height: 100px;
    font-family: monospace;
  ">
    点击"开始测试"查看效果
  </div>
  <div>
    <button id="start-test" style="
      padding: 10px 20px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      margin-right: 10px;
    ">开始测试</button>
    <button id="close-test" style="
      padding: 10px 20px;
      background: #6c757d;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    ">关闭</button>
  </div>
`;

document.body.appendChild(testButton);
document.body.appendChild(testContainer);

// 测试功能
let streamingInterval = null;

testButton.onclick = () => {
  testContainer.style.display = 'block';
};

document.getElementById('close-test').onclick = () => {
  testContainer.style.display = 'none';
  if (streamingInterval) {
    clearInterval(streamingInterval);
    streamingInterval = null;
  }
};

document.getElementById('start-test').onclick = () => {
  const display = document.getElementById('test-display');
  const text = '这是一个流式响应测试。每个字符会逐个显示，模拟ChatGPT的打字效果。如果你能看到文字逐个出现，说明流式显示功能正常工作。';
  let index = 0;
  
  display.innerHTML = '';
  
  if (streamingInterval) {
    clearInterval(streamingInterval);
  }
  
  streamingInterval = setInterval(() => {
    if (index < text.length) {
      display.innerHTML = text.substring(0, index + 1) + '<span style="display:inline-block;width:2px;height:1em;background:#333;animation:blink 1s infinite;"></span>';
      index++;
    } else {
      display.innerHTML = text;
      clearInterval(streamingInterval);
      streamingInterval = null;
    }
  }, 50);
};

// 添加闪烁动画
const style = document.createElement('style');
style.textContent = `
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
`;
document.head.appendChild(style);

console.log('✅ 测试功能已加载，点击右上角绿色按钮开始测试');

// 测试WebSocket
console.log('🔍 测试WebSocket连接...');
const testWs = new WebSocket('ws://localhost:8000/ws');
testWs.onopen = () => console.log('✅ WebSocket测试连接成功');
testWs.onerror = (e) => console.error('❌ WebSocket测试连接失败:', e);
testWs.onmessage = (e) => console.log('📨 WebSocket消息:', e.data);