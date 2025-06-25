# 错误消息传播修复说明

## 问题描述
用户反馈：在2025-06-25 17:00:19时，当输入错误的股票代码（如"02359"）时，后端日志显示了正确的错误消息"股票代码长度不正确"，但前端只显示空白对话气泡。

## 问题原因分析

### 错误传播链路
1. **Financial Agent** (`financial_agent.py`):
   - 检测到无效股票代码时，正确返回错误消息
   ```python
   return {
       'success': False,
       'error': '股票代码格式不正确，请输入6位数字',
       'type': 'financial_query'
   }
   ```

2. **Hybrid Agent** (`hybrid_agent.py`):
   - 正确传递错误消息
   ```python
   return {
       'success': False,
       'question': question,
       'error': financial_result.get('error', '财务分析失败'),
       'query_type': QueryType.FINANCIAL.value,
       'routing': routing
   }
   ```

3. **API WebSocket** (`main.py`):
   - 将整个result对象放入content字段
   ```python
   {
       "type": "analysis_result",
       "query_id": query_id,
       "content": result,  # 包含 success: false 和 error 字段
       "timestamp": datetime.now().isoformat()
   }
   ```

4. **前端JavaScript** (`index.html`):
   - **BUG所在**：`formatAnalysisResult`函数只查找`data.answer`或`data.content`
   - 当`data.content`是一个包含错误的对象时，没有正确提取`error`字段
   - 导致返回空字符串，显示空白气泡

## 修复方案

### 1. 修改`formatAnalysisResult`函数
在函数开头添加错误检查：
```javascript
// 检查是否是错误响应
if (data.content && typeof data.content === 'object' && data.content.success === false) {
    // 返回错误消息
    return `❌ ${data.content.error || '分析失败：未知错误'}`;
}
```

### 2. 修改WebSocket消息处理
在`handleWebSocketMessage`函数中，对`analysis_result`类型的消息增加错误检查：
```javascript
if (data.content && typeof data.content === 'object' && data.content.success === false) {
    // 直接显示错误消息
    addMessage('assistant', `❌ ${data.content.error || '分析失败：未知错误'}`, false);
} else {
    // 正常格式化并显示结果
    addMessage('assistant', formatAnalysisResult(data), true);
}
```

## 测试验证
创建了`test_error_propagation.py`测试脚本，可以验证各种错误情况下的消息传播。

## 影响范围
- 主要影响文件：`templates/index.html`
- 修复后，所有通过WebSocket返回的错误消息都能正确显示在前端

## 建议
1. 考虑统一API的错误响应格式
2. 在WebSocket层面区分成功和失败的消息类型
3. 添加前端错误消息的样式优化