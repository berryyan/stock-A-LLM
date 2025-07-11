#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL Agent板块查询功能增强
验证同时支持板块代码和板块名称的查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from agents.sql_agent import SQLAgent
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sector_query_enhancement():
    """测试板块查询功能增强"""
    print("\n" + "="*80)
    print("SQL Agent 板块查询功能增强测试")
    print("="*80)
    
    # 测试用例
    test_cases = [
        # 原有的板块名称查询（应该继续工作）
        ("银行板块的主力资金", "板块名称查询"),
        ("新能源板块的主力资金", "板块名称查询"),
        
        # 新增：板块代码查询（需要实现）
        ("BK0475.DC的主力资金", "板块代码查询"),
        ("BK1036.DC的主力资金", "板块代码查询"),
        
        # 混合测试
        ("查询银行板块昨天的主力资金", "板块名称+时间"),
        ("BK0475.DC今天的主力资金", "板块代码+时间"),
        
        # 边界测试
        ("银行的主力资金", "缺少板块后缀"),
        ("不存在板块的主力资金", "无效板块名称"),
    ]
    
    # 只测试模块化版本
    agent = SQLAgentModular()
    
    print("\n测试SQL Agent (模块化版本)")
    print("-" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    for query, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        
        try:
            result = agent.query(query)
            
            success = result.get('success', False)
            error = result.get('error', '')
            
            if success:
                print(f"结果: ✅ 成功")
                # 显示结果预览
                result_text = str(result.get('result', ''))[:200]
                if len(result.get('result', '')) > 200:
                    result_text += "..."
                print(f"预览: {result_text}")
                success_count += 1
            else:
                print(f"结果: ❌ 失败")
                print(f"错误: {error}")
                
        except Exception as e:
            print(f"结果: ❌ 异常")
            print(f"异常: {str(e)}")
    
    # 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    # 判断是否需要修复
    if success_count < total_count:
        print("\n需要增强的功能:")
        print("1. 支持板块代码查询（如BK0475.DC）")
        print("2. 统一使用sector_code_mapper进行板块映射")
        print("3. 优化错误提示信息")


if __name__ == "__main__":
    test_sector_query_enhancement()