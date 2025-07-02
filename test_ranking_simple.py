#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试新增排名模板
"""

import time
from agents.sql_agent import SQLAgent


def test_single_ranking():
    """测试单个排名查询"""
    
    print("=" * 60)
    print("单个排名查询测试")
    print("=" * 60)
    
    sql_agent = SQLAgent()
    
    # 只测试几个关键查询
    test_queries = [
        "PE最高的前5",
        "PB最低的前5",
        "利润排名前5",
        "营收排名前5",
        "ROE排名前5"
    ]
    
    for query in test_queries:
        print(f"\n测试: {query}")
        print("-" * 40)
        
        start_time = time.time()
        result = sql_agent._try_quick_query(query)
        elapsed = time.time() - start_time
        
        if result and result.get('success'):
            print(f"✅ 成功 - 耗时: {elapsed:.2f}秒")
            # 只显示前5行结果
            lines = result['result'].split('\n')
            for i, line in enumerate(lines[:8]):
                print(f"  {line}")
        else:
            print(f"❌ 失败")
            if result:
                print(f"  错误: {result.get('error')}")


if __name__ == "__main__":
    test_single_ranking()