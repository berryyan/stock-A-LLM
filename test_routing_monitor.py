#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由监控功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from agents.hybrid_agent import HybridAgent
from utils.routing_monitor import routing_monitor
from utils.logger import setup_logger

logger = setup_logger("test_routing_monitor")


def test_routing_monitor():
    """测试路由监控功能"""
    print("="*70)
    print("测试路由监控功能")
    print("="*70)
    
    # 初始化HybridAgent
    print("\n1. 初始化HybridAgent...")
    agent = HybridAgent()
    print("✅ 初始化完成")
    
    # 测试查询
    test_cases = [
        {
            "query": "贵州茅台最新股价",
            "expected_type": "SQL_ONLY",
            "description": "简单SQL查询"
        },
        {
            "query": "茅台最新的公告说了什么",
            "expected_type": "RAG_ONLY",
            "description": "文档检索查询"
        },
        {
            "query": "分析贵州茅台的财务健康状况",
            "expected_type": "FINANCIAL",
            "description": "财务分析查询"
        },
        {
            "query": "茅台最近的资金流向如何",
            "expected_type": "MONEY_FLOW",
            "description": "资金流向查询"
        },
        {
            "query": "茅台的股价和最新公告",
            "expected_type": "PARALLEL",
            "description": "并行查询"
        }
    ]
    
    print(f"\n2. 执行{len(test_cases)}个测试查询...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {test_case['description']}")
        print(f"查询: {test_case['query']}")
        print(f"预期路由: {test_case['expected_type']}")
        print("-"*60)
        
        try:
            # 执行查询
            start_time = time.time()
            result = agent.query(test_case['query'])
            elapsed = time.time() - start_time
            
            # 检查结果
            if result.get('success'):
                print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                print(f"查询类型: {result.get('query_type', 'N/A')}")
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback
            traceback.print_exc()
    
    # 等待一下确保所有记录都完成
    time.sleep(1)
    
    # 显示统计
    print(f"\n\n{'='*70}")
    print("3. 路由监控统计")
    print("="*70)
    
    stats = routing_monitor.get_statistics()
    
    print(f"\n总查询数: {stats['total_queries']}")
    
    print("\n路由分布:")
    for route_type, count in stats['routing_distribution'].items():
        print(f"  {route_type:<15} : {count}")
    
    print("\n成功率:")
    for route_type, data in stats['success_rates'].items():
        print(f"  {route_type:<15} : {data['rate']:.1f}% ({data['success']}/{data['total']})")
    
    print("\n平均响应时间:")
    for route_type, data in stats['avg_response_times'].items():
        print(f"  {route_type:<15} : {data['avg']:.2f}秒")
    
    # 生成完整报告
    print(f"\n\n{'='*70}")
    print("4. 完整统计报告")
    print("="*70)
    print(routing_monitor.generate_report())
    
    # 保存统计
    print("\n5. 保存统计数据...")
    routing_monitor.save_stats()
    print("✅ 统计数据已保存到 data/routing_stats.json")


def test_error_tracking():
    """测试错误跟踪功能"""
    print(f"\n\n{'='*70}")
    print("测试错误跟踪功能")
    print("="*70)
    
    agent = HybridAgent()
    
    # 测试一些会失败的查询
    error_queries = [
        "",  # 空查询
        "查询不存在的股票XXXYYY的信息",  # 无效股票
        "分析2099年的数据",  # 未来日期
    ]
    
    for query in error_queries:
        print(f"\n测试错误查询: '{query}'")
        try:
            result = agent.query(query)
            if not result.get('success'):
                print(f"✅ 正确处理错误: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"异常: {e}")


def main():
    """主测试函数"""
    print("开始测试路由监控系统...\n")
    
    # 清除旧的统计数据（可选）
    # routing_monitor.routing_stats['total_queries'] = 0
    
    # 运行主要测试
    test_routing_monitor()
    
    # 运行错误跟踪测试
    test_error_tracking()
    
    print("\n\n测试完成！")
    print("提示：")
    print("1. 查看统计文件: data/routing_stats.json")
    print("2. 运行 python view_routing_stats.py 查看详细报告")
    print("3. 统计数据会累积，可以手动清除文件重新开始")


if __name__ == "__main__":
    main()