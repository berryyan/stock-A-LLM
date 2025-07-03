# 版本更新说明 v2.1.15

**发布日期**: 2025-07-04  
**版本号**: v2.1.15

## 🎨 主题系统实现

### 新功能
1. **完整的主题切换系统**
   - 创建 `ThemeContext` 上下文管理主题状态
   - 支持手动切换亮色/暗色模式
   - 主题偏好保存到本地存储
   - 初始化时优先使用用户设置，其次系统偏好

2. **侧边栏主题切换按钮**
   - 在侧边栏底部添加主题切换按钮
   - 支持折叠状态下的图标显示
   - 优雅的过渡动画效果

3. **Markdown表格样式优化**
   - 修复暗色模式下表格标题可读性问题
   - 表格标题在暗色模式下使用浅色背景+黑色文字
   - 确保在两种主题下都有良好的对比度

### 样式改进
1. **全局主题支持**
   - 所有组件支持亮色/暗色主题切换
   - 使用 Tailwind 的 `dark:` 前缀实现条件样式
   - 配置 `darkMode: 'class'` 支持手动控制

2. **组件样式更新**
   - **App主容器**: 亮色背景白色，暗色背景深灰
   - **侧边栏**: 亮色模式浅灰背景，暗色模式深灰背景
   - **消息气泡**: 用户消息支持两种主题配色
   - **输入框**: 文字颜色和占位符适配主题
   - **工具栏**: 边框和文字颜色主题适配

3. **输入区域优化**
   - 输入框背景色支持主题切换
   - 渐变效果适配两种主题
   - 阴影效果优化

### 技术实现
- 使用 React Context API 管理主题状态
- Tailwind CSS `darkMode: 'class'` 配置
- localStorage 持久化用户偏好
- 系统偏好检测作为默认值

### 文件变更
- 新增: `src/contexts/ThemeContext.tsx`
- 新增: `src/components/common/ThemeToggle.tsx`
- 修改: `tailwind.config.js` - 添加 darkMode 配置
- 修改: `src/main.tsx` - 添加 ThemeProvider
- 修改: `src/App.tsx` - 添加主题切换按钮和样式更新
- 修改: `src/components/common/MarkdownRenderer.tsx` - 表格样式优化
- 修改: `src/components/chat/Message.tsx` - 消息样式主题支持
- 修改: `src/components/input/SmartInput.tsx` - 输入框样式主题支持

## 下一步计划
- 优化更多组件的主题样式
- 添加主题切换的键盘快捷键
- 考虑添加更多主题选项