#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终的市值排名功能测试
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import time

def test_final_functionality():
    """测试最终的功能实现"""
    
    print("市值排名功能最终测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 完整的测试用例
    test_cases = [
        # 1. 无数字查询（默认前10）
        ("总市值排名", "默认前10"),
        ("市值排名", "默认前10（省略总）"),
        ("流通市值排名", "默认前10"),
        
        # 2. TOP格式
        ("市值TOP5", "TOP5"),
        ("总市值TOP20", "TOP20"),
        ("流通市值TOP15", "流通市值TOP15"),
        
        # 3. 时间+无数字
        ("今天的市值排名", "今天+默认前10"),
        ("最新市值排名", "最新+默认前10"),
        ("昨天流通市值排名", "昨天+流通市值"),
        
        # 4. 指定日期+无数字
        ("2025-07-01市值排名", "指定日期+默认前10"),
        ("2025年7月1日总市值排名", "中文日期+默认前10"),
        
        # 5. 传统格式（验证兼容性）
        ("总市值最大的前10只股票", "传统格式"),
        ("市值前20", "前N格式"),
        ("流通市值前5名", "前N名格式"),
    ]
    
    for query, desc in test_cases:
        print(f"\n{'='*80}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            result = sql_agent.query(query)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            if result['success']:
                print(f"✅ 查询成功 (耗时: {elapsed_time:.2f}秒)")
                
                # 分析结果
                result_text = str(result.get('result', ''))
                
                # 统计返回的记录数
                lines = result_text.split('\n')
                data_lines = []
                in_data_section = False
                
                for line in lines:
                    if '----' in line:
                        in_data_section = True
                        continue
                    if in_data_section and line.strip() and '|' in line:
                        data_lines.append(line)
                
                print(f"返回记录数: {len(data_lines)}")
                
                # 提取日期信息
                import re
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', result_text)
                if dates:
                    print(f"数据日期: {dates[0]}")
                
                # 检查是否使用了快速路由
                if result.get('quick_path'):
                    print("使用了快速路由 ⚡")
                    
                # 显示前3条记录
                if data_lines:
                    print("\n数据预览:")
                    for i, line in enumerate(data_lines[:3]):
                        print(f"  {line.strip()}")
                        
            else:
                print(f"❌ 查询失败")
                print(f"错误信息: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*100)
    print("测试完成！")


def test_edge_cases():
    """测试边界情况"""
    
    print("\n\n边界情况测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    edge_cases = [
        ("市值排行榜", "排行榜"),
        ("A股总市值TOP10", "A股前缀+TOP"),
        ("中国市值排名前5", "中国前缀+前N"),
        ("全市场市值排名", "全市场"),
        ("深市市值排名", "深市"),
    ]
    
    for query, desc in edge_cases:
        print(f"\n测试: {desc} - '{query}'")
        
        try:
            # 只测试快速路由
            result = sql_agent._try_quick_query(query)
            if result:
                print("✅ 快速路由匹配成功")
            else:
                print("❌ 未匹配快速路由（将使用普通模板）")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    # 运行完整功能测试
    test_final_functionality()
    
    # 运行边界情况测试
    test_edge_cases()