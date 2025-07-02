#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试市值排名的日期处理问题
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from datetime import datetime

def test_market_cap_date_issue():
    """测试市值排名的日期处理"""
    
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试查询列表 - 包含不同的日期表达
    test_queries = [
        # 默认查询（应该返回最新交易日）
        "总市值最大的前10只股票",
        "市值排名前20",
        
        # 指定今天
        "今天总市值最大的前10只股票",
        "今天市值排名前20",
        
        # 指定昨天
        "昨天总市值最大的前10只股票",
        "昨天市值排名前20",
        
        # 指定具体日期
        "20250630总市值最大的前10只股票",
        "2025-06-30市值排名前20",
        "2025年06月30日总市值最大的前10只股票",
    ]
    
    print("市值排名日期处理测试")
    print("=" * 80)
    print(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
    print("-" * 80)
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        print("-" * 40)
        
        try:
            # 测试快速路由
            quick_result = sql_agent._try_quick_query(query)
            
            if quick_result and quick_result.get('success'):
                result_text = quick_result['result']
                
                # 提取结果中的日期信息
                import re
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', result_text)
                if date_match:
                    result_date = date_match.group(1)
                    print(f"✅ 查询成功")
                    print(f"   返回数据日期: {result_date}")
                    
                    # 检查日期是否正确
                    if "今天" in query:
                        print(f"   期望: 最新交易日")
                    elif "昨天" in query:
                        print(f"   期望: 上一个交易日")
                    elif "20250630" in query or "2025-06-30" in query or "2025年06月30日" in query:
                        print(f"   期望: 2025-06-30")
                    else:
                        print(f"   期望: 最新交易日（默认）")
                else:
                    print(f"❌ 结果中未找到日期信息")
                    
                # 显示结果的前几行
                lines = result_text.split('\n')
                for i, line in enumerate(lines[:5]):
                    if line.strip():
                        print(f"   {line}")
                    if i >= 4:
                        print("   ...")
                        break
            else:
                print(f"❌ 查询失败")
                if quick_result:
                    print(f"   错误: {quick_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 出现异常: {e}")
            import traceback
            traceback.print_exc()
    
    # 清理
    sql_agent.mysql_connector.close()
    
    print("\n" + "=" * 80)
    print("测试完成")


if __name__ == "__main__":
    test_market_cap_date_issue()