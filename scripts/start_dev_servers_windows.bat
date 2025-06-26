@echo off
REM 股票分析系统开发服务器启动脚本 (Windows)
REM 在Windows Anaconda环境中同时运行前后端服务器

echo ===================================================
echo   Stock Analysis System Development Servers
echo   在Windows原生环境运行以获得最佳性能
echo ===================================================
echo.

REM 检查是否在正确的conda环境
echo 当前Conda环境: %CONDA_DEFAULT_ENV%
echo.

if "%CONDA_DEFAULT_ENV%"=="" (
    echo 错误：请先激活conda环境
    echo 运行: conda activate stock-frontend
    pause
    exit /b 1
)

REM 启动后端API服务器
echo [1/2] 启动后端API服务器 (端口: 8000)...
start "Stock Analysis API" cmd /k "python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

REM 等待API启动
echo 等待API服务器启动...
timeout /t 5 /nobreak > nul

REM 检查frontend目录是否存在
if not exist "frontend" (
    echo.
    echo 警告：frontend目录不存在
    echo 请先初始化React项目：
    echo   cd frontend
    echo   npm create vite@latest . -- --template react-ts
    echo   npm install
    pause
    exit /b 1
)

REM 启动前端开发服务器
echo.
echo [2/2] 启动前端开发服务器 (端口: 3000)...
cd frontend
start "React Dev Server" cmd /k "npm run dev"

echo.
echo ===================================================
echo   服务器启动完成！
echo   
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo   前端界面: http://localhost:3000
echo   
echo   按Ctrl+C停止服务器
echo ===================================================
echo.

REM 显示运行状态
echo 查看运行状态...
netstat -an | findstr "8000 3000"

pause