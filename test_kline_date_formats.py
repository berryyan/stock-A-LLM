#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试K线查询的各种日期格式和表达方式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import QueryTemplateLibrary
from agents.sql_agent import SQLAgent

def test_kline_date_formats():
    """测试K线查询的各种日期格式"""
    print("K线查询日期格式全面测试")
    print("=" * 80)
    
    # 初始化组件
    query_templates = QueryTemplateLibrary()
    sql_agent = SQLAgent()
    
    # 测试用例分组
    test_groups = {
        "具体日期范围格式": [
            "600036.SH从2025年6月1日到2025年6月30日的K线",
            "贵州茅台从2025-06-01到2025-06-27的K线",
            "中国平安从20250601到20250630的K线",
        ],
        
        "相对时间表达": [
            "中国平安最近10天的K线",
            "万科A过去5天的K线",
            "比亚迪最近一个月的K线",
            "平安银行最近3个月的K线",
            "贵州茅台近20个交易日的K线",
            "招商银行最近30个交易日的K线",
        ],
        
        "特殊用例": [
            "600519.SH的K线",  # 默认90天
            "000001.SZ最近一月的走势",
            "万科A过去2个月的行情",
            "中国平安的k线",  # 小写k
        ]
    }
    
    for group_name, test_cases in test_groups.items():
        print(f"\n{group_name}")
        print("-" * 60)
        
        for query in test_cases:
            print(f"\n查询: {query}")
            
            # 1. 测试模板匹配
            template = query_templates.match_template(query)
            if template:
                print(f"✅ 匹配模板: {template.name}")
                
                # 2. 测试参数提取
                params = query_templates.extract_params(query, template)
                print(f"提取参数:")
                print(f"  - entities: {params.get('entities', [])[:2]}")  # 只显示前2个
                print(f"  - time_range: {params.get('time_range')}")
                print(f"  - days: {params.get('days', '未设置')}")
                
                if params.get('start_date'):
                    print(f"  - start_date: {params.get('start_date')}")
                    print(f"  - end_date: {params.get('end_date')}")
                
                # 3. 测试快速路由（只对部分测试）
                if "贵州茅台" in query or "600036.SH" in query or "中国平安" in query:
                    result = sql_agent._try_quick_query(query)
                    if result and result.get('success'):
                        print("✅ 快速路由成功")
                        content = result['result']
                        # 检查输出描述
                        if "从" in content and "到" in content:
                            print("  - 使用日期范围格式")
                        elif "最近" in content:
                            print("  - 使用相对时间格式")
                    else:
                        print("❌ 快速路由失败")
            else:
                print("❌ 模板匹配失败")
    
    print("\n" + "=" * 80)
    print("测试完成！")

if __name__ == "__main__":
    test_kline_date_formats()