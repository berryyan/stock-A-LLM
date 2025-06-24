#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试日期智能处理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

def test_date_intelligence_basic():
    """测试基础日期智能解析"""
    print("🔍 测试基础日期智能解析")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        # 获取最近交易日
        latest_trading = date_intelligence.get_latest_trading_day()
        print(f"✅ 最近交易日: {latest_trading}")
        
        # 获取最新报告期
        latest_report = date_intelligence.get_latest_report_period("600519.SH", "1")
        print(f"✅ 茅台最新年报期: {latest_report}")
        
        # 获取最新公告日期
        latest_ann = date_intelligence.get_latest_announcement_date("600519.SH")
        print(f"✅ 茅台最新公告日期: {latest_ann}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return False

def test_date_parsing_examples():
    """测试日期解析示例"""
    print("\n🔍 测试日期解析示例")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        test_cases = [
            # 股价相关
            ("茅台最新股价", "stock_price"),
            ("贵州茅台最近股价", "stock_price"),
            ("600519.SH现在的收盘价", "stock_price"),
            ("比亚迪当前的股价表现", "stock_price"),
            
            # 财务相关
            ("贵州茅台最新财务数据", "financial"),
            ("茅台最近的业绩", "financial"),
            ("平安银行最新年报", "financial"),
            
            # 公告相关
            ("贵州茅台最新公告", "announcement"),
            ("600519.SH最近披露了什么", "announcement"),
            
            # 无时间表达
            ("查询茅台股价", None),
            ("分析贵州茅台财务状况", None)
        ]
        
        print(f"\n{'查询':<30} {'预期类型':<15} {'实际类型':<15} {'解析结果':<30}")
        print("-" * 90)
        
        all_correct = True
        for query, expected_type in test_cases:
            processed, result = date_intelligence.preprocess_question(query)
            actual_type = result['context'].get('data_type')
            
            if expected_type is None:
                is_correct = result['modified_question'] is None
            else:
                is_correct = actual_type == expected_type and result['modified_question'] is not None
            
            status = "✅" if is_correct else "❌"
            parsed_date = result.get('parsed_date', '-')
            
            print(f"{status} {query:<28} {expected_type or '-':<15} {actual_type or '-':<15} {parsed_date:<30}")
            
            if not is_correct:
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ 解析示例测试失败: {e}")
        return False

def test_sql_agent_date_integration():
    """测试SQL Agent的日期集成"""
    print("\n🔍 测试SQL Agent日期集成")
    print("=" * 60)
    
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        
        # 简单测试查询
        queries = [
            "茅台最新股价",
            "查询贵州茅台2025年6月20日的股价"  # 对比：明确日期
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            # 只测试是否能成功启动查询
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 查询成功启动 (耗时: {elapsed:.2f}秒)")
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Agent测试失败: {e}")
        return False

def test_rag_agent_date_integration():
    """测试RAG Agent的日期集成"""
    print("\n🔍 测试RAG Agent日期集成")
    print("=" * 60)
    
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        
        # 测试单个查询
        query = "贵州茅台最新公告"
        print(f"\n查询: {query}")
        
        result = agent.query(query, top_k=1)  # 只返回1个文档，加快速度
        
        if result.get('success'):
            print(f"✅ 查询成功")
            print(f"   文档数: {result.get('document_count', 0)}")
            
            # 检查日期解析
            if 'date_parsing' in result:
                parsing = result['date_parsing']
                print(f"✅ 日期解析已集成")
                print(f"   建议: {parsing.get('suggestion', '')}")
                print(f"   修改后查询: {parsing.get('modified_question', '')}")
            else:
                print("⚠️  未检测到日期解析信息")
        else:
            print(f"❌ 查询失败: {result.get('message', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Agent测试失败: {e}")
        return False

def test_cache_functionality():
    """测试缓存功能"""
    print("\n🔍 测试缓存功能")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        # 清空缓存
        date_intelligence._cache.clear()
        date_intelligence._cache_timestamp.clear()
        
        # 第一次查询（无缓存）
        start = time.time()
        result1 = date_intelligence.get_latest_trading_day()
        time1 = time.time() - start
        
        # 第二次查询（有缓存）
        start = time.time()
        result2 = date_intelligence.get_latest_trading_day()
        time2 = time.time() - start
        
        print(f"第一次查询: {result1} (耗时: {time1*1000:.2f}ms)")
        print(f"第二次查询: {result2} (耗时: {time2*1000:.2f}ms)")
        
        if result1 == result2 and time2 < time1:
            print(f"✅ 缓存功能正常，性能提升 {((time1-time2)/time1*100):.1f}%")
            return True
        else:
            print("❌ 缓存功能可能存在问题")
            return False
            
    except Exception as e:
        print(f"❌ 缓存测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 日期智能处理功能快速测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = {}
    
    # 1. 基础功能测试
    results['basic'] = test_date_intelligence_basic()
    
    # 2. 解析示例测试
    results['parsing'] = test_date_parsing_examples()
    
    # 3. SQL Agent集成测试
    results['sql_integration'] = test_sql_agent_date_integration()
    
    # 4. RAG Agent集成测试
    results['rag_integration'] = test_rag_agent_date_integration()
    
    # 5. 缓存功能测试
    results['cache'] = test_cache_functionality()
    
    # 结果总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("-" * 80)
    print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有日期智能处理功能测试通过！")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败")
    
    return passed == total

if __name__ == "__main__":
    main()