@echo off
echo ================================================================================
echo v2.3.0 回归测试 - Windows环境
echo ================================================================================
echo.
echo 请在Windows Anaconda Prompt中运行此脚本
echo 确保已激活正确的conda环境: conda activate stock-frontend
echo.
echo 将按以下顺序运行测试：
echo 1. SQL Agent 综合测试
echo 2. Money Flow Agent 综合测试  
echo 3. Financial Agent 综合测试
echo 4. RAG Agent 综合测试
echo 5. Hybrid Agent 快速验证
echo.
pause

echo.
echo [1/5] 开始SQL Agent综合测试（64个测试用例）...
echo ================================================================================
python test_sql_agent_comprehensive.py > test_results\sql_agent_regression_20250712.txt 2>&1
echo SQL Agent测试完成，结果保存到: test_results\sql_agent_regression_20250712.txt

echo.
echo [2/5] 开始Money Flow Agent综合测试（64个测试用例）...
echo ================================================================================
python test_money_flow_agent_comprehensive_final.py > test_results\money_flow_regression_20250712.txt 2>&1
echo Money Flow Agent测试完成，结果保存到: test_results\money_flow_regression_20250712.txt

echo.
echo [3/5] 开始Financial Agent综合测试（63个测试用例）...
echo ================================================================================
python test_financial_agent_comprehensive_windows.py > test_results\financial_regression_20250712.txt 2>&1
echo Financial Agent测试完成，结果保存到: test_results\financial_regression_20250712.txt

echo.
echo [4/5] 开始RAG Agent综合测试（72个测试用例）...
echo ================================================================================
python test_rag_agent_comprehensive.py > test_results\rag_agent_regression_20250712.txt 2>&1
echo RAG Agent测试完成，结果保存到: test_results\rag_agent_regression_20250712.txt

echo.
echo [5/5] 开始Hybrid Agent综合测试（13个测试用例）...
echo ================================================================================
python test_hybrid_agent_comprehensive.py > test_results\hybrid_agent_regression_20250712.txt 2>&1
echo Hybrid Agent测试完成，结果保存到: test_results\hybrid_agent_regression_20250712.txt

echo.
echo ================================================================================
echo 所有测试完成！
echo.
echo 测试结果保存在 test_results 目录下：
echo - sql_agent_regression_20250712.txt
echo - money_flow_regression_20250712.txt
echo - financial_regression_20250712.txt
echo - rag_agent_regression_20250712.txt
echo - hybrid_agent_regression_20250712.txt
echo.
echo 请将这些结果文件发送给Claude进行分析
echo ================================================================================
pause