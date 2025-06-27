// API响应类型定义
export interface ApiResponse {
  success: boolean;
  answer?: string;
  content?: string;
  sources?: any;
  error?: string;
  query_type?: string;
}

// 消息类型定义
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
  isStreaming?: boolean;
}

// 查询类型
export type QueryType = 'sql' | 'rag' | 'financial' | 'hybrid';

// WebSocket消息类型
export interface WSMessage {
  type: 'query' | 'welcome' | 'processing' | 'analysis_result' | 'error';
  question?: string;
  id?: number;
  content?: any;
  message?: string;
  error?: string;
}