# Windows Anaconda Frontend Environment Setup Guide

## 前置要求
- 已安装Anaconda (路径: E:\anaconda3\)
- 已安装Git Bash或PowerShell
- 管理员权限

## 环境策略说明

### 为什么推荐复制现有环境？

1. **保持开发一致性**：前端开发时可能需要运行Python脚本（如API测试、数据处理）
2. **避免重复安装**：继承所有已配置好的Python包和设置
3. **简化调试流程**：在同一环境中可以同时调试前后端代码
4. **配置继承**：保留原有的pip源、conda源等配置

### 什么时候选择全新环境？

- 当前环境特别大（>5GB）
- 存在已知的包冲突
- 只做纯前端开发，不涉及Python

## 设置步骤

### 1. 创建Node.js环境

打开Anaconda Prompt (以管理员身份运行):

#### 选项A：复制现有环境（推荐）
```powershell
# 假设你的现有环境名为 'stock-analysis' 或 'base'
# 首先列出所有环境确认名称
conda env list

# 复制现有环境
conda create -n stock-frontend --clone stock-analysis
# 或者如果使用base环境
conda create -n stock-frontend --clone base

# 激活新环境
conda activate stock-frontend

# 安装Node.js
conda install -c conda-forge nodejs=18

# 安装前端开发特定工具
conda install -c conda-forge yarn  # 可选，yarn包管理器
```

#### 选项B：创建全新环境（轻量级）
```powershell
# 如果你确定不需要Python依赖，可以创建干净环境
conda create -n stock-frontend-minimal python=3.10
conda activate stock-frontend-minimal
conda install -c conda-forge nodejs=18
```

### 2. 验证安装

```powershell
node --version  # 应显示 v18.x.x
npm --version   # 应显示 9.x.x
```

### 3. 配置npm镜像（中国用户）

```powershell
npm config set registry https://registry.npmmirror.com/
```

### 4. 安装VS Code扩展

推荐安装以下VS Code扩展：
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint
- TypeScript Vue Plugin (Volar)
- Tailwind CSS IntelliSense

### 5. 环境变量配置

将以下内容添加到系统环境变量：

```
NODE_OPTIONS=--max-old-space-size=4096
```

### 6. 创建工作区配置

在项目根目录创建 `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ]
}
```

### 7. 同步检查脚本

创建 `check_env_sync.bat`:

```batch
@echo off
echo === Environment Sync Check ===
echo.
echo Windows Anaconda Environment:
call conda activate stock-frontend
node --version
npm --version
echo.
echo Please ensure WSL2 has the same Node.js version
pause
```

## 注意事项

1. **版本一致性**: 确保Windows和WSL2使用相同的Node.js版本(18.x)
2. **路径问题**: Windows路径使用反斜杠，WSL2使用正斜杠
3. **换行符**: 配置Git使用LF换行符
   ```
   git config --global core.autocrlf false
   ```
4. **端口占用**: React开发服务器默认使用3000端口，API服务器使用8000端口

## 开发工作流

1. **代码编辑**: 在Windows中使用VS Code编辑代码
2. **前端开发**: 在Windows Anaconda环境中运行React开发服务器
3. **API服务**: 在WSL2中运行FastAPI服务器
4. **版本控制**: 两边都可以使用Git

## 故障排除

### npm install失败
```powershell
# 清除缓存
npm cache clean --force
# 删除node_modules
rmdir /s /q node_modules
# 重新安装
npm install
```

### 端口被占用
```powershell
# 查找占用端口的进程
netstat -ano | findstr :3000
# 终止进程
taskkill /PID <进程ID> /F
```