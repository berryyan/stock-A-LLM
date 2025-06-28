import { useState, useRef, useCallback } from 'react';

interface UseStreamingResponseOptions {
  onComplete?: () => void;
  charsPerInterval?: number;
  intervalMs?: number;
}

export function useStreamingResponse(options: UseStreamingResponseOptions = {}) {
  const {
    onComplete,
    charsPerInterval = 3,
    intervalMs = 30,
  } = options;

  const [isStreaming, setIsStreaming] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const currentTextRef = useRef<string>('');

  const startStreaming = useCallback((
    fullText: string,
    onUpdate: (text: string) => void
  ) => {
    // 清理之前的流式显示
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    let currentIndex = 0;
    currentTextRef.current = '';
    setIsStreaming(true);

    intervalRef.current = setInterval(() => {
      if (currentIndex < fullText.length) {
        const endIndex = Math.min(currentIndex + charsPerInterval, fullText.length);
        currentTextRef.current = fullText.substring(0, endIndex);
        onUpdate(currentTextRef.current);
        currentIndex = endIndex;
      } else {
        // 流式显示完成
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setIsStreaming(false);
        onComplete?.();
      }
    }, intervalMs);
  }, [charsPerInterval, intervalMs, onComplete]);

  const stopStreaming = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    startStreaming,
    stopStreaming,
  };
}