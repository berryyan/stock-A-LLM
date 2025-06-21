#!/usr/bin/env python3
"""
测试RAG Agent增强功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
import time

def test_enhancements():
    """测试增强功能"""
    
    print("=== 测试RAG Agent增强功能 ===\n")
    
    try:
        # 1. 初始化
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功")
        
        # 检查是否有统计功能
        if hasattr(rag_agent, 'stats'):
            print("✓ 统计功能已启用")
        else:
            print("⚠️ 统计功能未启用")
        
        # 2. 执行几个查询来生成统计数据
        print("\n2. 执行测试查询...")
        
        test_queries = [
            ("贵州茅台的主要产品", {"ts_code": "600519.SH"}),
            ("分析茅台的盈利能力", {"ts_code": "600519.SH"}),
            ("最近的重要公告", None)
        ]
        
        for i, (question, filters) in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {question}")
            
            result = rag_agent.query(question, filters=filters)
            
            if result.get('success'):
                print(f"✓ 成功 - 耗时: {result.get('processing_time', 0):.2f}秒")
            else:
                print(f"✗ 失败 - {result.get('error', '未知错误')}")
            
            time.sleep(1)  # 避免过快
        
        # 3. 获取性能报告
        print("\n3. 生成性能报告...")
        
        if hasattr(rag_agent, 'get_performance_report'):
            report = rag_agent.get_performance_report()
            print(report)
        else:
            print("⚠️ 性能报告功能未实现")
        
        # 4. 检查警告是否解决
        print("\n4. 检查警告状态...")
        print("- LangChain弃用警告: 检查控制台输出")
        print("- StdOutCallbackHandler警告: 检查控制台输出")
        
        print("\n✓ 测试完成！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhancements()
