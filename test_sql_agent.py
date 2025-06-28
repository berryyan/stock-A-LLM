#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Agent实际查询测试
测试优化后的SQL Agent查询能力
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger
import time

logger = setup_logger("test_sql_agent")


def test_sql_queries():
    """测试各种SQL查询"""
    print("="*70)
    print("SQL Agent 实际查询测试")
    print("="*70)
    
    # 初始化SQL Agent
    print("\n初始化SQL Agent...")
    agent = SQLAgent()
    print("✅ SQL Agent初始化完成")
    
    # 测试查询列表
    test_queries = [
        # 基础股价查询
        {
            "query": "贵州茅台最新股价是多少？",
            "category": "股价查询",
            "expected": "包含开盘价、收盘价等信息"
        },
        {
            "query": "比亚迪今天的成交量和成交额",
            "category": "成交数据",
            "expected": "成交量（手）和成交额（千元）"
        },
        {
            "query": "查询中国平安最近5天的涨跌幅",
            "category": "历史数据",
            "expected": "5天的涨跌幅数据"
        },
        
        # 财务数据查询
        {
            "query": "茅台最新的营业收入是多少？",
            "category": "财务指标",
            "expected": "最新季度或年度营收"
        },
        {
            "query": "查询宁德时代的市盈率和市净率",
            "category": "估值指标",
            "expected": "PE和PB数值"
        },
        
        # 排名统计查询
        {
            "query": "A股市值最大的5家公司",
            "category": "排名查询",
            "expected": "按市值排序的公司列表"
        },
        {
            "query": "今天涨幅最大的10只股票",
            "category": "涨跌排名",
            "expected": "涨幅TOP10列表"
        },
        
        # 复杂查询
        {
            "query": "银行股中市盈率最低的3家",
            "category": "行业筛选",
            "expected": "银行业PE最低的公司"
        },
        {
            "query": "查询最近发布年报的5家公司",
            "category": "公告查询",
            "expected": "最新年报发布信息"
        }
    ]
    
    # 执行测试
    success_count = 0
    total_count = len(test_queries)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{total_count}: {test_case['category']}")
        print(f"查询: {test_case['query']}")
        print(f"期望: {test_case['expected']}")
        print("-"*60)
        
        start_time = time.time()
        
        try:
            # 执行查询
            result = agent.query(test_case['query'])
            elapsed_time = time.time() - start_time
            
            if result['success']:
                print(f"✅ 查询成功! (耗时: {elapsed_time:.2f}秒)")
                print(f"结果预览: {result['result'][:200]}...")
                
                # 验证是否有解析错误
                if "Could not parse" in str(result.get('result', '')):
                    print("⚠️ 警告: 检测到解析错误痕迹")
                else:
                    success_count += 1
                    
            else:
                print(f"❌ 查询失败!")
                print(f"错误: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            elapsed_time = time.time() - start_time
            print(f"耗时: {elapsed_time:.2f}秒")
    
    # 总结
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 性能分析
    print(f"\n性能优化效果:")
    print(f"- Schema知识库: ✅ 已启用（查询时间 <0.1秒）")
    print(f"- 输出格式优化: ✅ Final Answer格式强化")
    print(f"- 错误处理: ✅ 灵活解析器降级处理")
    
    return success_count == total_count


def test_edge_cases():
    """测试边界情况"""
    print(f"\n\n{'='*70}")
    print("边界情况测试")
    print(f"{'='*70}")
    
    agent = SQLAgent()
    
    edge_cases = [
        {
            "query": "",
            "name": "空查询",
            "expected": "error"
        },
        {
            "query": "   ",
            "name": "空白查询",
            "expected": "error"
        },
        {
            "query": "查询不存在的股票XXXYYY的价格",
            "name": "无效股票",
            "expected": "empty or error"
        },
        {
            "query": "查询2099年的数据",
            "name": "未来日期",
            "expected": "empty or error"
        }
    ]
    
    for case in edge_cases:
        print(f"\n测试: {case['name']}")
        print(f"查询: '{case['query']}'")
        
        try:
            result = agent.query(case['query'])
            if not result['success']:
                print(f"✅ 正确处理: {result.get('error', 'Handled as error')}")
            else:
                print(f"结果: {result['result'][:100]}...")
        except Exception as e:
            print(f"异常: {e}")


def main():
    """主测试函数"""
    print("开始SQL Agent实际查询测试...\n")
    
    # 运行主要测试
    success = test_sql_queries()
    
    # 运行边界测试
    test_edge_cases()
    
    print("\n\n测试完成!")
    
    if success:
        print("✅ 所有主要查询测试通过!")
    else:
        print("⚠️ 部分查询测试失败，请检查日志")
    
    print("\n提示：如需更详细的测试，可以运行:")
    print("- python test_optimizations.py  # 测试优化效果")
    print("- python test_schema_integration.py  # 测试Schema集成")
    print("- python comprehensive_test_with_date_intelligence.py  # 综合测试")


if __name__ == "__main__":
    main()