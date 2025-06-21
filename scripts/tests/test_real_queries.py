# test_real_queries.py
# 测试实际的查询功能

from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent
from agents.rag_agent import RAGAgent

def test_sql_queries():
    """测试SQL查询"""
    print("=== 测试 SQL 查询 ===\n")
    
    sql_agent = SQLAgent()
    
    test_queries = [
        "贵州茅台的股票代码是什么",
        "查询股票代码600519的最新股价",
        "今天涨幅最大的5只股票"
    ]
    
    for query in test_queries:
        print(f"查询: {query}")
        result = sql_agent.query(query)
        
        if result['success']:
            print(f"✓ 成功")
            print(f"结果: {result['result'][:200]}...")
        else:
            print(f"✗ 失败: {result.get('error', 'Unknown error')}")
        print("-" * 50)

def test_hybrid_queries():
    """测试混合查询"""
    print("\n=== 测试混合查询 ===\n")
    
    hybrid_agent = HybridAgent()
    
    test_queries = [
        "贵州茅台最新股价",
        "分析贵州茅台的投资价值",
        "比较贵州茅台和五粮液的股价表现"
    ]
    
    for query in test_queries:
        print(f"查询: {query}")
        try:
            result = hybrid_agent.query(query)
            
            if result['success']:
                print(f"✓ 成功")
                print(f"查询类型: {result.get('query_type', 'unknown')}")
                print(f"答案预览: {result['answer'][:200]}...")
            else:
                print(f"✗ 失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"✗ 错误: {str(e)}")
        print("-" * 50)

def test_rag_queries():
    """测试RAG查询"""
    print("\n=== 测试 RAG 查询 ===\n")
    
    rag_agent = RAGAgent()
    
    test_queries = [
        {
            "question": "贵州茅台最新的财报有什么重要信息",
            "filters": {"ts_code": "600519.SH"}
        }
    ]
    
    for test in test_queries:
        print(f"查询: {test['question']}")
        try:
            result = rag_agent.query(
                question=test['question'],
                filters=test.get('filters')
            )
            
            if result['success']:
                print(f"✓ 成功")
                print(f"找到文档数: {result.get('document_count', 0)}")
                print(f"答案预览: {result['answer'][:200]}...")
            else:
                print(f"✗ 失败: {result.get('error', result.get('message', 'Unknown error'))}")
        except Exception as e:
            print(f"✗ 错误: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    print("股票分析系统 - 功能测试\n")
    
    # 选择测试
    print("1. 测试SQL查询")
    print("2. 测试混合查询")
    print("3. 测试RAG查询")
    print("4. 测试所有")
    print("5. 快速测试（每类一个查询）")
    
    choice = input("\n选择测试项 (1-5): ")
    
    if choice == '1':
        test_sql_queries()
    elif choice == '2':
        test_hybrid_queries()
    elif choice == '3':
        test_rag_queries()
    elif choice == '4':
        test_sql_queries()
        test_hybrid_queries()
        test_rag_queries()
    elif choice == '5':
        # 快速测试
        print("\n=== 快速测试 ===\n")
        
        # SQL测试
        print("1. SQL查询测试:")
        sql_agent = SQLAgent()
        result = sql_agent.query("贵州茅台最新股价")
        print(f"   结果: {result.get('result', 'Error')[:100]}...")
        
        # Hybrid测试
        print("\n2. 混合查询测试:")
        hybrid_agent = HybridAgent()
        result = hybrid_agent.query("贵州茅台最新股价")
        print(f"   结果: {result.get('answer', 'Error')[:100]}...")
        
        # RAG测试
        print("\n3. RAG查询测试:")
        rag_agent = RAGAgent()
        result = rag_agent.query("贵州茅台财报", filters={"ts_code": "600519.SH"})
        if result['success']:
            print(f"   找到 {result.get('document_count', 0)} 个文档")
        else:
            print(f"   失败: {result.get('message', 'Error')}")
    else:
        print("无效选择")