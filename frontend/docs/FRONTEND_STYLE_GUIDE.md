# 前端组件样式调整操作手册

本手册详细说明了如何在PyCharm中直接调整前端组件的颜色、间距、圆角等样式配置。

## 一、组件文件路径清单

### 核心组件
| 组件名称 | 文件路径 | 功能说明 |
|---------|---------|---------|
| 主应用 | `frontend/src/App.tsx` | 整体布局、消息管理、滚动控制 |
| 消息组件 | `frontend/src/components/chat/Message.tsx` | 用户/AI消息显示、复制功能 |
| 头像组件 | `frontend/src/components/common/Avatar.tsx` | 用户/AI头像显示 |
| Markdown渲染器 | `frontend/src/components/common/MarkdownRenderer.tsx` | 富文本内容渲染 |
| 输入框组件 | `frontend/src/components/input/SmartInput.tsx` | 智能输入框、自动高度调整 |
| 文档查看器 | `frontend/src/components/document/DocumentViewer.tsx` | 侧边栏文档显示 |

### 样式配置文件
| 文件名 | 路径 | 说明 |
|--------|------|------|
| Tailwind配置 | `frontend/tailwind.config.js` | 主题色、自定义样式类 |
| 全局样式 | `frontend/src/index.css` | 全局CSS、动画定义 |

## 二、常见样式调整指南

### 1. 用户消息气泡样式
**文件**: `frontend/src/components/chat/Message.tsx`
**位置**: 第54-77行

```javascript
// 当前配置
style={{
  maxWidth: '95%',           // 最大宽度（可调整为70%-100%）
  backgroundColor: '#F0EEE6', // 气泡背景色（米色）
  padding: '8px 14px 8px 8px', // 内边距（上 右 下 左）
  borderRadius: '8px',        // 圆角大小（4px-20px）
}}

// 文字样式（第71-74行）
style={{ 
  color: '#000000',          // 文字颜色
}}
```

**调整建议**：
- 圆角大小：`4px`（方形）、`8px`（微圆）、`12px`（圆润）、`18px`（很圆）
- 内边距：增加数值让气泡更宽松，减少数值让气泡更紧凑

### 2. 用户头像样式
**文件**: `frontend/src/components/common/Avatar.tsx`
**位置**: 第17-23行

```javascript
style={{
  backgroundColor: isUser ? '#3D3D3A' : undefined,  // 用户头像背景色
  color: isUser ? '#FFFFFF' : undefined,            // 用户头像文字颜色
}}
```

**调整建议**：
- 深色系：`#2C2C2C`（更深）、`#3D3D3A`（当前）、`#4A4A4A`（稍浅）
- 头像大小：在Message.tsx第71行调整 `size={24}`，建议范围20-32

### 3. AI消息样式
**文件**: `frontend/src/components/chat/Message.tsx`
**位置**: 第83行

```javascript
<div className="ai-message pl-12">  // pl-12 = 左侧内边距48px
```

**调整建议**：
- `pl-8`（32px）：更靠左
- `pl-10`（40px）：稍微靠左
- `pl-12`（48px）：当前值
- `pl-16`（64px）：更靠右

### 4. 全局背景色
**文件**: `frontend/tailwind.config.js`
**位置**: 第13行

```javascript
'claude-background': '#FAF9F5',  // 主背景色（浅米色）
```

**调整建议**：
- 纯白：`#FFFFFF`
- 浅灰：`#F7F7F8`
- 米色系：`#FAF9F5`（当前）、`#FFF9F0`（偏暖）
- 蓝灰：`#F0F4F8`

### 5. 输入框样式
**文件**: `frontend/src/components/input/SmartInput.tsx`
**位置**: 第94-98行

```javascript
style={{
  minHeight: '40px',    // 最小高度
  maxHeight: '240px',   // 最大高度
  lineHeight: '20px'    // 行高
}}
```

**文件**: `frontend/src/App.tsx`
**位置**: 第248-252行（输入框容器阴影）

```javascript
boxShadow: '0 0 0 1px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.05)'
```

### 6. 按钮样式
**文件**: `frontend/src/components/input/SmartInput.tsx`
**位置**: 第114-116行

```javascript
// 激活状态
'bg-claude-primary hover:bg-claude-primary-hover text-white'
// 禁用状态  
'bg-gray-100 text-gray-400 cursor-not-allowed'
```

**主题色调整**：
文件：`frontend/tailwind.config.js`
```javascript
'claude-primary': '#10a37f',        // 主色（绿色）
'claude-primary-hover': '#0d8968',  // 悬停色（深绿）
```

### 7. 消息间距
**文件**: `frontend/src/components/chat/Message.tsx`
**位置**: 第29-32行

```javascript
// 动态计算消息间距
const messageSpacing = isLastFromSameSpeaker ? 'mb-3' : 'mb-6';
// mb-3 = 12px（同一发言者）
// mb-6 = 24px（不同发言者）
```

**调整建议**：
- 紧凑：`mb-2`（8px）/ `mb-4`（16px）
- 标准：`mb-3`（12px）/ `mb-6`（24px）当前值
- 宽松：`mb-4`（16px）/ `mb-8`（32px）

## 三、快速调整技巧

### 1. 颜色选择器
在PyCharm中：
- 点击颜色值（如`#F0EEE6`）左侧的颜色方块
- 使用内置颜色选择器调整
- 实时预览效果

### 2. 间距单位对照
Tailwind CSS间距类：
- `p-1` = 4px
- `p-2` = 8px
- `p-3` = 12px
- `p-4` = 16px
- `p-6` = 24px
- `p-8` = 32px

### 3. 圆角大小参考
- `rounded-sm` = 2px
- `rounded` = 4px
- `rounded-md` = 6px
- `rounded-lg` = 8px
- `rounded-xl` = 12px
- `rounded-2xl` = 16px
- `rounded-3xl` = 24px
- `rounded-full` = 9999px（完全圆形）

### 4. 阴影效果
```javascript
// 轻微阴影
boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'

// 标准阴影（当前输入框使用）
boxShadow: '0 0 0 1px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.05)'

// 深层阴影
boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)'
```

## 四、调试和测试

### 1. 实时预览
修改文件后，Vite会自动热更新，无需手动刷新浏览器。

### 2. 开发者工具
- F12打开Chrome开发者工具
- 使用元素检查器查看实际渲染的样式
- 在Styles面板中实时调整CSS值

### 3. 响应式测试
- 使用Chrome设备模拟器测试不同屏幕尺寸
- 特别注意移动端（<768px）的显示效果

## 五、注意事项

1. **保持一致性**：调整样式时注意整体视觉协调
2. **备份修改**：重大修改前先git commit
3. **性能考虑**：避免过度使用阴影和动画
4. **可访问性**：确保颜色对比度符合WCAG标准
5. **浏览器兼容**：测试Chrome、Firefox、Safari等主流浏览器

## 六、常用配色方案

### 专业商务风
```javascript
背景色: '#FFFFFF'
气泡色: '#F5F5F5'
头像色: '#333333'
文字色: '#1A1A1A'
主题色: '#0066CC'
```

### 温暖米色系（当前）
```javascript
背景色: '#FAF9F5'
气泡色: '#F0EEE6'
头像色: '#3D3D3A'
文字色: '#000000'
主题色: '#10a37f'
```

### 现代深色风
```javascript
背景色: '#1E1E1E'
气泡色: '#2D2D30'
头像色: '#4A4A4A'
文字色: '#E0E0E0'
主题色: '#4CAF50'
```

### 清新蓝绿系
```javascript
背景色: '#F0F7FF'
气泡色: '#E6F3FF'
头像色: '#2C5282'
文字色: '#1A365D'
主题色: '#3182CE'
```

## 七、Git提交前检查清单

- [ ] 颜色值格式正确（#RRGGBB）
- [ ] 间距值使用Tailwind类或具体像素值
- [ ] 圆角大小协调统一
- [ ] 移动端显示正常
- [ ] 深色模式兼容（如果支持）
- [ ] 无语法错误（ESLint通过）

---

最后更新：2025-06-27
版本：v1.0