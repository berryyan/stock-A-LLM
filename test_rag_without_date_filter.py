#!/usr/bin/env python3
"""
测试禁用时间过滤后的RAG查询
"""
import requests
import json
import time

def test_rag_without_date_filter():
    """测试禁用时间过滤后的RAG查询"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试用例
    test_cases = [
        {
            "name": "贵州茅台经营策略查询（原失败案例）",
            "question": "贵州茅台2024年的经营策略",
            "expected": "应该找到相关文档"
        },
        {
            "name": "茅台公告查询",
            "question": "茅台最新公告说了什么",
            "expected": "应该找到相关文档"
        },
        {
            "name": "平安银行查询",
            "question": "平安银行的经营风险",
            "expected": "应该找到相关文档"
        },
        {
            "name": "简单公司查询",
            "question": "贵州茅台的主营业务是什么",
            "expected": "应该找到相关文档"
        }
    ]
    
    print("🧪 测试禁用时间过滤后的RAG查询")
    print("目标：验证去除时间过滤后RAG查询能否找到文档")
    print("=" * 70)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        print(f"期望: {test_case['expected']}")
        
        try:
            # 发送请求
            response = requests.post(
                f"{base_url}/query",
                json={"question": test_case['question'], "query_type": "rag"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ HTTP状态: {response.status_code}")
                print(f"✅ 查询成功: {result.get('success', False)}")
                
                if result.get('success'):
                    success_count += 1
                    
                    answer = result.get('answer', '')
                    print(f"✅ 答案长度: {len(answer)}字符")
                    
                    if answer:
                        # 显示答案的前200字符
                        preview = answer[:200].replace('\n', ' ')
                        print(f"📝 答案预览: {preview}...")
                    
                    # 检查文档来源
                    sources = result.get('sources', {})
                    if sources and 'rag' in sources:
                        rag_sources = sources['rag'].get('sources', [])
                        if rag_sources:
                            print(f"✅ 找到文档数量: {len(rag_sources)}")
                            
                            # 显示第一个文档信息
                            first_doc = rag_sources[0]
                            ts_code = first_doc.get('ts_code', '')
                            title = first_doc.get('title', '')
                            ann_date = first_doc.get('ann_date', '')
                            print(f"📄 首个文档: {ts_code} {ann_date} - {title[:50]}...")
                        else:
                            print("⚠️  未找到文档来源")
                    else:
                        print("⚠️  响应中无文档来源信息")
                        
                    print(f"⏱️  处理时间: {result.get('processing_time', 'N/A')}秒")
                    
                else:
                    error = result.get('error', 'unknown error')
                    print(f"❌ 查询失败: {error}")
                    
                    # 检查是否仍然是过滤器问题
                    if '找到0个结果' in error or '未找到相关文档' in error:
                        print("💡 可能仍然存在过滤器或数据问题")
                        
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                error_text = response.text[:200] if response.text else "无错误信息"
                print(f"错误内容: {error_text}...")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时（60秒）")
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - API服务器可能未启动")
            print("💡 请在Windows环境中启动API服务器")
            break
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 50)
        time.sleep(1)  # 避免请求过快
    
    print(f"\n📊 测试总结:")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count > 0:
        print("✅ 禁用时间过滤后RAG查询开始工作了！")
        print("💡 这证实了问题确实是智能日期解析过度干预造成的")
        print("📋 下一步：需要优化智能日期解析的触发条件")
    else:
        print("❌ 仍然无法找到文档")
        print("💡 可能还有其他问题：")
        print("   - 数据库中没有相关股票的文档")
        print("   - 向量搜索算法问题")
        print("   - 股票代码过滤仍然有问题")

def test_direct_hybrid_agent():
    """直接测试HybridAgent（绕过API）"""
    print("\n🔬 直接测试HybridAgent（绕过API）")
    print("=" * 50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from agents.hybrid_agent import HybridAgent
        
        print("✅ HybridAgent加载成功")
        
        agent = HybridAgent()
        print("✅ HybridAgent初始化成功")
        
        # 测试查询
        question = "贵州茅台2024年的经营策略"
        print(f"🔍 测试查询: {question}")
        
        result = agent.query(question)
        print(f"📝 查询结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        print("💡 可能存在依赖问题，建议通过API测试")

if __name__ == "__main__":
    print("🔧 RAG查询时间过滤问题修复验证")
    print("修改内容：")
    print("1. 禁用RAG Agent中的智能日期解析")
    print("2. 禁用HybridAgent中的时间过滤逻辑")
    print("=" * 80)
    
    # 测试通过API
    test_rag_without_date_filter()
    
    # 如果API不可用，尝试直接测试
    # test_direct_hybrid_agent()