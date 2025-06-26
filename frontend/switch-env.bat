@echo off
echo Frontend Environment Switcher (Windows)
echo =====================================
echo.

:: Check if .frontend-env exists
if exist .frontend-env (
    echo Current environment file found.
    type .frontend-env | findstr "CURRENT_ENV"
) else (
    echo No environment file found.
)

echo.
echo Switching to Windows environment...

:: Create/Update environment file
(
echo # Frontend Development Environment Indicator
echo # This file indicates which environment is currently set up for frontend development  
echo # DO NOT COMMIT THIS FILE
echo.
echo # Current Environment: windows
echo CURRENT_ENV=windows
echo.
echo # Instructions:
echo # - When developing in WSL2, set CURRENT_ENV=wsl2
echo # - When developing in Windows, set CURRENT_ENV=windows
echo # - This helps track which node_modules is currently installed
) > .frontend-env

echo Environment switched to: Windows
echo.
echo Next steps:
echo 1. Delete node_modules folder if it exists (from WSL2)
echo 2. Run: npm install
echo 3. Run: npm run dev
echo.
pause