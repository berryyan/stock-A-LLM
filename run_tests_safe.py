#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全运行测试脚本（避免编码问题）
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test(script_name, output_file):
    """运行单个测试脚本"""
    print(f"\n{'='*60}")
    print(f"运行测试: {script_name}")
    print(f"输出文件: {output_file}")
    print(f"{'='*60}")
    
    try:
        # 设置环境变量，强制使用UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 运行测试脚本
        with open(output_file, 'w', encoding='utf-8') as f:
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 等待完成
            process.wait()
            
        print(f"[完成] 返回代码: {process.returncode}")
        
        # 尝试提取结果摘要
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # 查找最后的测试结果
                for line in reversed(lines[-50:]):
                    if '通过率' in line or 'pass_rate' in line or '%' in line:
                        print(f"[结果] {line.strip()}")
                        break
        except:
            pass
            
    except Exception as e:
        print(f"[错误] 运行失败: {str(e)}")

def main():
    print("="*60)
    print("v2.3.0 回归测试 - 安全模式")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 创建输出目录
    os.makedirs('test_results', exist_ok=True)
    
    # 测试列表
    tests = [
        ('test_sql_agent_comprehensive.py', 'test_results/sql_agent_safe.txt'),
        ('test_money_flow_agent_comprehensive_final.py', 'test_results/money_flow_safe.txt'),
        ('test_financial_agent_comprehensive_windows.py', 'test_results/financial_safe.txt'),
        ('test_rag_agent_comprehensive.py', 'test_results/rag_safe.txt'),
        ('test_hybrid_agent_comprehensive.py', 'test_results/hybrid_safe.txt'),
    ]
    
    # 运行所有测试
    for script, output in tests:
        if os.path.exists(script):
            run_test(script, output)
        else:
            print(f"\n[跳过] 文件不存在: {script}")
    
    print("\n"+"="*60)
    print("所有测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()