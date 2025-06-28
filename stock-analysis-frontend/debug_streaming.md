# 流式响应调试指南

## 1. 在浏览器控制台执行以下命令检查状态

```javascript
// 检查是否有WebSocket连接
const sockets = Array.from(window.performance.getEntriesByType('resource'))
  .filter(entry => entry.name.includes('ws://'));
console.log('WebSocket连接:', sockets);

// 手动创建WebSocket测试
const testWs = new WebSocket('ws://localhost:8000/ws');
testWs.onopen = () => console.log('测试WebSocket连接成功');
testWs.onerror = (e) => console.error('测试WebSocket错误:', e);
testWs.onmessage = (e) => console.log('测试WebSocket消息:', e.data);

// 发送测试消息
setTimeout(() => {
  if (testWs.readyState === WebSocket.OPEN) {
    testWs.send(JSON.stringify({
      type: 'query',
      question: '茅台最新股价'
    }));
  }
}, 1000);
```

## 2. 检查React组件状态

在React DevTools中查看：
1. ChatInterface组件的state
2. 特别注意 `isLoading` 状态
3. 查看 `messages` 数组中最后一条消息的 `isStreaming` 属性

## 3. 网络请求检查

在Network标签中：
1. 过滤"WS"查看WebSocket连接
2. 点击WebSocket连接查看Messages
3. 确认是否有消息往来

## 4. 添加临时调试代码

在 ChatInterface.tsx 的 handleSend 函数开头添加：
```javascript
console.log('=== handleSend 开始 ===');
console.log('wsServiceRef.current:', wsServiceRef.current);
console.log('isConnected:', wsServiceRef.current?.isConnected());
```

## 5. 验证环境变量

在控制台执行：
```javascript
console.log('VITE_WS_HOST:', import.meta.env.VITE_WS_HOST);
console.log('VITE_WS_PORT:', import.meta.env.VITE_WS_PORT);
console.log('window.location.hostname:', window.location.hostname);
```

## 6. 检查取消按钮

查看CSS样式是否正确加载：
```javascript
// 检查是否有.cancel-button样式
const styles = Array.from(document.styleSheets)
  .flatMap(sheet => {
    try {
      return Array.from(sheet.cssRules || []);
    } catch (e) {
      return [];
    }
  })
  .filter(rule => rule.selectorText && rule.selectorText.includes('cancel-button'));
console.log('Cancel button styles:', styles);

// 手动查找取消按钮
document.querySelector('.cancel-button');
```

## 7. 验证流式显示函数

在控制台直接测试：
```javascript
// 模拟流式显示
const testStreaming = (text) => {
  let index = 0;
  const interval = setInterval(() => {
    if (index <= text.length) {
      console.log(text.substring(0, index));
      index++;
    } else {
      clearInterval(interval);
    }
  }, 50);
};

testStreaming('这是一个测试文本');
```