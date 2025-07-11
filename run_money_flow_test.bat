@echo off
echo ====================================
echo Running Money Flow Agent Comprehensive Test
echo ====================================
echo.
echo Please run this in Windows Anaconda Prompt:
echo.
echo conda activate stock-frontend
echo python test_money_flow_agent_comprehensive_final.py
echo.
echo This test will verify:
echo 1. DataFrame.empty fixes
echo 2. Sector caching with content_type (586 sectors)
echo 3. 白酒板块 as 概念板块 (BK0896.DC)
echo 4. SQL route patterns
echo 5. Non-standard term handling
echo 6. Validation fixes
echo.
pause