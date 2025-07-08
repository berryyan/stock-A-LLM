#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复SQL Agent综合测试中的错误预期
基于深度分析结果
"""

import re

def fix_test_expectations():
    """修复测试预期"""
    
    # 读取测试文件
    with open('test_sql_agent_comprehensive.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1：成交量排名应该成功
    content = re.sub(
        r'self\.test_query\("成交量排名", expected_success=False',
        'self.test_query("成交量排名", expected_success=True',
        content
    )
    
    # 修复2：成交额排行应该成功
    content = re.sub(
        r'self\.test_query\("成交额排行", expected_success=False',
        'self.test_query("成交额排行", expected_success=True',
        content
    )
    
    # 修复3：贵州茅台的成交量应该成功
    content = re.sub(
        r'self\.test_query\("贵州茅台的成交量", expected_success=False',
        'self.test_query("贵州茅台的成交量", expected_success=True',
        content
    )
    
    # 修复4：平安银行成交量应该成功
    content = re.sub(
        r'self\.test_query\("平安银行成交量", expected_success=False',
        'self.test_query("平安银行成交量", expected_success=True',
        content
    )
    
    # 写回文件
    with open('test_sql_agent_comprehensive.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("测试预期修复完成！")
    print("修复了以下测试用例的预期：")
    print("1. 成交量排名 - 改为期望成功")
    print("2. 成交额排行 - 改为期望成功")
    print("3. 贵州茅台的成交量 - 改为期望成功")
    print("4. 平安银行成交量 - 改为期望成功")

if __name__ == "__main__":
    fix_test_expectations()