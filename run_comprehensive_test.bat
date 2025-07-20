@echo off
REM Concept Agent综合测试脚本 - Windows批处理文件
REM 确保在正确的Python环境中运行

echo ================================================================================
echo Concept Agent 综合测试 - Windows版本
echo ================================================================================
echo.

REM 检查是否在正确的conda环境
echo 检查Python环境...
python --version
echo.

REM 检查必要的包
echo 检查依赖包...
python -c "import langchain; print(f'LangChain版本: {langchain.__version__}')"
python -c "import fastapi; print(f'FastAPI版本: {fastapi.__version__}')"
python -c "import pymysql; print(f'PyMySQL版本: {pymysql.__version__}')"
echo.

REM 设置环境变量（如果需要）
REM set PYTHONPATH=%cd%

REM 运行综合测试
echo 开始运行综合测试...
echo 注意：此测试可能需要5-10分钟，请耐心等待
echo.

python test_concept_agent_comprehensive_windows.py

echo.
echo ================================================================================
echo 测试完成！
echo 请查看生成的日志文件和测试报告
echo ================================================================================

pause