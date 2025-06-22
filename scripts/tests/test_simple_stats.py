#!/usr/bin/env python3
"""
测试简单的统计功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent

def test_simple_stats():
    """测试简单统计"""
    
    print("=== 测试RAG Agent简单统计功能 ===\n")
    
    try:
        # 初始化
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功")
        
        # 检查统计变量
        if hasattr(rag_agent, 'query_count'):
            print("✓ 统计功能已启用")
            print(f"  - 初始查询数: {rag_agent.query_count}")
        else:
            print("⚠️ 统计功能未找到")
            return
        
        # 执行一个查询
        print("\n2. 执行测试查询...")
        result = rag_agent.query("贵州茅台的主要产品", filters={"ts_code": "600519.SH"})
        
        if result.get('success'):
            print(f"✓ 查询成功")
            print(f"  - 处理时间: {result.get('processing_time', 0):.2f}秒")
            print(f"  - 文档数: {result.get('document_count', 0)}")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
        
        # 检查统计更新
        print("\n3. 检查统计信息...")
        if hasattr(rag_agent, 'get_stats'):
            stats = rag_agent.get_stats()
            print("✓ 统计信息:")
            for key, value in stats.items():
                print(f"  - {key}: {value}")
        else:
            print(f"  - 查询总数: {rag_agent.query_count}")
            print(f"  - 成功数: {rag_agent.success_count}")
            if rag_agent.query_count > 0:
                print(f"  - 平均时间: {rag_agent.total_time / rag_agent.query_count:.2f}秒")
        
        print("\n✓ 测试完成！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_stats()
