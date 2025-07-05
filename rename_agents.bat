@echo off
echo ========================================
echo 重命名Agent文件以避免混淆
echo ========================================
echo.

REM 备份原文件
echo 创建备份...
mkdir agents\backup_20250705 2>nul

REM 备份现有文件
copy agents\sql_agent_v2.py agents\backup_20250705\
copy agents\sql_agent_modular.py agents\backup_20250705\
copy agents\rag_agent_modular.py agents\backup_20250705\
copy agents\financial_agent_modular.py agents\backup_20250705\
copy agents\money_flow_agent_modular.py agents\backup_20250705\

echo.
echo 重命名文件...

REM 重命名为更清晰的名字
REM sql_agent_v2.py -> sql_agent_modular_impl.py (真正的模块化实现)
REM sql_agent_modular.py -> sql_agent_inherited.py (继承版本)

ren agents\sql_agent_v2.py sql_agent_modular_impl.py
ren agents\sql_agent_modular.py sql_agent_inherited.py

echo.
echo 重命名完成！
echo.
echo 新的命名：
echo - sql_agent_modular_impl.py: 真正使用模块化组件的实现
echo - sql_agent_inherited.py: 简单继承原版本的实现
echo.
pause