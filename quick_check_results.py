#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查测试结果
"""

import os
import re

def check_test_file(file_path, agent_name):
    """检查单个测试文件"""
    if not os.path.exists(file_path):
        print(f"❌ {agent_name}: 文件不存在")
        return
    
    # 尝试多种编码读取文件末尾
    encodings = ['gbk', 'utf-8', 'gb2312', 'cp936', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                # 只看最后100行
                last_lines = ''.join(lines[-100:])
                
                # 查找测试结果
                if '通过率' in last_lines or 'pass_rate' in last_lines:
                    # 提取通过率
                    rate_match = re.search(r'(\d+\.?\d*)[%％]', last_lines)
                    if rate_match:
                        rate = float(rate_match.group(1))
                        if rate >= 90:
                            print(f"✅ {agent_name}: {rate}% 通过")
                        elif rate >= 70:
                            print(f"⚠️  {agent_name}: {rate}% 通过")
                        else:
                            print(f"❌ {agent_name}: {rate}% 通过")
                    else:
                        print(f"? {agent_name}: 无法提取通过率")
                    
                    # 尝试提取总数和通过数
                    total_match = re.search(r'总测试[数量]*[:：]\s*(\d+)', last_lines)
                    passed_match = re.search(r'通过[:：]\s*(\d+)', last_lines)
                    if total_match and passed_match:
                        total = int(total_match.group(1))
                        passed = int(passed_match.group(1))
                        print(f"   详情: {passed}/{total} 测试通过")
                    
                    break
                else:
                    # 检查是否有错误
                    if 'Error' in last_lines or 'error' in last_lines or '错误' in last_lines:
                        print(f"❌ {agent_name}: 测试执行出错")
                        break
                    elif encoding == encodings[-1]:
                        print(f"? {agent_name}: 无法找到测试结果")
                        
        except Exception as e:
            if encoding == encodings[-1]:
                print(f"❌ {agent_name}: 无法读取文件 - {str(e)}")

def main():
    print("="*60)
    print("v2.3.0 回归测试快速检查")
    print("="*60)
    print()
    
    test_files = {
        'SQL Agent': 'test_results/sql_agent_regression_20250712.txt',
        'Money Flow Agent': 'test_results/money_flow_regression_20250712.txt',
        'Financial Agent': 'test_results/financial_regression_20250712.txt',
        'RAG Agent': 'test_results/rag_agent_regression_20250712.txt',
        'Hybrid Agent': 'test_results/hybrid_agent_regression_20250712.txt'
    }
    
    for agent_name, file_path in test_files.items():
        check_test_file(file_path, agent_name)
    
    print()
    print("="*60)
    print("提示：如需查看详细结果，请打开对应的txt文件")

if __name__ == "__main__":
    main()