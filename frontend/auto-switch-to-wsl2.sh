#!/bin/bash
# 自动切换到WSL2环境并准备开发
echo "🚀 自动切换到WSL2开发环境"
echo "=========================="

# 1. 更新环境标识文件
echo "📝 更新环境标识..."
cat > .frontend-env << 'EOF'
# Frontend Development Environment Indicator
# This file indicates which environment is currently set up for frontend development  
# DO NOT COMMIT THIS FILE

# Current Environment: wsl2
CURRENT_ENV=wsl2

# Instructions:
# - When developing in WSL2, set CURRENT_ENV=wsl2
# - When developing in Windows, set CURRENT_ENV=windows
# - This helps track which node_modules is currently installed
EOF

# 2. 检查当前node_modules是否为Windows版本
echo "🔍 检查node_modules..."
if [ -d "node_modules" ]; then
    # 检查是否有Windows特有的文件
    if [ -f "node_modules/.bin/vite.cmd" ] || [ -f "node_modules/.bin/vite.ps1" ]; then
        echo "⚠️  检测到Windows版本的node_modules，正在清理..."
        rm -rf node_modules package-lock.json
    else
        echo "✅ node_modules是Linux版本，跳过清理"
    fi
else
    echo "📦 node_modules不存在，需要安装"
fi

# 3. 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装Linux版本依赖..."
    npm install
else
    echo "✅ 依赖已存在，跳过安装"
fi

# 4. 显示状态
echo ""
echo "✅ WSL2环境准备完成！"
echo "当前环境: WSL2"
echo ""
echo "可用命令:"
echo "  npm run dev    - 启动开发服务器"
echo "  npm run build  - 构建生产版本"
echo ""
echo "💡 提示: Claude可以直接在WSL2中进行开发调试"

# 5. 设置WSL2环境变量
if [ -f ".env.wsl2" ]; then
    echo "🔧 使用WSL2专用配置（API地址: 10.0.0.66:8000）"
    cp .env.wsl2 .env.local
fi