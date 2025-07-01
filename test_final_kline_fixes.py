#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终K线查询修复验证
包括具体日期范围、各种时间表达、结构化数据输出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import json

def test_final_kline_fixes():
    """最终K线查询修复验证"""
    sql_agent = SQLAgent()
    
    print("K线查询最终修复验证")
    print("=" * 80)
    
    # 关键测试用例
    test_cases = [
        # 1. 具体日期范围（问题用例）
        "600036.SH从2025年6月1日到2025年6月30日的K线",
        
        # 2. 相对时间表达
        "中国平安最近10天的K线",
        "贵州茅台最近一个月的K线",
        "万科A最近3个月的K线",
        "比亚迪近20个交易日的K线",
        
        # 3. 默认查询
        "平安银行的K线"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {query}")
        print("-" * 60)
        
        result = sql_agent._try_quick_query(query)
        
        if result and result.get('success'):
            print("✅ 快速路由成功")
            
            # 显示文本输出的前几行
            lines = result['result'].split('\n')[:8]
            print("\n文本输出预览:")
            for line in lines:
                print(line)
            
            # 检查是否包含结构化数据
            if 'structured_data' in result:
                print("\n✅ 包含结构化数据")
                structured = result['structured_data']
                print(f"股票: {structured['stock_info']['name']} ({structured['stock_info']['code']})")
                print(f"周期: {structured['period']}")
                print(f"数据点数: {structured['summary']['total_days']}")
                print(f"平均价格: {structured['summary']['avg_price']}")
                
                # 显示前2条K线数据
                if structured['data']:
                    print("\nK线数据样例:")
                    for j, kline in enumerate(structured['data'][:2], 1):
                        print(f"  {j}. {kline['date']}: 开{kline['open']:.2f} 高{kline['high']:.2f} 低{kline['low']:.2f} 收{kline['close']:.2f} 涨跌{kline['pct_chg']:.2f}%")
            else:
                print("\n❌ 未包含结构化数据")
                
        else:
            print("❌ 快速路由失败")
    
    print("\n" + "=" * 80)
    print("前端展示实现方案总结:")
    print("-" * 40)
    print("1. 数据格式:")
    print("   - ✅ 保留原有文本格式（左侧显示）")
    print("   - ✅ 新增结构化数据（右侧K线图）")
    print("   - ✅ 包含完整OHLC数据和汇总信息")
    
    print("\n2. 前端实现建议:")
    print("   a) 检测data_type='kline'")
    print("   b) 左侧显示result文本内容")
    print("   c) 右侧使用structured_data绘制K线图")
    print("   d) 推荐使用ECharts的K线图组件")
    
    print("\n3. ECharts配置示例:")
    echarts_example = {
        "xAxis": {
            "data": ["2025-06-24", "2025-06-25", "2025-06-26", "2025-06-27", "2025-06-30"]
        },
        "yAxis": {},
        "series": [{
            "type": "candlestick",
            "data": [
                [1423.35, 1437.20, 1423.35, 1451.68],  # [开盘, 收盘, 最低, 最高]
                # ... 更多数据
            ]
        }]
    }
    print(json.dumps(echarts_example, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_final_kline_fixes()