@echo off
echo ========================================
echo 启动模块化版本的股票分析系统API
echo ========================================
echo.

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate

REM 检查虚拟环境是否激活成功
if errorlevel 1 (
    echo 错误：无法激活虚拟环境
    pause
    exit /b 1
)

echo.
echo 启动API服务器（模块化版本）...
echo 访问地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.

REM 启动API服务
python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001

pause