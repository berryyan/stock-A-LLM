# 前端错误显示问题调试

## 问题描述
当后端返回 `success: false` 和错误信息时，前端显示"查询过程中出现未知错误"而不是具体的错误信息。

## 问题分析

### 1. 后端返回格式（正确）
```json
{
  "success": false,
  "question": "INVALID123的股价",
  "answer": "",
  "error": "无法识别股票代码：INVALID123",
  "query_type": "unknown",
  "timestamp": "2025-07-06T15:35:00"
}
```

### 2. 前端处理逻辑（有问题）
前端代码在第88-100行检查了 `success === false`，但是：
- 错误消息被正确设置了
- 但是后续的流式显示逻辑可能仍在执行
- 或者catch块中的通用错误处理覆盖了具体错误

## 调试步骤

1. **打开浏览器开发者工具（F12）**
2. **在Console标签中查看日志**
3. **输入一个错误查询，如："INVALID123的股价"**
4. **观察Console中的输出**：
   - 是否显示了"API Response:"日志
   - response.data中是否包含error字段
   - 是否有其他错误信息

## 可能的修复方案

### 方案1：确保错误处理后不执行流式显示
```typescript
if (!response || response.success === false) {
  const errorContent = `⚠️ ${response?.error || '查询失败，请稍后重试'}`;
  
  setMessages(prev => 
    prev.map(msg => 
      msg.id === assistantMessageId 
        ? { ...msg, content: errorContent, isStreaming: false, isError: true }
        : msg
    )
  );
  return; // 确保这里return后不会执行后续代码
}
```

### 方案2：在catch块中添加更多日志
```typescript
} catch (error: any) {
  console.error('Query failed - Full error:', error);
  console.error('Error type:', error.constructor.name);
  console.error('Error response:', error.response);
  // ...
}
```

## 请提供的信息

1. 浏览器Console中的完整日志输出
2. Network标签中API请求的响应内容
3. 是否看到了"API Response:"的日志