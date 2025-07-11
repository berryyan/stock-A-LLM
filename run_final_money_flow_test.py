#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行Money Flow Agent最终测试"""

import subprocess
import sys

def run_test():
    """运行测试脚本"""
    print("运行Money Flow Agent综合测试...")
    print("="*80)
    
    # 运行测试脚本
    result = subprocess.run(
        [sys.executable, "test_money_flow_agent_comprehensive_final.py"],
        capture_output=True,
        text=True
    )
    
    # 打印输出
    print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_test()
    print(f"\n测试完成，退出码: {exit_code}")