@echo off
echo ================================================================================
echo Money Flow Agent 综合测试 - Windows环境
echo 测试时间: %date% %time%
echo ================================================================================

REM 激活conda环境
echo 激活conda环境...
call conda activate stock-frontend

REM 确保在正确的目录
cd /d E:\PycharmProjects\stock_analysis_system

REM 运行测试
echo.
echo 开始运行Money Flow Agent综合测试...
echo 预计运行时间: 5-10分钟
echo.

python test_money_flow_agent_comprehensive_final.py

REM 检查是否有测试报告生成
if exist test_money_flow_agent_final_report.json (
    echo.
    echo ================================================================================
    echo 测试完成！报告已保存到: test_money_flow_agent_final_report.json
    echo ================================================================================
    echo.
    echo 显示测试摘要:
    type test_money_flow_agent_final_report.json | findstr /C:"pass_rate" /C:"total_tests" /C:"passed_tests" /C:"failed_tests"
) else (
    echo.
    echo ================================================================================
    echo 警告: 未找到测试报告文件！
    echo ================================================================================
)

echo.
echo 按任意键退出...
pause > nul