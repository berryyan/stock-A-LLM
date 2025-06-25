#!/usr/bin/env python3
"""
测试错误消息传播链
验证从financial_agent到前端的错误消息是否正确传递
"""

import json
from agents.hybrid_agent import HybridAgent

def test_invalid_stock_code():
    """测试无效股票代码的错误传播"""
    print("=== 测试错误消息传播 ===\n")
    
    # 初始化混合代理
    agent = HybridAgent()
    
    # 测试案例
    test_cases = [
        "分析02359的财务健康度",  # 5位数字
        "分析000000.SX的财务健康度",  # 错误的后缀
        "分析1234567的财务健康度",  # 7位数字
        "分析abcdef的财务健康度",  # 非数字
    ]
    
    for test_query in test_cases:
        print(f"测试查询: {test_query}")
        result = agent.query(test_query)
        
        print(f"返回结果: ")
        print(f"  - success: {result.get('success')}")
        print(f"  - error: {result.get('error')}")
        print(f"  - query_type: {result.get('query_type')}")
        
        # 模拟WebSocket消息格式
        ws_message = {
            "type": "analysis_result",
            "query_id": "test-123",
            "content": result,
            "timestamp": "2025-06-25T10:00:00"
        }
        
        print(f"模拟WebSocket消息: ")
        print(json.dumps(ws_message, ensure_ascii=False, indent=2))
        print("-" * 50 + "\n")

if __name__ == "__main__":
    test_invalid_stock_code()