#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终日期格式测试
验证所有支持的K线查询日期格式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from datetime import datetime

def test_final_date_formats():
    """最终日期格式测试"""
    sql_agent = SQLAgent()
    current_year = datetime.now().year
    
    print("K线查询日期格式最终验证")
    print("=" * 80)
    
    # 所有支持的日期格式测试用例
    test_cases = [
        # 1. 标准格式
        ("贵州茅台从2025-06-01到2025-06-30的K线", "标准YYYY-MM-DD格式"),
        ("贵州茅台从2025-6-1到2025-6-30的K线", "YYYY-M-D格式（单数字月日）"),
        
        # 2. 斜杠格式
        ("宁德时代从2025/06/01到2025/06/30的K线", "YYYY/MM/DD格式"),
        ("宁德时代从2025/6/1到2025/6/30的K线", "YYYY/M/D格式（单数字月日）"),
        
        # 3. 中文格式
        ("比亚迪从2025年6月1日到2025年6月30日的K线", "完整中文格式"),
        ("比亚迪从6月1日到6月30日的K线", f"省略年份格式（默认{current_year}年）"),
        
        # 4. 纯数字格式
        ("中国平安从20250601到20250630的K线", "YYYYMMDD格式"),
        
        # 5. 混合格式
        ("万科A从2025-06-01到6月30日的K线", "混合格式1"),
        ("平安银行从6月1日到2025/06/30的K线", "混合格式2"),
    ]
    
    success_count = 0
    
    for query, desc in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 60)
        
        result = sql_agent._try_quick_query(query)
        
        if result and result.get('success'):
            print("✅ 快速路由成功")
            
            # 检查结构化数据
            if 'structured_data' in result:
                structured = result['structured_data']
                period = structured['period']
                stock_name = structured['stock_info']['name']
                stock_code = structured['stock_info']['code']
                data_count = structured['summary']['total_days']
                
                print(f"股票: {stock_name} ({stock_code})")
                print(f"周期: {period}")
                print(f"数据点数: {data_count}")
                
                # 特殊验证：省略年份的情况
                if "6月1日到6月30日" in query or "6月1日到2025" in query:
                    if str(current_year) in period:
                        print(f"✅ 省略年份正确使用今年({current_year})")
                    
                success_count += 1
            else:
                print("❌ 缺少结构化数据")
        else:
            print("❌ 快速路由失败")
    
    print("\n" + "=" * 80)
    print(f"测试结果: {success_count}/{len(test_cases)} 成功")
    
    if success_count == len(test_cases):
        print("✅ 所有日期格式测试通过！")
    else:
        print("❌ 部分测试失败，请检查")
    
    print("\n支持的日期格式总结:")
    print("1. YYYY-MM-DD 和 YYYY-M-D")
    print("2. YYYY/MM/DD 和 YYYY/M/D")  
    print("3. YYYY年MM月DD日 和 MM月DD日（无年份默认今年）")
    print("4. YYYYMMDD")
    print("5. 以上格式的任意组合")

if __name__ == "__main__":
    test_final_date_formats()