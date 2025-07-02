#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试市值排名的输出格式
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import time

def test_output_format():
    """测试市值排名的输出格式"""
    
    print("市值排名输出格式测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 测试不同类型的市值查询
    test_queries = [
        ("总市值排名", "总市值排名（只显示总市值）"),
        ("市值TOP10", "市值排名（默认为总市值）"),
        ("流通市值排名", "流通市值排名（只显示流通市值）"),
        ("流通市值前5", "流通市值前5（只显示流通市值）"),
        ("今天的市值排名", "带时间的总市值排名"),
    ]
    
    for query, desc in test_queries:
        print(f"\n{'='*80}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            result = sql_agent.query(query)
            end_time = time.time()
            
            if result['success']:
                print(f"✅ 查询成功 (耗时: {end_time - start_time:.2f}秒)")
                
                # 显示完整的结果
                print("\n输出结果:")
                print(result['result'])
                
                # 检查是否使用了快速路由
                if result.get('quick_path'):
                    print("\n⚡ 使用了快速路由")
                    
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 自动继续，添加延时以便查看
        time.sleep(0.5)


def compare_formats():
    """对比旧格式和新格式"""
    
    print("\n\n格式对比")
    print("=" * 100)
    
    print("\n旧格式示例（同时显示总市值和流通市值）:")
    print("""
总市值排名 - 2025-07-01

排名 | 股票名称 | 股票代码 | 股价 | 涨跌幅 | 总市值(亿) | 流通市值(亿)
------------------------------------------------------------
 1 | 工商银行     | 601398.SH |     7.66 |   0.92% |   27300.70 |   20652.30
 2 | 建设银行     | 601939.SH |     9.71 |   2.86% |   25401.40 |     931.54
""")
    
    print("\n新格式示例（Markdown表格，只显示总市值）:")
    print("""
## 总市值排名 - 2025-07-01

| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 总市值(亿) |
|------|----------|----------|----------|--------|------------|
| 1 | 工商银行 | 601398.SH | 7.66 | 0.92% | 27300.70 |
| 2 | 建设银行 | 601939.SH | 9.71 | 2.86% | 25401.40 |
""")
    
    print("\n新格式示例（流通市值排名，只显示流通市值）:")
    print("""
## 流通市值排名 - 2025-07-01

| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 流通市值(亿) |
|------|----------|----------|----------|--------|--------------|
| 1 | 工商银行 | 601398.SH | 7.66 | 0.92% | 20652.30 |
| 2 | 农业银行 | 601288.SH | 5.96 | 1.36% | 19027.00 |
""")


def test_markdown_rendering():
    """测试Markdown渲染效果"""
    
    print("\n\nMarkdown渲染测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 执行一个快速查询
    result = sql_agent._try_quick_query("市值TOP3")
    
    if result and result.get('success'):
        print("原始输出:")
        print(result['result'])
        
        # 模拟前端渲染
        print("\n前端渲染效果预览:")
        print("┌─────────────────────────────────────────────┐")
        print("│ 总市值排名 - 2025-07-01                     │")
        print("├──────┬──────────┬───────────┬────────┬──────┤")
        print("│ 排名 │ 股票名称 │ 股票代码  │ 股价   │ 涨跌 │")
        print("├──────┼──────────┼───────────┼────────┼──────┤")
        print("│  1   │ 工商银行 │ 601398.SH │ 7.66   │ 0.92%│")
        print("│  2   │ 建设银行 │ 601939.SH │ 9.71   │ 2.86%│")
        print("│  3   │ 中国移动 │ 600941.SH │ 112.56 │ 0.01%│")
        print("└──────┴──────────┴───────────┴────────┴──────┘")
    else:
        print("查询失败")


if __name__ == "__main__":
    # 测试输出格式
    test_output_format()
    
    # 对比新旧格式
    compare_formats()
    
    # 测试Markdown渲染
    test_markdown_rendering()