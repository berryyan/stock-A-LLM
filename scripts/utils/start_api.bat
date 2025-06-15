@echo off
echo 股票分析系统 API 启动脚本
echo ============================
echo.

REM 激活虚拟环境
call stock_analysis_env\Scripts\activate

REM 检查环境变量
python -c "from config.settings import settings; print(f'DeepSeek API: {bool(settings.DEEPSEEK_API_KEY)}')"

echo.
echo 正在启动API服务器...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

REM 启动API服务
python -m api.main