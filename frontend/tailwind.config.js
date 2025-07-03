/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // 使用class模式而不是media查询
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Claude.ai brand colors - Dark Theme
        'claude-primary': '#10a37f',
        'claude-primary-hover': '#0d8968',
        'claude-background': '#262626',      // 左分屏背景色（深灰）
        'claude-surface': '#262626',         // 侧边栏背景色（深灰）
        'claude-border': '#404040',          // 边框色（更深的灰）
        'claude-text-primary': '#FFFFFF',    // 主文字色（白色）
        'claude-text-secondary': '#B0B0B0',  // 次要文字色（浅灰）
        // Dark mode colors
        'claude-dark-background': '#2d2d30',
        'claude-dark-surface': '#1e1e1e',
        'claude-dark-border': '#3e3e42',
      },
      width: {
        'sidebar': '260px',
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'typing': 'typing 1.4s ease-out infinite',
      },
      keyframes: {
        slideIn: {
          'from': { transform: 'translateX(100%)' },
          'to': { transform: 'translateX(0)' },
        },
        typing: {
          '0%': { opacity: 0 },
          '50%': { opacity: 1 },
          '100%': { opacity: 0 },
        },
      },
    },
  },
  plugins: [],
}