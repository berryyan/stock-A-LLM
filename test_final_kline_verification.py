#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终K线查询验证测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent

def test_final_kline():
    """最终K线查询验证"""
    sql_agent = SQLAgent()
    
    test_cases = [
        "中国平安最近10天的K线",
        "万科A最近5天的K线", 
        "贵州茅台过去20天的K线",  # 使用全称
        "比亚迪近30天的K线",
        "中国平安的K线"
    ]
    
    print("最终K线查询验证测试")
    print("=" * 50)
    
    for query in test_cases:
        print(f"\n查询: {query}")
        
        result = sql_agent._try_quick_query(query)
        if result and result.get('success'):
            print("✅ 快速路由成功")
            content = result['result']
            
            # 检查输出中的天数描述
            if "从" in content and "到" in content:
                print("✅ 使用日期范围格式")
            elif "最近" in content or "天" in content:
                print("✅ 使用天数格式")
            
            # 显示前几行内容
            lines = content.split('\n')[:5]
            print(f"输出预览: {' | '.join(lines)}")
        else:
            print("❌ 快速路由失败")
        
        print("-" * 30)

if __name__ == "__main__":
    test_final_kline()