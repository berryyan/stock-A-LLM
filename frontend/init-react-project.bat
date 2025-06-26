@echo off
REM React项目初始化脚本 - Windows环境
REM 在stock-frontend Anaconda环境中运行

echo ===================================================
echo   Stock Analysis System - React Project Setup
echo   初始化Claude.ai风格的React前端项目
echo ===================================================
echo.

REM 检查Node.js版本
echo 检查Node.js环境...
node --version
npm --version
echo.

REM 清理现有文件（保留模板）
echo 清理现有目录...
if exist src rmdir /s /q src
if exist public rmdir /s /q public
if exist docs rmdir /s /q docs

REM 使用Vite创建React+TypeScript项目
echo 创建React + TypeScript + Vite项目...
echo.
echo 注意：如果提示覆盖文件，请选择 Yes
echo.

call npm create vite@latest . -- --template react-ts

REM 安装基础依赖
echo.
echo 安装项目依赖...
call npm install

REM 安装额外依赖
echo.
echo 安装Claude.ai风格所需的额外依赖...
call npm install react-markdown remark-gfm rehype-katex remark-math katex
call npm install react-syntax-highlighter @types/react-syntax-highlighter
call npm install axios react-router-dom
call npm install clsx

REM 安装开发依赖
echo.
echo 安装开发工具...
call npm install -D tailwindcss postcss autoprefixer
call npm install -D @tailwindcss/typography
call npm install -D prettier eslint-config-prettier

REM 初始化Tailwind CSS
echo.
echo 初始化Tailwind CSS...
call npx tailwindcss init -p

echo.
echo ===================================================
echo   项目初始化完成！
echo   
echo   下一步：
echo   1. 在PyCharm中打开项目
echo   2. 运行 npm run dev 启动开发服务器
echo   3. 开始开发Claude.ai风格的界面
echo ===================================================
pause