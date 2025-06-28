#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试灵活解析器集成效果
验证SQL Agent是否正确使用了灵活解析器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger
import time

logger = setup_logger("test_flexible_parser")


def test_parser_integration():
    """测试解析器集成"""
    print("="*70)
    print("灵活解析器集成测试")
    print("="*70)
    
    # 初始化SQL Agent
    print("\n初始化SQL Agent（已集成灵活解析器）...")
    agent = SQLAgent()
    print("✅ 初始化完成")
    
    # 测试可能触发解析错误的查询
    test_cases = [
        {
            "name": "标准查询",
            "query": "茅台最新股价",
            "description": "测试正常查询流程"
        },
        {
            "name": "复杂查询",
            "query": "查询贵州茅台最近5天的开盘价、收盘价和涨跌幅",
            "description": "测试复杂数据返回"
        },
        {
            "name": "财务查询",
            "query": "比亚迪最新一期的营业收入和净利润",
            "description": "测试财务数据查询"
        },
        {
            "name": "统计查询",
            "query": "今天涨幅最大的3只股票",
            "description": "测试排名统计查询"
        },
        {
            "name": "中文表达",
            "query": "万科的总市值是多少",
            "description": "测试中文表达理解"
        }
    ]
    
    success_count = 0
    parse_error_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {test['name']}")
        print(f"查询: {test['query']}")
        print(f"说明: {test['description']}")
        print("-"*60)
        
        start_time = time.time()
        
        try:
            result = agent.query(test['query'])
            elapsed = time.time() - start_time
            
            if result['success']:
                # 检查结果中是否包含解析错误的痕迹
                result_str = str(result.get('result', ''))
                
                if "Could not parse" in result_str:
                    print(f"⚠️ 发现解析错误痕迹（但已恢复）")
                    parse_error_count += 1
                elif "查询处理过程中遇到格式问题" in result_str:
                    print(f"❌ 解析失败，返回了错误提示")
                else:
                    print(f"✅ 查询成功！(耗时: {elapsed:.2f}秒)")
                    success_count += 1
                
                # 显示结果预览
                print(f"结果: {result_str[:150]}...")
                
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    # 总结
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")
    print(f"总测试数: {len(test_cases)}")
    print(f"完全成功: {success_count}")
    print(f"解析恢复: {parse_error_count}")
    print(f"失败数: {len(test_cases) - success_count - parse_error_count}")
    
    print("\n灵活解析器集成效果:")
    if success_count == len(test_cases):
        print("✅ 完美！所有查询都成功处理")
    elif success_count + parse_error_count == len(test_cases):
        print("✅ 良好！虽有解析错误但都成功恢复")
    else:
        print("⚠️ 需要进一步优化")
    
    return success_count


def test_edge_cases():
    """测试边界情况"""
    print(f"\n\n{'='*70}")
    print("边界情况测试（灵活解析器）")
    print(f"{'='*70}")
    
    agent = SQLAgent()
    
    # 故意触发解析错误的查询
    edge_queries = [
        "SELECT * FROM tu_daily_detail LIMIT 1",  # 直接SQL
        "Final Answer",  # 不完整的答案
        "贵州茅台(600519.SH)在2025年6月27日的股价为",  # 不完整的结果
    ]
    
    for query in edge_queries:
        print(f"\n测试查询: '{query}'")
        try:
            result = agent.query(query)
            if result['success']:
                print(f"结果: {result['result'][:100]}...")
            else:
                print(f"错误: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"异常: {e}")


def check_parser_logs():
    """检查解析器相关日志"""
    print(f"\n\n{'='*70}")
    print("解析器日志检查")
    print(f"{'='*70}")
    
    log_keywords = [
        "使用灵活解析器",
        "成功提取LLM输出",
        "检测到输出解析错误",
        "灵活解析器处理"
    ]
    
    print("\n请检查日志文件中是否包含以下关键词：")
    for keyword in log_keywords:
        print(f"- {keyword}")
    
    print("\n日志文件位置: logs/sql_agent.log")


def main():
    """主测试函数"""
    print("开始测试灵活解析器集成效果...\n")
    
    # 运行集成测试
    success_count = test_parser_integration()
    
    # 运行边界测试
    test_edge_cases()
    
    # 日志检查提示
    check_parser_logs()
    
    print("\n\n测试完成！")
    
    if success_count >= 4:  # 至少4个成功
        print("✅ 灵活解析器集成成功！")
    else:
        print("⚠️ 需要进一步调试")
    
    print("\n建议：")
    print("1. 查看 logs/sql_agent.log 确认解析器工作情况")
    print("2. 如果仍有解析错误，可以调整 prompt 格式")
    print("3. 考虑为不同查询类型创建专门的输出模板")


if __name__ == "__main__":
    main()