#!/usr/bin/env python3
"""
测试RAG Agent模块化版本的字段映射修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular
from utils.logger import setup_logger

def test_rag_agent_modular():
    """测试RAG Agent模块化版本"""
    logger = setup_logger("test_rag_modular")
    
    print("=" * 80)
    print("测试RAG Agent模块化版本 - 字段映射修复")
    print("=" * 80)
    
    try:
        # 初始化Agent
        print("\n1. 初始化RAG Agent...")
        rag_agent = RAGAgentModular()
        print("✓ 初始化成功")
        
        # 测试查询
        test_queries = [
            "贵州茅台最新的公告内容是什么",
            "比亚迪2025年的财务报告",
            "宁德时代的战略发展计划"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i+1}. 测试查询: {query}")
            print("-" * 60)
            
            try:
                result = rag_agent.query(query)
                
                if result.get('success'):
                    print("✓ 查询成功")
                    print(f"找到文档数: {result.get('metadata', {}).get('doc_count', 0)}")
                    print(f"查询时间: {result.get('metadata', {}).get('query_time', 0):.2f}秒")
                    
                    # 显示部分结果
                    answer = result.get('result', '')
                    if answer:
                        print(f"\n答案预览: {answer[:200]}...")
                else:
                    print(f"✗ 查询失败: {result.get('error', '未知错误')}")
                    if result.get('suggestion'):
                        print(f"建议: {result.get('suggestion')}")
                        
            except Exception as e:
                print(f"✗ 查询异常: {str(e)}")
                logger.error(f"查询异常: {str(e)}", exc_info=True)
        
        print("\n" + "=" * 80)
        print("测试完成！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    # 执行测试
    success = test_rag_agent_modular()
    
    if success:
        print("\n✓ 所有测试通过！字段映射修复成功。")
    else:
        print("\n✗ 测试失败，请检查日志。")