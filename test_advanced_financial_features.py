#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务分析代理高级功能测试
测试杜邦分析、现金流质量分析、多期对比分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent

def test_dupont_analysis():
    """测试杜邦分析功能"""
    print("🧪 测试杜邦分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_cases = [
        {"ts_code": "600519.SH", "name": "贵州茅台"},
        {"ts_code": "000001.SZ", "name": "平安银行"}
    ]
    
    for case in test_cases:
        print(f"\n📊 {case['name']} ({case['ts_code']}) 杜邦分析:")
        print("-" * 50)
        
        try:
            result = agent.dupont_analysis(case['ts_code'])
            
            if result['success']:
                print(f"✅ 分析成功")
                print(f"📅 报告期: {result['period']}")
                
                dupont = result['dupont_metrics']
                if dupont['valid']:
                    print(f"📈 净利率: {dupont['net_profit_margin']:.2f}%")
                    print(f"📈 总资产周转率: {dupont['asset_turnover']:.3f}次")
                    print(f"📈 权益乘数: {dupont['equity_multiplier']:.2f}倍")
                    print(f"📈 计算ROE: {dupont['calculated_roe']:.2f}%")
                    print(f"📈 报告ROE: {dupont['reported_roe']:.2f}%")
                    print(f"📈 差异: {dupont['variance']:.2f}%")
                else:
                    print("❌ 数据不完整，无法进行杜邦分析")
                
                # 显示分析报告摘要
                if result.get('analysis_report'):
                    report_preview = result['analysis_report'][:200] + "..."
                    print(f"📝 分析报告摘要: {report_preview}")
                
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_cash_flow_quality():
    """测试现金流质量分析功能"""
    print("\n🧪 测试现金流质量分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_cases = [
        {"ts_code": "600519.SH", "name": "贵州茅台"},
        {"ts_code": "000002.SZ", "name": "万科A"}
    ]
    
    for case in test_cases:
        print(f"\n💰 {case['name']} ({case['ts_code']}) 现金流质量分析:")
        print("-" * 50)
        
        try:
            result = agent.cash_flow_quality_analysis(case['ts_code'])
            
            if result['success']:
                print(f"✅ 分析成功")
                
                quality = result['quality_analysis']
                print(f"📊 平均现金含量比率: {quality['average_cash_content']:.2f}")
                print(f"📊 稳定性评分: {quality['stability_score']:.0f}/100")
                print(f"📊 综合评级: {quality['overall_rating']}")
                print(f"📊 趋势: {quality['trend']}")
                
                # 显示近期现金流情况
                if quality['periods']:
                    print("\n近期现金流情况:")
                    for period in quality['periods'][:3]:
                        print(f"  {period['period']}: 经营现金流{period['operating_cf_billion']}亿, "
                              f"净利润{period['net_income_billion']}亿, "
                              f"现金含量{period['cash_content_ratio']:.2f} ({period['quality_rating']})")
                
                # 显示分析报告摘要
                if result.get('analysis_report'):
                    report_preview = result['analysis_report'][:200] + "..."
                    print(f"\n📝 分析报告摘要: {report_preview}")
                
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_multi_period_comparison():
    """测试多期财务对比分析功能"""
    print("\n🧪 测试多期财务对比分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_cases = [
        {"ts_code": "600519.SH", "name": "贵州茅台"}
    ]
    
    for case in test_cases:
        print(f"\n📈 {case['name']} ({case['ts_code']}) 多期财务对比:")
        print("-" * 50)
        
        try:
            result = agent.multi_period_comparison(case['ts_code'])
            
            if result['success']:
                print(f"✅ 分析成功")
                
                comparison = result['comparison_analysis']
                
                # 同比增长率
                yoy = comparison.get('yoy_growth', {})
                if yoy:
                    print("\n📊 同比增长率:")
                    print(f"  营收: {yoy.get('revenue_yoy', 'N/A')}%")
                    print(f"  净利润: {yoy.get('net_income_yoy', 'N/A')}%")
                    print(f"  经营现金流: {yoy.get('operating_cf_yoy', 'N/A')}%")
                
                # 环比增长率
                qoq = comparison.get('qoq_growth', {})
                if qoq:
                    print("\n📊 环比增长率:")
                    print(f"  营收: {qoq.get('revenue_qoq', 'N/A')}%")
                    print(f"  净利润: {qoq.get('net_income_qoq', 'N/A')}%")
                    print(f"  经营现金流: {qoq.get('operating_cf_qoq', 'N/A')}%")
                
                # 趋势分析
                trends = comparison.get('trend_analysis', {})
                if trends:
                    print("\n📊 趋势分析:")
                    print(f"  ROE趋势: {trends.get('roe_trend', 'N/A')}")
                    print(f"  营收趋势: {trends.get('revenue_trend', 'N/A')}")
                    print(f"  净利润趋势: {trends.get('profit_trend', 'N/A')}")
                
                # 稳定性分析
                volatility = comparison.get('volatility_analysis', {})
                if volatility:
                    print("\n📊 稳定性分析:")
                    print(f"  财务稳定性: {volatility.get('stability_rating', 'N/A')}")
                    print(f"  ROE波动率: {volatility.get('roe_volatility', 'N/A')}%")
                
                # 显示分析报告摘要
                if result.get('analysis_report'):
                    report_preview = result['analysis_report'][:200] + "..."
                    print(f"\n📝 分析报告摘要: {report_preview}")
                
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_natural_language_queries():
    """测试自然语言查询新功能"""
    print("\n🧪 测试自然语言查询新功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_queries = [
        "分析贵州茅台的杜邦分析",
        "600519.SH的现金流质量如何",
        "茅台的多期财务对比分析",
        "平安银行的ROE分解分析"
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
                
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")

def main():
    """主测试函数"""
    print("🚀 财务分析代理高级功能测试")
    print("=" * 80)
    
    try:
        # 测试杜邦分析
        test_dupont_analysis()
        
        # 测试现金流质量分析
        test_cash_flow_quality()
        
        # 测试多期对比分析
        test_multi_period_comparison()
        
        # 测试自然语言查询
        test_natural_language_queries()
        
        print("\n" + "=" * 80)
        print("✅ 所有高级功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")

if __name__ == "__main__":
    main()