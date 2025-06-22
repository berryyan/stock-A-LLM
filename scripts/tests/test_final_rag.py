#!/usr/bin/env python3
"""
最终测试RAG Agent功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
import time

def test_final_rag():
    """最终测试"""
    
    print("=== RAG Agent 最终测试 ===\n")
    
    try:
        # 1. 初始化
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功")
        
        # 2. 基本功能测试
        print("\n2. 测试基本查询功能...")
        
        test_cases = [
            {
                "question": "贵州茅台的主要产品是什么",
                "filters": {"ts_code": "600519.SH"},
                "expected": "查询茅台产品信息"
            },
            {
                "question": "分析贵州茅台2024年的财务状况",
                "filters": {"ts_code": "600519.SH"},
                "expected": "财务分析"
            }
        ]
        
        success_count = 0
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n测试 {i}: {test['question']}")
            
            start_time = time.time()
            result = rag_agent.query(test['question'], filters=test['filters'])
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                success_count += 1
                print(f"✓ 成功")
                print(f"  - 耗时: {elapsed_time:.2f}秒")
                print(f"  - 文档数: {result.get('document_count', 0)}")
                print(f"  - 答案长度: {len(result.get('answer', ''))}")
                answer_preview = result.get('answer', '')[:100]
                print(f"  - 答案预览: {answer_preview}...")
            else:
                print(f"✗ 失败: {result.get('error', '未知错误')}")
        
        # 3. 统计信息
        print(f"\n3. 测试结果统计:")
        print(f"  - 总测试数: {len(test_cases)}")
        print(f"  - 成功数: {success_count}")
        print(f"  - 成功率: {success_count/len(test_cases)*100:.0f}%")
        
        # 4. 检查统计功能
        if hasattr(rag_agent, 'query_count'):
            print(f"\n4. 查询统计:")
            print(f"  - 总查询数: {rag_agent.query_count}")
            print(f"  - 成功查询: {rag_agent.success_count}")
            
            if hasattr(rag_agent, 'get_stats'):
                stats = rag_agent.get_stats()
                print(f"  - 成功率: {stats.get('success_rate', 0)*100:.0f}%")
                print(f"  - 平均响应时间: {stats.get('avg_response_time', 0):.2f}秒")
        
        # 5. 总结
        print(f"\n{'='*50}")
        if success_count == len(test_cases):
            print("✓ 所有测试通过！RAG Agent功能正常。")
        elif success_count > 0:
            print("⚠️ 部分测试通过，需要进一步调试。")
        else:
            print("✗ 所有测试失败，请检查系统配置。")
            
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_rag()
