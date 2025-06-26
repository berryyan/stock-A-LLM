import axios from 'axios';
import { QueryResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时，适应复杂查询
  headers: {
    'Content-Type': 'application/json',
  },
});

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