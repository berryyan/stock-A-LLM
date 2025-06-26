// API Response Types
export interface QueryResponse {
  success: boolean;
  answer: string;
  query_type: 'sql' | 'rag' | 'financial_analysis' | 'money_flow' | 'hybrid';
  sources?: {
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