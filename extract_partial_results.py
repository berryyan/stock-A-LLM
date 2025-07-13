#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从部分完成的测试结果中提取信息
"""

import os
import re

def extract_info(file_path, agent_name):
    """从测试文件中提取已完成的测试信息"""
    if not os.path.exists(file_path):
        print(f"\n{agent_name}: 文件不存在")
        return
        
    print(f"\n{agent_name}:")
    print("-" * 40)
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 尝试解码
    text = content.decode('utf-8', errors='ignore')
    
    # 统计测试执行情况
    test_count = text.count('测试') + text.count('Test')
    pass_count = text.count('[PASS]') + text.count('通过') + text.count('成功')
    fail_count = text.count('[FAIL]') + text.count('失败') + text.count('错误')
    
    # 查找测试类别
    categories = re.findall(r'测试类别[:：]\s*([^\n]+)', text)
    unique_categories = list(set(categories))
    
    print(f"文件大小: {len(content)/1024:.1f} KB")
    print(f"发现测试: ~{test_count} 个")
    print(f"成功标记: ~{pass_count} 个")
    print(f"失败标记: ~{fail_count} 个")
    
    if unique_categories:
        print(f"测试类别: {', '.join(unique_categories[:5])}")
    
    # 查找错误信息
    if 'UnicodeEncodeError' in text:
        print("状态: 因编码错误中断")
        # 找出中断前最后执行的测试
        lines = text.split('\n')
        for i in range(len(lines)-1, max(0, len(lines)-20), -1):
            if '查询:' in lines[i] or 'Query:' in lines[i]:
                print(f"最后查询: {lines[i].strip()}")
                break

def main():
    print("="*60)
    print("部分测试结果分析")
    print("="*60)
    
    test_files = {
        'SQL Agent': 'test_results/sql_agent_regression_20250712.txt',
        'Money Flow Agent': 'test_results/money_flow_regression_20250712.txt',
        'Financial Agent': 'test_results/financial_regression_20250712.txt',
        'RAG Agent': 'test_results/rag_agent_regression_20250712.txt',
        'Hybrid Agent': 'test_results/hybrid_agent_regression_20250712.txt'
    }
    
    for agent_name, file_path in test_files.items():
        extract_info(file_path, agent_name)
    
    print("\n" + "="*60)
    print("建议：使用 run_tests_safe.py 重新运行测试")

if __name__ == "__main__":
    main()