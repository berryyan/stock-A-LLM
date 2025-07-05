@echo off
echo ========================================
echo 重启API服务并测试
echo ========================================
echo.

echo 请先停止正在运行的API服务（Ctrl+C）
echo 然后按任意键继续...
pause

echo.
echo 激活虚拟环境并启动API服务...
call venv\Scripts\activate
start cmd /k "python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo 等待API服务启动（10秒）...
timeout /t 10

echo.
echo 运行测试...
python test_simple_query.py

pause