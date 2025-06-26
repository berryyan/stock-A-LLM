import axios from 'axios';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API types
export interface QueryRequest {
  question: string;
  query_type?: 'sql' | 'rag' | 'financial_analysis' | 'money_flow' | 'hybrid';
  top_k?: number;
}

export interface QueryResponse {
  success: boolean;
  answer: string;
  query_type: string;
  sources?: {
    sql_data?: any[];
    documents?: any[];
    table_data?: any[];
    chart_data?: any;
  };
  error?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: QueryResponse['sources'];
}

// API methods
export const stockAPI = {
  // Query endpoint
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  },

  // Health check
  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get available query types
  getQueryTypes: async () => {
    const response = await api.get('/query-types');
    return response.data;
  },
};

// WebSocket connection for real-time communication
export class StockWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000;

  constructor(
    private onMessage: (data: any) => void,
    private onConnect?: () => void,
    private onDisconnect?: () => void,
    private onError?: (error: Event) => void
  ) {}

  connect() {
    const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
    this.ws = new WebSocket(`${wsUrl}/ws`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.onConnect?.();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.onDisconnect?.();
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onError?.(error);
    };
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => {
        this.connect();
      }, this.reconnectTimeout * this.reconnectAttempts);
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default stockAPI;