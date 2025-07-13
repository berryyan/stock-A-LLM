#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原始测试结果
"""

import os

def check_file_size_and_content(file_path, agent_name):
    """检查文件大小和部分内容"""
    if not os.path.exists(file_path):
        print(f"{agent_name}: 文件不存在")
        return
    
    # 获取文件大小
    size = os.path.getsize(file_path)
    size_kb = size / 1024
    
    print(f"\n{agent_name}:")
    print(f"  文件大小: {size_kb:.1f} KB")
    
    if size < 100:  # 文件太小，可能是错误
        print("  状态: 文件过小，可能执行失败")
        # 尝试读取全部内容
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # 尝试解码
                for encoding in ['utf-8', 'gbk', 'latin-1']:
                    try:
                        text = content.decode(encoding)
                        print(f"  内容预览: {text[:200]}")
                        break
                    except:
                        continue
        except:
            pass
    else:
        print("  状态: 文件正常大小")
        # 读取文件开头和结尾
        try:
            with open(file_path, 'rb') as f:
                # 读取开头
                start = f.read(500)
                # 读取结尾
                f.seek(-500, 2)
                end = f.read(500)
                
                # 尝试解码
                for encoding in ['utf-8', 'gbk', 'latin-1']:
                    try:
                        start_text = start.decode(encoding, errors='ignore')
                        end_text = end.decode(encoding, errors='ignore')
                        
                        # 查找关键信息
                        if '测试' in end_text or 'test' in end_text.lower():
                            print(f"  开头: {start_text[:100]}...")
                            print(f"  结尾: ...{end_text[-200:]}")
                        break
                    except:
                        continue
        except Exception as e:
            print(f"  读取错误: {str(e)}")

def main():
    print("="*60)
    print("原始测试结果检查")
    print("="*60)
    
    test_files = {
        'SQL Agent': 'test_results/sql_agent_regression_20250712.txt',
        'Money Flow Agent': 'test_results/money_flow_regression_20250712.txt',
        'Financial Agent': 'test_results/financial_regression_20250712.txt',
        'RAG Agent': 'test_results/rag_agent_regression_20250712.txt',
        'Hybrid Agent': 'test_results/hybrid_agent_regression_20250712.txt'
    }
    
    for agent_name, file_path in test_files.items():
        check_file_size_and_content(file_path, agent_name)

if __name__ == "__main__":
    main()