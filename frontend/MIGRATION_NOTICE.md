# 前端API迁移通知

## 重要提示

从v2.3.0开始，我们推荐使用模块化API（端口8001）以获得更好的性能和功能。

## 快速迁移步骤

### Windows用户
```bash
# 在frontend目录下
copy .env.modular .env
npm run dev
```

### Linux/Mac用户
```bash
# 在frontend目录下
cp .env.modular .env
npm run dev
```

## 为什么要迁移？

1. **性能提升**: 快速查询路径覆盖82.4%，响应速度提升30%
2. **更好的错误提示**: 详细的错误信息帮助快速定位问题
3. **新功能**: 完整的投资价值分析、增强的股票识别等

## 兼容性说明

- ✅ API接口99%兼容，无需修改代码
- ✅ 只需更改配置文件即可
- ✅ 所有功能正常工作

## 回滚方法

如果遇到问题，可以临时切换回原API：

```bash
# 恢复使用原API（端口8000）
# 修改.env文件：
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## 支持

遇到问题请查看：
- 完整迁移指南：`docs/MIGRATION_GUIDE.md`
- API文档：http://localhost:8001/docs
- 提交Issue：GitHub Issues

---

**注意**: 原API（端口8000）将在v2.4.0（2025年10月）完全移除，请尽快完成迁移。