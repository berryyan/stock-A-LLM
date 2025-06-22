#!/usr/bin/env python3
"""
测试优化后的RAG Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
import json

def test_optimized_rag():
    """测试优化后的RAG功能"""
    
    print("=== 测试优化后的RAG Agent ===\n")
    
    try:
        # 初始化
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功\n")
        
        # 测试查询
        test_cases = [
            {
                "question": "贵州茅台最新财报的主要内容",
                "filters": {"ts_code": "600519.SH"}
            },
            {
                "question": "分析茅台的财务状况",
                "filters": {"ts_code": "600519.SH"}
            },
            {
                "question": "最近有哪些重要公告",
                "filters": None
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. 测试查询: {test['question']}")
            print(f"   过滤条件: {test.get('filters', '无')}")
            
            result = rag_agent.query(
                question=test['question'],
                filters=test.get('filters')
            )
            
            print(f"\n   结果:")
            print(f"   - 成功: {result.get('success')}")
            print(f"   - 文档数: {result.get('document_count', 0)}")
            print(f"   - 答案长度: {len(result.get('answer', ''))}")
            print(f"   - 处理时间: {result.get('processing_time', 'N/A'):.2f}秒" if 'processing_time' in result else "   - 处理时间: N/A")
            
            if result.get('success'):
                answer_preview = result.get('answer', '')[:200]
                print(f"   - 答案预览: {answer_preview}...")
            else:
                print(f"   - 错误: {result.get('error', '未知错误')}")
            
            print("-" * 60)
        
        # 测试答案提取的各种情况
        print("\n2. 测试答案提取逻辑...")
        
        # 直接测试qa_chain
        if hasattr(rag_agent, 'qa_chain'):
            test_inputs = {
                "context": "测试文档内容",
                "question": "测试问题",
                "chat_history": "无历史对话"
            }
            
            try:
                result = rag_agent.qa_chain.invoke(test_inputs)
                print(f"   QA Chain返回类型: {type(result)}")
                
                # 测试答案提取
                if hasattr(result, 'content'):
                    print(f"   ✓ 检测到content属性: {result.content[:50]}...")
                elif isinstance(result, dict):
                    print(f"   ✓ 返回字典，包含键: {list(result.keys())}")
                elif isinstance(result, str):
                    print(f"   ✓ 返回字符串: {result[:50]}...")
                else:
                    print(f"   ⚠️ 未知返回类型: {type(result)}")
                    
            except Exception as e:
                print(f"   ✗ 测试失败: {e}")
        
        print("\n✓ 所有测试完成！")
        
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimized_rag()
