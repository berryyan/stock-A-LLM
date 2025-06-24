#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Analysis Agent 测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent

def test_financial_health_analysis():
    """测试财务健康度分析"""
    print("🧪 测试财务健康度分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    # 测试贵州茅台财务健康度
    test_cases = [
        {"ts_code": "600519.SH", "name": "贵州茅台"},
        {"ts_code": "000001.SZ", "name": "平安银行"},
        {"ts_code": "000002.SZ", "name": "万科A"}
    ]
    
    for case in test_cases:
        print(f"\n📊 分析 {case['name']} ({case['ts_code']}) 财务健康度:")
        print("-" * 50)
        
        try:
            result = agent.analyze_financial_health(case['ts_code'])
            
            if result['success']:
                print(f"✅ 分析成功")
                print(f"📅 报告期: {result['period']}")
                print(f"🏆 财务评级: {result['health_score']['rating']}")
                print(f"📈 总体评分: {result['health_score']['total_score']}/100")
                
                scores = result['health_score']['dimension_scores']
                print(f"📊 分维度评分:")
                print(f"   盈利能力: {scores['profitability']}/100")
                print(f"   偿债能力: {scores['solvency']}/100")
                print(f"   运营能力: {scores['operation']}/100")
                print(f"   成长能力: {scores['growth']}/100")
                
                # 显示分析报告摘要（前200字符）
                if result.get('analysis_report'):
                    report_preview = result['analysis_report'][:200] + "..."
                    print(f"📝 分析报告摘要: {report_preview}")
                
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_query_interface():
    """测试查询接口"""
    print("\n🧪 测试自然语言查询接口")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_queries = [
        "分析贵州茅台的财务健康状况",
        "600519.SH财务评级如何",
        "平安银行的盈利能力分析",
        "万科A的偿债能力怎么样"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        print("-" * 40)
        
        try:
            result = agent.query(query)
            
            if result['success']:
                print(f"✅ 查询成功")
                print(f"📊 分析类型: {result.get('analysis_type', 'unknown')}")
                print(f"📈 股票代码: {result.get('ts_code', 'unknown')}")
                print(f"⏱️ 处理时间: {result.get('processing_time', 0):.2f}秒")
                
                if 'health_score' in result:
                    print(f"🏆 财务评级: {result['health_score']['rating']}")
                    print(f"📈 总体评分: {result['health_score']['total_score']}/100")
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")

def test_data_retrieval():
    """测试数据获取功能"""
    print("\n🧪 测试财务数据获取功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_codes = ["600519.SH", "000001.SZ"]
    
    for ts_code in test_codes:
        print(f"\n📊 获取 {ts_code} 财务数据:")
        print("-" * 40)
        
        try:
            financial_data = agent.get_financial_data(ts_code, periods=4)
            
            if financial_data:
                print(f"✅ 成功获取 {len(financial_data)} 期数据")
                
                latest = financial_data[0]
                print(f"📅 最新报告期: {latest.end_date}")
                print(f"💰 营业收入: {latest.total_revenue/100000000:.2f}亿元")
                print(f"💰 净利润: {latest.n_income_attr_p/100000000:.2f}亿元")
                print(f"📊 ROE: {latest.roe:.2f}%")
                print(f"📊 资产负债率: {latest.debt_to_assets:.2f}%")
                
            else:
                print(f"❌ 未获取到数据")
                
        except Exception as e:
            print(f"❌ 数据获取异常: {e}")

def main():
    """主测试函数"""
    print("🚀 Financial Analysis Agent 功能测试")
    print("=" * 80)
    
    try:
        # 测试数据获取
        test_data_retrieval()
        
        # 测试财务健康度分析
        test_financial_health_analysis()
        
        # 测试查询接口
        test_query_interface()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")

if __name__ == "__main__":
    main()