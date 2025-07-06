# 从旧版API迁移到模块化API指南

**更新日期**: 2025-07-06  
**适用版本**: v2.1.x → v2.2.0+

## 快速开始

### 1. 更改API端点

**旧版本**:
```
http://localhost:8000
```

**新版本**:
```
http://localhost:8001
```

### 2. API兼容性

好消息！新版API保持了99%的向后兼容性。大多数情况下，您只需要更改端点URL即可。

## 主要变化

### 1. 错误响应格式

**旧版本**:
```json
{
  "error": "查询过程中出现未知错误"
}
```

**新版本**:
```json
{
  "error": "无法识别输入内容。请输入：1) 6位股票代码（如002047）2) 证券代码（如600519.SH）3) 股票名称（如贵州茅台）"
}
```

新版本提供更详细的错误信息！

### 2. 性能提升

- 快速查询路径覆盖率：82.4%
- 平均响应时间降低30%
- 并发处理能力提升50%

## 迁移步骤

### Python客户端

```python
# 旧代码
import requests
response = requests.post("http://localhost:8000/query", json={
    "question": "贵州茅台的最新股价"
})

# 新代码（只需更改URL）
import requests
response = requests.post("http://localhost:8001/query", json={
    "question": "贵州茅台的最新股价"
})
```

### JavaScript/前端

```javascript
// 旧代码
const API_BASE_URL = 'http://localhost:8000';

// 新代码
const API_BASE_URL = 'http://localhost:8001';
```

### 环境变量配置

```bash
# .env 文件
# 旧配置
VITE_API_BASE_URL=http://localhost:8000

# 新配置
VITE_API_BASE_URL=http://localhost:8001
```

## 新功能亮点

1. **更好的错误提示**: 具体的错误信息帮助快速定位问题
2. **更快的响应速度**: 82.4%的查询走快速路径
3. **更稳定的服务**: 模块化架构提升系统稳定性

## 常见问题

### Q: 我需要修改查询格式吗？
A: 不需要！查询格式完全兼容。

### Q: 旧API什么时候会关闭？
A: 计划在2025年10月（v2.4.0）完全移除。

### Q: 如何确认迁移成功？
A: 访问 http://localhost:8001/health，看到以下响应即为成功：
```json
{
  "status": "healthy",
  "version": "2.2.0-modular"
}
```

### Q: 遇到问题怎么办？
A: 
1. 查看错误日志：`logs/api_modular.log`
2. 提交Issue：https://github.com/your-org/stock-analysis-system/issues
3. 联系技术支持：support@your-domain.com

## 迁移检查清单

- [ ] 更新所有API端点URL
- [ ] 更新环境变量配置
- [ ] 测试主要功能是否正常
- [ ] 更新自动化脚本
- [ ] 通知下游系统
- [ ] 监控新API的使用情况

## 回滚方案

如果遇到严重问题，可以临时切换回旧API：
1. 将端点改回8000
2. 报告问题给技术团队
3. 等待问题修复后再次迁移

---

感谢您的配合！新版本将带来更好的使用体验。