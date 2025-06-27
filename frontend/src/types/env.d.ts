/// <reference types="vite/client" />

interface ImportMetaEnv {
  // 核心配置
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_ENV: 'development' | 'production' | 'staging'
  readonly VITE_DEBUG: string
  readonly VITE_API_TIMEOUT: string
  
  // 开发工具配置
  readonly VITE_ENABLE_DEV_TOOLS: string
  readonly VITE_ENABLE_SOURCE_MAP: string
  
  // 可选配置
  readonly VITE_ANALYTICS_ID?: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_ENABLE_TEST_FEATURES?: string
  readonly VITE_MOCK_MODE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}