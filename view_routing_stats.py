#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看路由决策统计
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.routing_monitor import routing_monitor, generate_routing_report
from utils.logger import setup_logger

logger = setup_logger("view_routing_stats")


def view_stats():
    """查看统计数据"""
    print("="*70)
    print("路由决策统计系统")
    print("="*70)
    
    # 生成并打印报告
    report = routing_monitor.generate_report()
    print(report)
    
    # 获取详细统计
    stats = routing_monitor.get_statistics()
    
    # 显示额外的分析
    print("\n\n补充分析:")
    print("="*60)
    
    # 路由效率分析
    if stats['routing_distribution']:
        total = stats['total_queries']
        print("\n路由效率分析:")
        
        # 计算简单查询比例
        simple_queries = (stats['routing_distribution'].get('SQL_ONLY', 0) + 
                         stats['routing_distribution'].get('RAG_ONLY', 0))
        if total > 0:
            simple_ratio = simple_queries / total * 100
            print(f"- 简单查询占比: {simple_ratio:.1f}% (SQL_ONLY + RAG_ONLY)")
        
        # 计算复杂查询比例
        complex_queries = (stats['routing_distribution'].get('PARALLEL', 0) + 
                          stats['routing_distribution'].get('COMPLEX', 0))
        if total > 0:
            complex_ratio = complex_queries / total * 100
            print(f"- 复杂查询占比: {complex_ratio:.1f}% (PARALLEL + COMPLEX)")
    
    # 性能建议
    print("\n性能优化建议:")
    
    # 基于响应时间给出建议
    slow_types = []
    for query_type, time_data in stats['avg_response_times'].items():
        if time_data['avg'] > 30:  # 超过30秒
            slow_types.append((query_type, time_data['avg']))
    
    if slow_types:
        print("- 以下查询类型响应较慢，建议优化:")
        for query_type, avg_time in slow_types:
            print(f"  * {query_type}: 平均{avg_time:.1f}秒")
    else:
        print("- 所有查询类型响应时间正常")
    
    # 错误率分析
    print("\n错误率分析:")
    for query_type, data in stats['success_rates'].items():
        if data['rate'] < 90:  # 成功率低于90%
            print(f"- {query_type} 成功率较低 ({data['rate']:.1f}%)，需要关注")
    
    # 保存最新统计
    print("\n正在保存统计数据...")
    routing_monitor.save_stats()
    print("✅ 统计数据已保存")


def test_with_queries():
    """使用一些测试查询来生成统计数据"""
    print("\n\n测试查询以生成统计数据...")
    print("="*60)
    
    from agents.hybrid_agent import HybridAgent
    
    try:
        agent = HybridAgent()
        
        test_queries = [
            "贵州茅台最新股价",
            "分析茅台的财务健康度",
            "茅台最新公告内容",
            "茅台的资金流向如何",
            "比较茅台和五粮液的股价",
            "分析银行板块的整体表现"
        ]
        
        print(f"执行{len(test_queries)}个测试查询...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. {query}")
            try:
                result = agent.query(query)
                if result.get('success'):
                    print("   ✅ 成功")
                else:
                    print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ 异常: {e}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='查看路由决策统计')
    parser.add_argument('--test', action='store_true', help='运行测试查询')
    parser.add_argument('--report', action='store_true', help='只显示报告')
    
    args = parser.parse_args()
    
    if args.test:
        test_with_queries()
        print("\n" + "="*70 + "\n")
    
    # 显示统计
    view_stats()


if __name__ == "__main__":
    main()