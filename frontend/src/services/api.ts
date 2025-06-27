import axios from 'axios';
import type { QueryResponse } from '../types';

// 从环境变量读取配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 120000;
const IS_DEV = import.meta.env.VITE_ENV === 'development';
const DEBUG = import.meta.env.VITE_DEBUG === 'true';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 开发环境请求/响应日志
if (DEBUG) {
  api.interceptors.request.use(
    (config) => {
      console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
      return config;
    },
    (error) => {
      console.error('API Request Error:', error);
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => {
      console.log('API Response:', response.status, response.data);
      return response;
    },
    (error) => {
      console.error('API Response Error:', error.response?.status, error.response?.data);
      return Promise.reject(error);
    }
  );
}

// API methods
export const stockAPI = {
  query: async (question: string, queryType?: string): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/query', {
      question,
      query_type: queryType || 'hybrid',
      top_k: 5,
    });
    return response.data;
  },

  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default stockAPI;