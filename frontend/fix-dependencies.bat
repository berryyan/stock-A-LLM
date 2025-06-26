@echo off
echo Fixing Node.js 18 compatibility issues...

echo Removing node_modules and package-lock.json...
rmdir /s /q node_modules
del package-lock.json

echo Installing compatible Vite version...
call npm install vite@^5.2.0 --save-dev

echo Installing base dependencies...
call npm install

echo Installing Claude.ai style dependencies...
call npm install react-markdown remark-gfm rehype-katex remark-math katex
call npm install react-syntax-highlighter @types/react-syntax-highlighter
call npm install axios react-router-dom clsx

echo Installing Tailwind CSS...
call npm install -D tailwindcss postcss autoprefixer @tailwindcss/typography

echo Initializing Tailwind...
call npx tailwindcss init -p

echo.
echo Dependencies fixed! Try running: npm run dev
pause