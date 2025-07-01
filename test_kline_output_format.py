#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试K线查询输出格式，分析前端展示需求
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import json

def test_kline_output_format():
    """测试K线查询输出格式"""
    sql_agent = SQLAgent()
    
    # 测试一个具体的K线查询
    query = "贵州茅台最近5天的K线"
    
    print("测试K线查询输出格式")
    print("=" * 80)
    print(f"查询: {query}")
    print("-" * 80)
    
    result = sql_agent._try_quick_query(query)
    
    if result and result.get('success'):
        print("\n1. 当前文本格式输出:")
        print("-" * 40)
        print(result['result'][:1000])  # 显示前1000字符
        
        print("\n\n2. 分析前端展示需求:")
        print("-" * 40)
        print("当前输出特点:")
        print("- 纯文本表格格式")
        print("- 包含完整的OHLC数据")
        print("- 按日期排序")
        print("- 包含成交量和成交额")
        
        print("\n前端展示改进建议:")
        print("1) 左侧列表展示:")
        print("   - 保持当前文本表格格式")
        print("   - 使用等宽字体确保对齐")
        print("   - 添加表格样式美化")
        
        print("\n2) 右侧K线图展示:")
        print("   - 需要返回结构化数据（JSON格式）")
        print("   - 包含原始数值数据用于图表渲染")
        print("   - 使用ECharts或类似库绘制K线图")
        
        print("\n3) 建议的返回格式:")
        suggested_format = {
            "type": "kline",
            "stock_info": {
                "name": "贵州茅台",
                "code": "600519.SH"
            },
            "period": "最近5天",
            "data": [
                {
                    "date": "2025-06-30",
                    "open": 1700.00,
                    "high": 1720.00,
                    "low": 1695.00,
                    "close": 1710.00,
                    "volume": 2500000,
                    "amount": 4250000000,
                    "pct_chg": 0.58
                }
                # ... 更多数据
            ],
            "summary": {
                "total_days": 5,
                "avg_price": 1705.00,
                "total_volume": 12500000,
                "total_amount": 21250000000
            }
        }
        
        print(json.dumps(suggested_format, indent=2, ensure_ascii=False))
        
    else:
        print("查询失败")

if __name__ == "__main__":
    test_kline_output_format()