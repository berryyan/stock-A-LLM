@echo off
REM Clear Python cache on Windows

echo Clearing Python cache...
echo =======================

REM 1. Clear all __pycache__ directories
echo 1. Clearing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM 2. Clear all .pyc files
echo 2. Clearing .pyc files...
del /s /q *.pyc 2>nul

REM 3. Clear all .pyo files
echo 3. Clearing .pyo files...
del /s /q *.pyo 2>nul

REM 4. Clear pytest cache
echo 4. Clearing .pytest_cache directories...
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"

echo.
echo Python cache cleared successfully!
echo.
echo You can now run the comprehensive test:
echo python test_sql_agent_comprehensive.py
echo.
pause