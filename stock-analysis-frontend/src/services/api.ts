import axios from 'axios';
import { ApiResponse, QueryType } from '../types';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API服务类
export class ApiService {
  // 发送查询请求
  static async query(question: string, queryType: QueryType = 'hybrid'): Promise<ApiResponse> {
    try {
      const response = await apiClient.post<ApiResponse>('/api/query', {
        question,
        query_type: queryType,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.error || error.message || '网络错误',
        };
      }
      return {
        success: false,
        error: '未知错误',
      };
    }
  }

  // 健康检查
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await apiClient.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

// WebSocket服务类
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private messageHandlers: ((data: any) => void)[] = [];

  // 连接WebSocket
  connect(onMessage: (data: any) => void) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;

    try {
      this.ws = new WebSocket(wsUrl);
      this.messageHandlers.push(onMessage);

      this.ws.onopen = () => {
        console.log('WebSocket连接已建立');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.messageHandlers.forEach(handler => handler(data));
        } catch (e) {
          console.error('WebSocket消息解析失败:', e);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket连接已关闭');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
      };
    } catch (error) {
      console.error('WebSocket初始化失败:', error);
    }
  }

  // 发送消息
  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接');
    }
  }

  // 断开连接
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers = [];
  }

  // 尝试重连
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => {
        this.messageHandlers.forEach(handler => {
          this.connect(handler);
        });
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }
}