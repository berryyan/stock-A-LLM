# 前端环境配置指南

## 环境文件说明

本项目支持多种环境配置，通过不同的 `.env` 文件来管理：

### 环境文件列表

1. **`.env.development`** - 开发环境配置
   - 用于本地开发
   - API指向 `localhost:8000`
   - 启用调试模式和开发工具

2. **`.env.production`** - 生产环境配置
   - 用于正式部署
   - API指向生产服务器
   - 关闭调试模式，优化性能

3. **`.env.staging`** - 预发布/测试环境配置
   - 用于内部测试
   - API指向内网测试服务器
   - 保留调试功能

4. **`.env.local`** - 本地覆盖配置（不提交到Git）
   - 用于个人开发环境的特殊配置
   - 优先级最高，会覆盖其他环境文件

### 特殊环境文件

- **`.env.local.wsl2`** - WSL2专用配置（示例）
- **`.env.local.windows`** - Windows专用配置（示例）

## 环境变量说明

### 核心配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | API基础URL | `http://localhost:8000` |
| `VITE_WS_BASE_URL` | WebSocket基础URL | `ws://localhost:8000` |
| `VITE_ENV` | 当前环境标识 | `development` / `production` / `staging` |
| `VITE_DEBUG` | 是否启用调试模式 | `true` / `false` |
| `VITE_API_TIMEOUT` | API请求超时时间（毫秒） | `120000` |

### 开发工具配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_ENABLE_DEV_TOOLS` | 启用开发者工具 | `true` (开发) / `false` (生产) |
| `VITE_ENABLE_SOURCE_MAP` | 启用源码映射 | `true` (开发) / `false` (生产) |

### 可选配置

| 变量名 | 说明 | 用途 |
|--------|------|------|
| `VITE_ANALYTICS_ID` | 分析工具ID | 生产环境数据分析 |
| `VITE_SENTRY_DSN` | Sentry错误追踪DSN | 生产环境错误监控 |
| `VITE_ENABLE_TEST_FEATURES` | 启用测试功能 | 测试环境专用功能 |

## 使用方法

### 开发环境

```bash
# 使用开发环境配置启动
npm run dev

# 或明确指定
npm run dev -- --mode development
```

### 生产构建

```bash
# 生产环境构建
npm run build

# 或明确指定
npm run build -- --mode production
```

### 测试环境

```bash
# 使用staging配置
npm run dev -- --mode staging
npm run build -- --mode staging
```

### WSL2开发环境特殊配置

在WSL2环境中开发时，需要特殊处理API访问：

1. 创建 `.env.local` 文件（已包含在 `.gitignore` 中）
2. 配置Windows主机IP：

```bash
# .env.local
VITE_API_BASE_URL=http://10.0.0.66:8000
VITE_WS_BASE_URL=ws://10.0.0.66:8000
```

3. 获取Windows主机IP的方法：
```bash
# 在WSL2中执行
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

## 环境切换脚本

### 快速切换环境配置

```bash
# 创建切换脚本
cat > switch-env.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./switch-env.sh [wsl2|windows|dev]"
  exit 1
fi

case $1 in
  wsl2)
    cp .env.local.wsl2 .env.local
    echo "Switched to WSL2 environment"
    ;;
  windows)
    cp .env.local.windows .env.local
    echo "Switched to Windows environment"
    ;;
  dev)
    rm -f .env.local
    echo "Switched to default development environment"
    ;;
  *)
    echo "Unknown environment: $1"
    exit 1
    ;;
esac
EOF

chmod +x switch-env.sh
```

## 环境配置最佳实践

1. **不要提交** `.env.local` 文件到Git
2. **生产环境密钥** 应通过CI/CD环境变量注入，不要硬编码
3. **保持环境一致性** - 确保所有开发者使用相同的环境变量名
4. **文档化所有变量** - 新增环境变量时更新此文档
5. **使用类型安全** - 在TypeScript中定义环境变量类型

### TypeScript类型定义示例

```typescript
// src/types/env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_ENV: 'development' | 'production' | 'staging'
  readonly VITE_DEBUG: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_ENABLE_DEV_TOOLS: string
  readonly VITE_ENABLE_SOURCE_MAP: string
  readonly VITE_ANALYTICS_ID?: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_ENABLE_TEST_FEATURES?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## 故障排查

### 常见问题

1. **API连接失败**
   - 检查 `VITE_API_BASE_URL` 是否正确
   - WSL2环境确认使用Windows主机IP
   - 确认后端服务已启动

2. **环境变量未生效**
   - 重启开发服务器
   - 检查变量名是否以 `VITE_` 开头
   - 确认 `.env` 文件在项目根目录

3. **构建失败**
   - 检查生产环境配置是否完整
   - 确认所有必需的环境变量都已设置

### 调试技巧

```javascript
// 在代码中查看当前环境配置
console.log('Environment:', import.meta.env.VITE_ENV);
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
console.log('Debug mode:', import.meta.env.VITE_DEBUG);
```

## 部署注意事项

1. **生产部署前检查清单**
   - [ ] 更新 `.env.production` 中的API地址
   - [ ] 确认关闭调试模式
   - [ ] 设置正确的超时时间
   - [ ] 配置监控和分析工具

2. **环境隔离**
   - 开发、测试、生产环境应使用不同的API端点
   - 避免测试数据污染生产环境
   - 使用不同的数据库和服务实例

3. **安全考虑**
   - 不要在前端代码中暴露敏感信息
   - API密钥应在后端管理
   - 使用HTTPS/WSS协议部署生产环境