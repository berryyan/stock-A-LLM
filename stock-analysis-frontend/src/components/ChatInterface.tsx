import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Message, QueryType } from '../types';
import { ApiService, WebSocketService } from '../services/api';
import MessageList from './MessageList';
import InputBox from './InputBox';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);
  const [currentStreamingId, setCurrentStreamingId] = useState<string | null>(null);
  const wsServiceRef = useRef<WebSocketService | null>(null);
  const streamingContentRef = useRef<string>('');

  // 初始化WebSocket连接
  useEffect(() => {
    // 创建WebSocket服务实例
    const wsService = new WebSocketService('ws://localhost:8000/ws');
    wsServiceRef.current = wsService;

    // 设置消息处理器
    wsService.onMessage((data) => {
      if (data.type === 'stream') {
        handleStreamMessage(data);
      } else if (data.type === 'complete') {
        handleCompleteMessage(data);
      } else if (data.type === 'error') {
        handleErrorMessage(data);
      }
    });

    // 连接WebSocket
    wsService.connect();

    // 清理函数
    return () => {
      wsService.disconnect();
    };
  }, []);

  // 处理流式消息
  const handleStreamMessage = useCallback((data: any) => {
    if (data.message_id && currentStreamingId === data.message_id) {
      streamingContentRef.current += data.content || '';
      
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0 && newMessages[lastIndex].id === data.message_id) {
          newMessages[lastIndex] = {
            ...newMessages[lastIndex],
            content: streamingContentRef.current,
            isStreaming: true,
          };
        }
        return newMessages;
      });
    }
  }, [currentStreamingId]);

  // 处理完成消息
  const handleCompleteMessage = useCallback((data: any) => {
    if (data.message_id && currentStreamingId === data.message_id) {
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0 && newMessages[lastIndex].id === data.message_id) {
          newMessages[lastIndex] = {
            ...newMessages[lastIndex],
            isStreaming: false,
          };
        }
        return newMessages;
      });
      
      setCurrentStreamingId(null);
      streamingContentRef.current = '';
      setIsLoading(false);
    }
  }, [currentStreamingId]);

  // 处理错误消息
  const handleErrorMessage = useCallback((data: any) => {
    if (data.message_id && currentStreamingId === data.message_id) {
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0 && newMessages[lastIndex].id === data.message_id) {
          newMessages[lastIndex] = {
            ...newMessages[lastIndex],
            content: `❌ ${data.error || '查询失败，请稍后重试。'}`,
            isError: true,
            isStreaming: false,
          };
        }
        return newMessages;
      });
      
      setCurrentStreamingId(null);
      streamingContentRef.current = '';
      setIsLoading(false);
    }
  }, [currentStreamingId]);

  // 初始化欢迎消息
  useEffect(() => {
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      type: 'assistant',
      content: `您好！我是股票分析智能助手，可以为您提供：

📊 **财务分析**：财务健康度评分、杜邦分析、现金流质量分析
📈 **技术分析**：趋势分析、技术指标、交易信号
💰 **资金流向**：主力资金监控、超大单分析、四级资金分布

请输入您想了解的股票或分析需求，例如：
- "分析贵州茅台的财务健康度"
- "茅台最近的主力资金流向"
- "平安银行的技术走势如何"`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);

    // 健康检查
    checkApiHealth();
  }, []);

  // API健康检查
  const checkApiHealth = async () => {
    const healthy = await ApiService.healthCheck();
    setIsHealthy(healthy);
    if (!healthy) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: '⚠️ API服务连接失败，请确保后端服务正在运行。',
        timestamp: new Date(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // 智能判断查询类型
  const detectQueryType = (question: string): QueryType => {
    // 财务分析关键词
    if (question.includes('财务') || question.includes('健康度') || 
        question.includes('杜邦') || question.includes('现金流质量') ||
        question.includes('多期对比')) {
      return 'financial';
    }
    
    // RAG查询关键词
    if (question.includes('公告') || question.includes('年报') || 
        question.includes('季报') || question.includes('战略') ||
        question.includes('优势') || question.includes('分析')) {
      return 'rag';
    }
    
    // SQL查询关键词
    if (question.includes('股价') || question.includes('涨幅') || 
        question.includes('市值') || question.includes('成交量') ||
        question.includes('排名') || question.includes('资金流向')) {
      return 'sql';
    }
    
    // 默认使用混合查询
    return 'hybrid';
  };

  // 发送消息
  const handleSend = async (content: string) => {
    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // 设置加载状态
    setIsLoading(true);

    // 检查WebSocket连接状态
    if (!wsServiceRef.current || !wsServiceRef.current.isConnected()) {
      // 如果WebSocket未连接，使用传统HTTP方式
      try {
        const queryType = detectQueryType(content);
        const response = await ApiService.query(content, queryType);
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.success 
            ? (response.answer || response.content || '抱歉，未获取到有效回复。')
            : `❌ ${response.error || '查询失败，请稍后重试。'}`,
          timestamp: new Date(),
          isError: !response.success,
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      } catch (error) {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: '❌ 网络错误，请检查网络连接并重试。',
          timestamp: new Date(),
          isError: true,
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    } else {
      // 使用WebSocket流式响应
      const messageId = (Date.now() + 1).toString();
      setCurrentStreamingId(messageId);
      streamingContentRef.current = '';
      
      // 添加空的助手消息占位符
      const assistantMessage: Message = {
        id: messageId,
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // 自动检测查询类型
      const queryType = detectQueryType(content);
      
      // 发送WebSocket消息
      wsServiceRef.current.send({
        type: 'query',
        message_id: messageId,
        question: content,
        query_type: queryType,
      });
    }
  };

  // 快捷查询
  const quickQueries = [
    { label: '茅台财务分析', query: '分析贵州茅台的财务健康度' },
    { label: '茅台资金流向', query: '600519.SH最近的资金流向' },
    { label: '平安技术分析', query: '平安银行的技术走势分析' },
    { label: '市值排行榜', query: 'A股市值排名前10' },
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>🤖 股票分析智能助手</h1>
        <p>基于AI的专业股票分析 | 财务分析 • 技术分析 • 资金流向</p>
        {!isHealthy && (
          <div className="health-warning">
            ⚠️ API服务未连接
          </div>
        )}
      </div>

      <MessageList messages={messages} isLoading={isLoading} />

      <div className="input-section">
        <div className="quick-actions">
          {quickQueries.map((item, index) => (
            <button
              key={index}
              className="quick-action"
              onClick={() => handleSend(item.query)}
              disabled={isLoading}
            >
              {item.label}
            </button>
          ))}
        </div>
        
        <InputBox
          onSend={handleSend}
          disabled={isLoading || !isHealthy}
          placeholder={isLoading ? "正在处理查询中，请稍候..." : "请输入您的问题..."}
        />
      </div>
    </div>
  );
};

export default ChatInterface;