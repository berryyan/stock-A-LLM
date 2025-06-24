#!/usr/bin/env python3
"""
测试HybridAgent过滤表达式修复
直接测试HybridAgent类而不需要API服务器
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent import HybridAgent
from pprint import pprint

def test_entity_extraction():
    """测试实体提取和转换"""
    print("🧪 测试实体提取和转换")
    print("=" * 60)
    
    agent = HybridAgent()
    
    test_cases = [
        {
            "question": "贵州茅台2024年的经营策略",
            "expected_entities": ["600519.SH"],
            "expected_code": "600519.SH"
        },
        {
            "question": "茅台最新公告说了什么", 
            "expected_entities": ["600519.SH"],
            "expected_code": "600519.SH"
        },
        {
            "question": "平安银行2024年财务报告",
            "expected_entities": ["000001.SZ"],
            "expected_code": "000001.SZ"
        },
        {
            "question": "600519.SH最新股价",
            "expected_entities": ["600519.SH"],
            "expected_code": "600519.SH"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['question']}")
        
        # 测试实体提取
        entities = agent._extract_entities(test_case['question'])
        print(f"提取的实体: {entities}")
        
        # 验证结果
        expected = test_case['expected_entities']
        if entities == expected:
            print(f"✅ 实体提取正确: {entities}")
        else:
            print(f"❌ 实体提取错误: 期望{expected}, 实际{entities}")
        
        # 测试转换函数
        if '茅台' in test_case['question'] or '平安银行' in test_case['question']:
            entity_in_question = '贵州茅台' if '茅台' in test_case['question'] else '平安银行'
            converted = agent._convert_entity_to_stock_code(entity_in_question)
            print(f"转换测试: '{entity_in_question}' -> '{converted}'")
            
            if converted == test_case['expected_code']:
                print(f"✅ 转换正确: {converted}")
            else:
                print(f"❌ 转换错误: 期望{test_case['expected_code']}, 实际{converted}")
        
        print("-" * 40)

def test_rag_filter_building():
    """测试RAG过滤器构建"""
    print("\n🧪 测试RAG过滤器构建")
    print("=" * 60)
    
    agent = HybridAgent()
    
    test_cases = [
        {
            "name": "贵州茅台2024年查询",
            "routing": {
                "entities": ["600519.SH"],
                "time_range": "2024"
            },
            "expected_ts_code": "600519.SH",
            "expected_start_date": "20240101",
            "expected_end_date": "20241231"
        },
        {
            "name": "平安银行最近30天查询",
            "routing": {
                "entities": ["000001.SZ"],
                "time_range": "recent_30d"
            },
            "expected_ts_code": "000001.SZ"
        },
        {
            "name": "公司名称转换测试",
            "routing": {
                "entities": ["贵州茅台"],  # 这应该被转换为股票代码
                "time_range": "2024"
            },
            "expected_ts_code": "600519.SH",
            "test_conversion": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入路由: {test_case['routing']}")
        
        # 构建过滤器
        filters = agent._build_rag_filters(test_case['routing'])
        print(f"生成的过滤器: {filters}")
        
        # 验证股票代码
        if 'ts_code' in filters:
            actual_code = filters['ts_code']
            expected_code = test_case['expected_ts_code']
            
            if actual_code == expected_code:
                print(f"✅ 股票代码正确: {actual_code}")
            else:
                print(f"❌ 股票代码错误: 期望{expected_code}, 实际{actual_code}")
        else:
            print("⚠️  未生成股票代码过滤器")
        
        # 验证日期格式
        if 'ann_date' in filters:
            date_filter = filters['ann_date']
            print(f"日期过滤器: {date_filter}")
            
            if isinstance(date_filter, dict):
                start_date = date_filter.get('start', '')
                end_date = date_filter.get('end', '')
                
                # 检查日期格式是否为YYYYMMDD
                if start_date.isdigit() and len(start_date) == 8:
                    print(f"✅ 开始日期格式正确: {start_date}")
                else:
                    print(f"❌ 开始日期格式错误: {start_date}")
                
                if end_date.isdigit() and len(end_date) == 8:
                    print(f"✅ 结束日期格式正确: {end_date}")
                else:
                    print(f"❌ 结束日期格式错误: {end_date}")
        
        print("-" * 40)

def test_routing_decision():
    """测试路由决策"""
    print("\n🧪 测试路由决策")
    print("=" * 60)
    
    agent = HybridAgent()
    
    test_questions = [
        "贵州茅台2024年的经营策略",
        "茅台最新公告说了什么",
        "平安银行2024年财务报告"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        try:
            # 测试路由决策
            routing = agent._route_query(question)
            print(f"路由决策结果:")
            pprint(routing, indent=2)
            
            # 检查实体是否正确转换
            entities = routing.get('entities', [])
            print(f"识别的实体: {entities}")
            
            # 验证实体格式
            for entity in entities:
                if '.' in entity and (entity.endswith('.SH') or entity.endswith('.SZ')):
                    print(f"✅ 实体格式正确: {entity}")
                else:
                    print(f"❌ 实体格式可能错误: {entity}")
            
        except Exception as e:
            print(f"❌ 路由决策失败: {e}")
        
        print("-" * 40)

def main():
    """主测试函数"""
    print("🔧 HybridAgent过滤表达式修复测试")
    print("测试目标: 确保公司名称正确转换为股票代码，日期格式正确")
    print("=" * 80)
    
    try:
        # 测试实体提取和转换
        test_entity_extraction()
        
        # 测试RAG过滤器构建
        test_rag_filter_building()
        
        # 测试路由决策
        test_routing_decision()
        
        print("\n📋 测试总结:")
        print("✅ 所有测试完成")
        print("🔍 查看输出中的❌标记来识别需要修复的问题")
        print("💡 主要检查点:")
        print("   - 公司名称是否正确转换为股票代码（如 贵州茅台 -> 600519.SH）") 
        print("   - 日期格式是否为YYYYMMDD而不是中文格式")
        print("   - 过滤表达式是否使用正确的字段值")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()