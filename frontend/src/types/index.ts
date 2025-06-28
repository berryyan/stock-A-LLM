// API Response Types
export interface QueryResponse {
  success: boolean;
  answer: string;
  query_type: 'sql' | 'rag' | 'financial_analysis' | 'money_flow' | 'hybrid';
  sources?: {
    // 新的API响应格式
    sql?: {
      result: any;
      sql?: string;
      error?: string;
    };
    rag?: {
      documents?: Document[];
      answer?: string;
      error?: string;
    };
    financial?: {
      analysis_report?: string;
      financial_data?: any;
      error?: string;
    };
    money_flow?: {
      analysis?: string;
      data?: any;
      error?: string;
    };
    // 兼容旧格式
    sql_data?: any[];
    documents?: Document[];
    table_data?: any[];
    chart_data?: any;
  };
  error?: string;
}

export interface Document {
  id: string;
  content: string;
  metadata: {
    source: string;
    page?: number;
    title?: string;
    date?: string;
  };
}

// Chat Types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: QueryResponse['sources'];
  isStreaming?: boolean;
  isError?: boolean;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// UI Types
export interface DocumentViewerProps {
  content: string | Document | any;
  type: 'markdown' | 'table' | 'chart' | 'document';
  onClose: () => void;
}