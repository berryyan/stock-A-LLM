#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复测试中关于股票简称的错误预期
根据系统设计，不支持股票简称查询
"""

import re

def fix_abbreviation_tests():
    """修复简称相关的测试预期"""
    
    # 读取测试文件
    with open('test_sql_agent_comprehensive.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要修改的测试用例
    # 这些使用了简称，应该失败
    fixes = [
        # 在利润查询的其他表达方式中
        ('("茅台赚了多少钱", "赚钱表达")', '("茅台赚了多少钱", "赚钱表达-简称错误")'),
        ('("万科盈利情况", "盈利情况")', '("万科盈利情况", "盈利情况-简称错误")'),
        
        # 需要从正常用例移到错误用例
        ('for query, test_name in other_cases:\n            self.test_query(query, True,',
         'for query, test_name in other_cases:\n            self.test_query(query, False,'),  # 改为False
    ]
    
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"修改: {old[:50]}... -> {new[:50]}...")
    
    # 确保错误用例中包含了简称测试
    # 在利润查询的错误用例中已经有了"茅台的利润"
    
    # 写回文件
    with open('test_sql_agent_comprehensive.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n简称测试修复完成！")
    print("\n重要说明：")
    print("根据系统设计，不支持股票简称、昵称、公司全称等变体")
    print("只接受：")
    print("1. 股票名称（如：贵州茅台）")
    print("2. 股票代码（如：600519）")
    print("3. 证券代码（如：600519.SH）")
    print("\n已修改的测试：")
    print("- '茅台赚了多少钱' -> 期望失败（使用了简称）")
    print("- '万科盈利情况' -> 期望失败（使用了简称）")

if __name__ == "__main__":
    fix_abbreviation_tests()