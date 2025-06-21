#!/usr/bin/env python3
"""
基线测试 - 验证原始功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent

def baseline_test():
    """测试原始功能"""
    
    print("=== RAG Agent 基线测试 ===\n")
    
    try:
        # 1. 初始化
        print("1. 测试初始化...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功")
        
        # 2. 测试基本查询
        print("\n2. 测试基本查询...")
        result = rag_agent.query("贵州茅台最新财报")
        
        if result.get('success'):
            print("✓ 查询成功")
            print(f"  - 文档数: {result.get('document_count', 0)}")
            print(f"  - 答案长度: {len(result.get('answer', ''))}")
            print(f"  - 处理时间: {result.get('processing_time', 0):.2f}秒")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
        
        # 3. 测试过滤查询
        print("\n3. 测试过滤查询...")
        result2 = rag_agent.query(
            "分析财务数据",
            filters={"ts_code": "600519.SH"}
        )
        
        if result2.get('success'):
            print("✓ 过滤查询成功")
            print(f"  - 文档数: {result2.get('document_count', 0)}")
        else:
            print(f"✗ 过滤查询失败: {result2.get('error', '未知错误')}")
        
        # 4. 检查核心方法
        print("\n4. 检查核心方法...")
        methods = [
            '_build_filter_expr',
            '_extract_documents', 
            '_format_context',
            '_format_sources',
            '_get_chat_history'
        ]
        
        for method in methods:
            if hasattr(rag_agent, method):
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} 缺失")
        
        print("\n✓ 基线测试完成")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    baseline_test()
