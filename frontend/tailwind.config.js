/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Claude.ai brand colors
        'claude-primary': '#10a37f',
        'claude-primary-hover': '#0d8968',
        'claude-background': '#f7f7f8',
        'claude-surface': '#ffffff',
        'claude-border': '#e5e5e7',
        'claude-text-primary': '#202123',
        'claude-text-secondary': '#6e6e80',
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