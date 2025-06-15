# final_api_test.py
# 最终的API功能测试

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print('='*60)

def test_basic_health():
    """测试基础健康检查"""
    print_header("1. 基础健康检查")
    
    # 健康检查
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API状态: {data['status']}")
        print(f"   MySQL: {'✅' if data['mysql'] else '❌'}")
        print(f"   Milvus: {'✅' if data['milvus'] else '❌'}")
    
    # 系统状态
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        data = response.json()
        print(f"\n系统状态:")
        print(f"   文档数量: {data['documents_count']:,}")
        print(f"   最后更新: {data['last_update']}")

def test_sql_queries():
    """测试SQL查询功能"""
    print_header("2. SQL查询测试")
    
    sql_queries = [
        "贵州茅台最新股价",
        "600519今天的成交量",
        "贵州茅台最近5天的平均价格",
    ]
    
    for query in sql_queries:
        print(f"\n查询: {query}")
        
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功")
                print(f"   查询类型: {result.get('query_type')}")
                answer = result.get('answer', '')
                if isinstance(answer, str):
                    print(f"   回答: {answer[:150]}...")
                else:
                    print(f"   ⚠️  回答格式异常: {type(answer)}")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")

def test_rag_queries():
    """测试RAG查询功能"""
    print_header("3. RAG查询测试")
    
    rag_queries = [
        "贵州茅台2024年第一季度营收情况",
        "茅台最新的年度报告主要内容",
        "贵州茅台的经营战略",
    ]
    
    for query in rag_queries:
        print(f"\n查询: {query}")
        
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query, "top_k": 3},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功")
                print(f"   查询类型: {result.get('query_type')}")
                answer = result.get('answer', '')
                print(f"   回答长度: {len(answer)} 字符")
                sources = result.get('sources', [])
                if sources:
                    print(f"   数据源: {len(sources)} 个文档")
                    for i, source in enumerate(sources[:2], 1):
                        print(f"     {i}. {source.get('title', 'N/A')[:50]}...")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")

def test_complex_queries():
    """测试复杂查询"""
    print_header("4. 复杂查询测试")
    
    complex_queries = [
        "结合股价走势和财报数据，分析贵州茅台的投资价值",
        "比较贵州茅台最近的股价表现和业绩增长情况",
    ]
    
    for query in complex_queries:
        print(f"\n查询: {query}")
        
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功")
                print(f"   查询类型: {result.get('query_type')}")
                answer = result.get('answer', '')
                if answer:
                    # 打印前300个字符
                    preview = answer[:300] + "..." if len(answer) > 300 else answer
                    print(f"   回答预览:\n     {preview}")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")

def test_other_endpoints():
    """测试其他端点"""
    print_header("5. 其他功能测试")
    
    # 测试建议
    print("\n获取查询建议:")
    response = requests.get(f"{BASE_URL}/suggestions")
    if response.status_code == 200:
        suggestions = response.json()
        print(f"✅ 获得 {len(suggestions)} 个建议")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"   {i}. {s}")
    
    # 测试最近报告
    print("\n\n获取最近报告:")
    response = requests.get(f"{BASE_URL}/reports/recent")
    if response.status_code == 200:
        reports = response.json()
        print(f"✅ 获得最近的报告信息")
        # 处理可能的不同响应格式
        if isinstance(reports, list):
            for report in reports[:3]:
                print(f"   - {report.get('title', str(report))[:60]}...")
        elif isinstance(reports, dict):
            for key, value in list(reports.items())[:3]:
                print(f"   - {key}: {str(value)[:60]}...")

def test_performance():
    """测试性能和响应时间"""
    print_header("6. 性能测试")
    
    queries = [
        ("简单SQL查询", "茅台股价"),
        ("中等复杂度", "茅台2024年营收和利润"),
        ("复杂分析", "分析茅台的财务状况和发展前景"),
    ]
    
    for desc, query in queries:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            status = "✅ 成功" if result.get('success') else "❌ 失败"
            print(f"\n{desc}: {status}")
            print(f"   响应时间: {elapsed:.2f} 秒")
            if result.get('success'):
                print(f"   查询类型: {result.get('query_type')}")
        else:
            print(f"\n{desc}: ❌ HTTP {response.status_code}")
            print(f"   响应时间: {elapsed:.2f} 秒")

def main():
    """主测试函数"""
    print("="*60)
    print("股票分析系统 API 完整测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print("="*60)
    
    try:
        # 运行所有测试
        test_basic_health()
        test_sql_queries()
        test_rag_queries()
        test_complex_queries()
        test_other_endpoints()
        test_performance()
        
        print_header("测试完成")
        print("\n✨ 所有测试已完成！")
        print("\n下一步建议:")
        print("1. 检查测试结果，确认所有功能正常")
        print("2. 如有失败的测试，查看API服务日志")
        print("3. 可以开始使用API进行实际的股票分析")
        print("4. 考虑开发前端界面或集成到其他应用")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
