# 文件名: test_agents.py
# 在项目根目录下创建此文件

"""
测试Agent功能的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from agents.rag_agent import RAGAgent
from agents.hybrid_agent import HybridAgent
import time


def test_sql_agent():
    """测试SQL Agent"""
    print("\n" + "="*60)
    print("测试 SQL Agent")
    print("="*60)
    
    try:
        # 创建SQL Agent
        sql_agent = SQLAgent()
        print("✓ SQL Agent 创建成功")
        
        # 测试查询
        test_queries = [
            "查询贵州茅台最新的股价",
            "统计最近发布年报的10家公司",
            "查找营收超过100亿的公司"
        ]
        
        for query in test_queries[:1]:  # 只测试第一个查询
            print(f"\n查询: {query}")
            result = sql_agent.query(query)
            
            if result['success']:
                print(f"✓ 查询成功")
                print(f"结果预览: {str(result['result'])[:200]}...")
            else:
                print(f"✗ 查询失败: {result.get('error', '未知错误')}")
                
    except Exception as e:
        print(f"✗ SQL Agent 测试失败: {e}")


def test_rag_agent():
    """测试RAG Agent"""
    print("\n" + "="*60)
    print("测试 RAG Agent")
    print("="*60)
    
    try:
        # 创建RAG Agent
        rag_agent = RAGAgent()
        print("✓ RAG Agent 创建成功")
        
        # 测试查询
        test_queries = [
            {
                "question": "贵州茅台2024年第一季度的经营情况如何？",
                "filters": {"ts_code": "600519.SH"}
            },
            {
                "question": "最近有哪些公司发布了重要公告？",
                "filters": None
            }
        ]
        
        for test in test_queries[:1]:  # 只测试第一个查询
            print(f"\n查询: {test['question']}")
            result = rag_agent.query(
                question=test['question'],
                filters=test['filters']
            )
            
            if result['success']:
                print(f"✓ 查询成功")
                print(f"找到 {result['document_count']} 个相关文档")
                print(f"答案预览: {result['answer'][:200]}...")
            else:
                print(f"✗ 查询失败: {result.get('error', result.get('message', '未知错误'))}")
                
    except Exception as e:
        print(f"✗ RAG Agent 测试失败: {e}")


def test_hybrid_agent():
    """测试Hybrid Agent"""
    print("\n" + "="*60)
    print("测试 Hybrid Agent")
    print("="*60)
    
    try:
        # 创建Hybrid Agent
        hybrid_agent = HybridAgent()
        print("✓ Hybrid Agent 创建成功")
        
        # 测试不同类型的查询
        test_queries = [
            "贵州茅台最新股价是多少？",  # SQL_ONLY
            "贵州茅台2024年第一季度报告说了什么？",  # RAG_ONLY
            "分析贵州茅台2024年营收增长的原因",  # HYBRID
        ]
        
        for query in test_queries[:1]:  # 只测试第一个查询
            print(f"\n查询: {query}")
            result = hybrid_agent.query(query)
            
            if result['success']:
                print(f"✓ 查询成功")
                print(f"查询类型: {result['query_type']}")
                print(f"答案预览: {str(result['answer'])[:200]}...")
            else:
                print(f"✗ 查询失败: {result.get('error', '未知错误')}")
                
    except Exception as e:
        print(f"✗ Hybrid Agent 测试失败: {e}")


def test_api_connection():
    """测试API连接"""
    print("\n" + "="*60)
    print("测试 API 连接")
    print("="*60)
    
    try:
        import requests
        
        # 测试健康检查端点
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ API 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"✗ API 健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器")
        print("请确保API服务器正在运行: python -m api.main")
    except Exception as e:
        print(f"✗ API 测试失败: {e}")


def main():
    """主测试函数"""
    print("股票分析系统 Agent 模块测试")
    print("="*60)
    
    # 检查环境变量
    from config.settings import settings
    
    print("\n检查配置...")
    print(f"MySQL数据库: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"Milvus数据库: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    print(f"DeepSeek API密钥: {'已配置' if settings.DEEPSEEK_API_KEY else '未配置'}")
    
    if not settings.DEEPSEEK_API_KEY:
        print("\n⚠️ 警告: DeepSeek API密钥未配置!")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return
    
    # 运行测试
    while True:
        print("\n选择测试项目:")
        print("1. 测试 SQL Agent")
        print("2. 测试 RAG Agent")
        print("3. 测试 Hybrid Agent")
        print("4. 测试 API 连接")
        print("5. 运行所有测试")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ")
        
        if choice == '1':
            test_sql_agent()
        elif choice == '2':
            test_rag_agent()
        elif choice == '3':
            test_hybrid_agent()
        elif choice == '4':
            test_api_connection()
        elif choice == '5':
            test_sql_agent()
            test_rag_agent()
            test_hybrid_agent()
            test_api_connection()
        elif choice == '0':
            break
        else:
            print("无效选择，请重试")
        
        input("\n按Enter继续...")


if __name__ == "__main__":
    main()
