@echo off
REM React Project Init Script - Windows Environment
REM Run in stock-frontend Anaconda environment

echo ===================================================
echo   Stock Analysis System - React Project Setup
echo   Initialize Claude.ai Style React Frontend
echo ===================================================
echo.

REM Check Node.js version
echo Checking Node.js environment...
node --version
npm --version
echo.

REM Clean existing files (keep templates)
echo Cleaning existing directories...
if exist src rmdir /s /q src
if exist public rmdir /s /q public
if exist docs rmdir /s /q docs

REM Create React+TypeScript project with Vite
echo Creating React + TypeScript + Vite project...
echo.
echo Note: If prompted to overwrite files, please select Yes
echo.

call npm create vite@latest . -- --template react-ts

REM Install base dependencies
echo.
echo Installing project dependencies...
call npm install

REM Install additional dependencies
echo.
echo Installing Claude.ai style required dependencies...
call npm install react-markdown remark-gfm rehype-katex remark-math katex
call npm install react-syntax-highlighter @types/react-syntax-highlighter
call npm install axios react-router-dom
call npm install clsx

REM Install dev dependencies
echo.
echo Installing development tools...
call npm install -D tailwindcss postcss autoprefixer
call npm install -D @tailwindcss/typography
call npm install -D prettier eslint-config-prettier

REM Initialize Tailwind CSS
echo.
echo Initializing Tailwind CSS...
call npx tailwindcss init -p

echo.
echo ===================================================
echo   Project initialization complete!
echo   
echo   Next steps:
echo   1. Open project in PyCharm
echo   2. Run npm run dev to start dev server
echo   3. Start developing Claude.ai style interface
echo ===================================================
pause