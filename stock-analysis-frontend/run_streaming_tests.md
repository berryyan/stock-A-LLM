# 流式响应功能测试执行指南

## 快速开始

### 1. 环境启动
```bash
# 终端1：启动后端API（Windows环境）
cd E:\PycharmProjects\stock_analysis_system
conda activate stock-frontend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：启动前端开发服务器（Windows环境）
cd E:\PycharmProjects\stock_analysis_system\stock-analysis-frontend
npm run dev
```

### 2. 测试工具准备
1. 打开浏览器访问：http://localhost:5173
2. 打开开发者工具（F12）
3. 在新标签页打开测试工具：file:///E:/PycharmProjects/stock_analysis_system/stock-analysis-frontend/test_websocket.html

### 3. 执行测试

#### 测试1：WebSocket连接
```javascript
// 在浏览器控制台执行
console.log('WebSocket状态检查...');
// 查看Network标签中的WS连接
```

#### 测试2：流式显示效果
发送以下查询并观察：
- "茅台最新股价" - 简短响应
- "分析贵州茅台的财务健康度" - 中等长度响应
- "详细分析贵州茅台近一年的经营状况、财务表现、市场地位和未来发展前景" - 长响应

#### 测试3：中断功能
1. 发送查询："分析A股所有银行股的财务状况并排名"
2. 在响应显示到一半时点击"取消"按钮
3. 验证响应停止且显示"(查询已中断)"

#### 测试4：错误处理
1. 停止后端服务
2. 发送查询
3. 验证降级到HTTP且显示错误信息

#### 测试5：性能监控
```javascript
// 在控制台执行性能监控
const startMemory = performance.memory.usedJSHeapSize;
console.log('初始内存:', (startMemory / 1024 / 1024).toFixed(2) + 'MB');

// 发送10个查询后
const endMemory = performance.memory.usedJSHeapSize;
console.log('结束内存:', (endMemory / 1024 / 1024).toFixed(2) + 'MB');
console.log('内存增长:', ((endMemory - startMemory) / 1024 / 1024).toFixed(2) + 'MB');
```

## 测试数据集

### 基础查询
```javascript
const testQueries = [
    "茅台最新股价",
    "600519.SH最近5天的走势",
    "贵州茅台最新公告",
    "分析茅台的财务健康度"
];
```

### 压力测试查询
```javascript
const stressQueries = [
    "分析A股所有白酒股的财务对比",
    "详细分析银行板块的资金流向",
    "对比分析茅台、五粮液、泸州老窖的财务状况"
];
```

### 边界测试
```javascript
const edgeCases = [
    "",  // 空查询
    " ",  // 空格
    "a".repeat(1000),  // 超长查询
    "<script>alert('xss')</script>",  // XSS测试
    "'; DROP TABLE stocks; --"  // SQL注入测试
];
```

## 测试记录表

| 测试项 | 通过 | 失败 | 备注 |
|--------|------|------|------|
| WebSocket自动连接 | ☐ | ☐ | |
| 流式显示效果 | ☐ | ☐ | |
| 打字光标动画 | ☐ | ☐ | |
| 中断查询功能 | ☐ | ☐ | |
| HTTP降级机制 | ☐ | ☐ | |
| 错误处理 | ☐ | ☐ | |
| 内存泄漏检查 | ☐ | ☐ | |
| 并发查询处理 | ☐ | ☐ | |

## 常见问题排查

### WebSocket连接失败
1. 检查后端服务是否运行
2. 检查端口8000是否被占用
3. 查看浏览器控制台错误信息

### 流式显示不工作
1. 确认WebSocket连接成功
2. 检查消息格式是否正确
3. 查看是否有JavaScript错误

### 性能问题
1. 使用Chrome Performance工具分析
2. 检查是否有内存泄漏
3. 监控CPU使用率

---
最后更新：2025-06-27