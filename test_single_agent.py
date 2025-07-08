#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个Agent测试运行器
用于测试编码修复是否有效
"""
import subprocess
import sys
import os
import json
import time
from datetime import datetime


def run_single_agent_test(agent_name, script_name):
    """运行单个Agent的测试"""
    print(f"\n{'='*60}")
    print(f"测试Agent: {agent_name}")
    print(f"测试脚本: {script_name}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    try:
        # 运行测试脚本，设置较短的超时时间用于测试
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            encoding='utf-8',  # 明确指定UTF-8编码
            errors='replace'   # 替换无法编码的字符
        )
        
        print(f"\n返回码: {result.returncode}")
        print(f"标准输出长度: {len(result.stdout)} 字符")
        print(f"错误输出长度: {len(result.stderr)} 字符")
        
        # 打印最后50行输出
        if result.stdout:
            lines = result.stdout.split('\n')
            print("\n最后50行输出:")
            print("-"*60)
            for line in lines[-50:]:
                print(line)
        
        if result.stderr:
            print("\n错误输出:")
            print("-"*60)
            print(result.stderr[:1000])  # 只打印前1000字符
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("[ERROR] 测试超时（5分钟）")
        return False
    except Exception as e:
        print(f"[ERROR] 执行失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("单个Agent测试运行器")
    print("="*60)
    print("请选择要测试的Agent:")
    print("1. SQL Agent")
    print("2. RAG Agent")
    print("3. Financial Agent")
    print("4. Money Flow Agent")
    print("5. Hybrid Agent")
    
    choice = input("\n请输入选择 (1-5): ")
    
    agents = {
        '1': ('SQL Agent', 'test_sql_agent_comprehensive.py'),
        '2': ('RAG Agent', 'test_rag_agent_comprehensive.py'),
        '3': ('Financial Agent', 'test_financial_agent_comprehensive.py'),
        '4': ('Money Flow Agent', 'test_money_flow_agent_comprehensive.py'),
        '5': ('Hybrid Agent', 'test_hybrid_agent_comprehensive.py')
    }
    
    if choice in agents:
        agent_name, script_name = agents[choice]
        if os.path.exists(script_name):
            success = run_single_agent_test(agent_name, script_name)
            print(f"\n测试{'成功' if success else '失败'}")
        else:
            print(f"\n[ERROR] 测试脚本不存在: {script_name}")
    else:
        print("\n无效的选择")


if __name__ == "__main__":
    main()