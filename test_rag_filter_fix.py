#!/usr/bin/env python3
"""
测试RAG过滤表达式修复
"""
import requests
import json
import time

def test_rag_filter_fix():
    """测试修复后的RAG过滤表达式"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试用例
    test_cases = [
        {
            "name": "贵州茅台2024年经营策略查询",
            "question": "贵州茅台2024年的经营策略",
            "expected_stock_code": "600519.SH",
            "expected_date_format": "20240101"
        },
        {
            "name": "茅台最新公告查询", 
            "question": "茅台最新公告说了什么",
            "expected_stock_code": "600519.SH"
        },
        {
            "name": "平安银行财务报告查询",
            "question": "平安银行2024年财务报告",
            "expected_stock_code": "000001.SZ"
        }
    ]
    
    print("🧪 测试RAG过滤表达式修复")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        
        try:
            # 发送请求
            response = requests.post(
                f"{base_url}/query",
                json={"question": test_case['question'], "query_type": "rag"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ 状态码: {response.status_code}")
                print(f"✅ 响应成功: {result.get('success', False)}")
                
                if result.get('success'):
                    print(f"✅ 查询类型: {result.get('query_type', 'unknown')}")
                    answer = result.get('answer', '')
                    if answer:
                        print(f"✅ 答案长度: {len(answer)}字符")
                        print(f"答案预览: {answer[:100]}...")
                    else:
                        print("⚠️  答案为空")
                    
                    # 检查源信息
                    sources = result.get('sources', {})
                    if sources and 'rag' in sources:
                        rag_sources = sources['rag'].get('sources', [])
                        print(f"✅ 文档来源数量: {len(rag_sources)}")
                        
                        # 检查第一个来源的股票代码
                        if rag_sources:
                            first_source = rag_sources[0]
                            source_ts_code = first_source.get('ts_code', 'unknown')
                            print(f"✅ 来源股票代码: {source_ts_code}")
                            
                            # 验证股票代码是否正确
                            expected_code = test_case.get('expected_stock_code')
                            if expected_code and source_ts_code == expected_code:
                                print(f"✅ 股票代码匹配正确: {source_ts_code}")
                            elif expected_code:
                                print(f"❌ 股票代码不匹配: 期望{expected_code}, 实际{source_ts_code}")
                else:
                    error = result.get('error', 'unknown error')
                    print(f"❌ 查询失败: {error}")
                    
                    # 检查是否是过滤器问题
                    if '找到0个结果' in error or '未找到相关文档' in error:
                        print("💡 可能是过滤表达式问题，检查股票代码和日期格式")
                        
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 40)
        time.sleep(2)  # 避免请求过快
    
    print("\n📋 总结:")
    print("- 检查日志中的过滤表达式是否使用正确的股票代码")
    print("- 检查日期格式是否为YYYYMMDD而不是中文格式")
    print("- 如果仍然失败，可能需要进一步调试过滤表达式生成逻辑")

if __name__ == "__main__":
    test_rag_filter_fix()