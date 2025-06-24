#!/usr/bin/env python
"""测试当前系统状态"""
import sys
import time

def test_money_flow():
    """测试资金流向功能"""
    print("\n=== 测试资金流向功能 ===")
    try:
        from agents.money_flow_agent import MoneyFlowAgent
        agent = MoneyFlowAgent()
        result = agent.query("茅台最近的主力资金流向")
        success = result.get('success', False)
        print(f"资金流向测试: {'✓ 成功' if success else '✗ 失败'}")
        if not success:
            print(f"错误: {result.get('error', '未知错误')}")
        return success
    except Exception as e:
        print(f"✗ 资金流向测试异常: {e}")
        return False

def test_sql():
    """测试SQL功能"""
    print("\n=== 测试SQL功能 ===")
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        result = agent.query("贵州茅台最新股价")
        success = result.get('success', False)
        print(f"SQL测试: {'✓ 成功' if success else '✗ 失败'}")
        if not success:
            print(f"错误: {result.get('error', '未知错误')}")
        return success
    except Exception as e:
        print(f"✗ SQL测试异常: {e}")
        return False

def test_rag_init():
    """测试RAG初始化（不执行查询）"""
    print("\n=== 测试RAG初始化 ===")
    try:
        print("开始初始化RAG Agent...")
        start_time = time.time()
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        elapsed = time.time() - start_time
        print(f"✓ RAG初始化成功，耗时: {elapsed:.2f}秒")
        return True
    except Exception as e:
        print(f"✗ RAG初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== 系统状态快速检查 ===")
    
    results = {
        'SQL功能': test_sql(),
        '资金流向功能': test_money_flow(),
        'RAG初始化': test_rag_init()
    }
    
    print("\n=== 测试结果 ===")
    for name, result in results.items():
        print(f"{name}: {'✓ 正常' if result else '✗ 异常'}")
    
    # 如果所有测试都通过，建议下一步操作
    if all(results.values()):
        print("\n✅ 所有测试通过，系统基本功能正常")
    else:
        print("\n⚠️ 部分功能异常，建议检查日志或考虑回滚")
        
    return all(results.values())

if __name__ == "__main__":
    sys.exit(0 if main() else 1)