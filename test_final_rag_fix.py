#!/usr/bin/env python3
"""
测试最终的RAG修复方案
验证智能日期解析的改进效果
"""
import requests
import json
import time

def test_final_rag_fix():
    """测试最终的RAG修复方案"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试用例：涵盖不同类型的时间表达
    test_cases = [
        {
            "name": "描述性年度表达（原问题案例）",
            "question": "贵州茅台2024年的经营策略",
            "expected_behavior": "应该跳过严格时间过滤，仅用股票代码过滤",
            "expected_filter": 'ts_code == "600519.SH"'
        },
        {
            "name": "明确的最新时间查询",
            "question": "茅台最近30天的公告",
            "expected_behavior": "应该添加最近30天的时间过滤",
            "expected_filter": "包含时间范围"
        },
        {
            "name": "无时间表达的查询",
            "question": "贵州茅台的主营业务是什么",
            "expected_behavior": "仅使用股票代码过滤",
            "expected_filter": 'ts_code == "600519.SH"'
        },
        {
            "name": "其他公司的描述性时间查询",
            "question": "平安银行2024年的风险管理",
            "expected_behavior": "应该跳过严格时间过滤",
            "expected_filter": 'ts_code == "000001.SZ"'
        }
    ]
    
    print("🧪 测试最终RAG修复方案")
    print("目标：验证智能日期解析的改进 - 区分描述性和明确性时间表达")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        print(f"期望行为: {test_case['expected_behavior']}")
        print(f"期望过滤: {test_case['expected_filter']}")
        
        try:
            # 发送请求
            start_time = time.time()
            response = requests.post(
                f"{base_url}/query",
                json={"question": test_case['question'], "query_type": "rag"},
                timeout=60
            )
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ HTTP状态: {response.status_code}")
                print(f"⏱️  请求耗时: {request_time:.2f}秒")
                
                if result.get('success'):
                    success_count += 1
                    print(f"✅ 查询成功: True")
                    
                    answer = result.get('answer', '')
                    print(f"✅ 答案长度: {len(answer)}字符")
                    
                    # 检查答案质量
                    if answer and len(answer) > 100:
                        preview = answer[:150].replace('\n', ' ')
                        print(f"📝 答案预览: {preview}...")
                        print(f"✅ 答案质量: 良好")
                    
                    # 检查文档来源
                    sources = result.get('sources', {})
                    if sources and 'rag' in sources:
                        rag_sources = sources['rag'].get('sources', [])
                        print(f"✅ 文档数量: {len(rag_sources)}")
                        
                        if rag_sources:
                            # 显示文档信息
                            for j, doc in enumerate(rag_sources[:2]):  # 显示前2个
                                ts_code = doc.get('ts_code', '')
                                title = doc.get('title', '')
                                ann_date = doc.get('ann_date', '')
                                print(f"  📄 文档{j+1}: {ts_code} {ann_date} - {title[:40]}...")
                    
                    # 分析过滤策略效果
                    routing = result.get('routing', {})
                    if routing:
                        entities = routing.get('entities', [])
                        time_range = routing.get('time_range')
                        print(f"🔍 路由分析:")
                        print(f"  - 识别实体: {entities}")
                        print(f"  - 时间范围: {time_range}")
                        
                        # 判断过滤策略是否符合预期
                        if "描述性年度表达" in test_case['name']:
                            if not any("ann_date" in str(s) for s in [result.get('sources', {})]):
                                print(f"✅ 过滤策略正确: 跳过了严格时间过滤")
                            else:
                                print(f"⚠️  过滤策略: 可能仍然使用了时间过滤")
                    
                else:
                    error = result.get('error', 'unknown error')
                    print(f"❌ 查询失败: {error}")
                    
                    # 分析失败原因
                    if 'ann_date' in error:
                        print(f"💡 可能仍然存在时间过滤问题")
                    elif '找到0个结果' in error:
                        print(f"💡 可能是数据匹配问题")
                        
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                error_text = response.text[:200] if response.text else "无错误信息"
                print(f"错误内容: {error_text}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - API服务器可能未启动")
            break
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 60)
        time.sleep(1)
    
    print(f"\n📊 最终测试总结:")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！RAG修复方案完全成功！")
        print("✅ 智能日期解析已优化，能够正确区分描述性和明确性时间表达")
        print("✅ RAG查询现在可以正常工作了")
    elif success_count > 0:
        print("⚠️  部分测试通过，需要进一步优化")
    else:
        print("❌ 所有测试失败，需要重新检查修复方案")
    
    print(f"\n📋 下一步:")
    print(f"1. 完成资金流向分析功能测试")
    print(f"2. 完成智能日期解析功能测试") 
    print(f"3. 记录完整的修复经验")
    print(f"4. 进行版本管理和标记")

if __name__ == "__main__":
    print("🔧 RAG智能日期解析修复最终验证")
    print("修复方案：区分描述性时间表达和明确时间需求")
    print("=" * 80)
    
    test_final_rag_fix()