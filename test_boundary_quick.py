#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试边界问题"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.parameter_extractor import ParameterExtractor

def quick_test():
    """快速测试参数提取"""
    extractor = ParameterExtractor()
    
    test_cases = [
        ("万科A季度财务对比分析", "万科A的季度财务对比分析"),
        ("贵州茅台净资产收益率分析", "贵州茅台的净资产收益率分析"),
        ("贵州茅台运营能力评价", "贵州茅台的运营能力评价"),
    ]
    
    print("参数提取边界测试")
    print("="*60)
    
    for original, fixed in test_cases:
        print(f"\n原始: {original}")
        params1 = extractor.extract_all_params(original)
        print(f"  提取股票: {params1.stocks}")
        print(f"  错误: {params1.error}")
        
        print(f"\n修改: {fixed}")
        params2 = extractor.extract_all_params(fixed)
        print(f"  提取股票: {params2.stocks}")
        print(f"  错误: {params2.error}")
        
        if not params1.stocks and params2.stocks:
            print("  ✅ 加'的'修复成功！")
        elif params1.stocks and params2.stocks:
            print("  ⚠️ 两个都成功")
        else:
            print("  ❌ 加'的'没有修复")

if __name__ == "__main__":
    quick_test()