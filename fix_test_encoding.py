#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复测试脚本的编码问题
将Unicode字符替换为ASCII字符
"""

import os
import glob

def fix_file_encoding(file_path):
    """修复单个文件的编码问题"""
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换Unicode字符
        replacements = {
            '✅': '[PASS]',
            '❌': '[FAIL]',
            '⚠️': '[WARN]',
            '✓': '[OK]',
            '✗': '[X]',
            '→': '->',
            '▶': '>',
            '●': '*',
            '═': '=',
            '─': '-',
            '│': '|',
            '├': '+',
            '└': '+',
            '》': '>',
            '《': '<',
            '【': '[',
            '】': ']',
            '（': '(',
            '）': ')',
            '：': ':',
            '，': ',',
            '。': '.',
            '！': '!',
            '？': '?',
        }
        
        # 检查是否需要修改
        needs_fix = False
        for char in replacements:
            if char in content:
                needs_fix = True
                content = content.replace(char, replacements[char])
        
        if needs_fix:
            # 创建备份
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 修复了: {file_path}")
            return True
        else:
            print(f"- 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ 处理失败 {file_path}: {str(e)}")
        return False

def main():
    """修复所有测试脚本的编码问题"""
    print("开始修复测试脚本编码问题...")
    print("="*60)
    
    # 需要修复的测试脚本
    test_scripts = [
        'test_sql_agent_comprehensive.py',
        'test_money_flow_agent_comprehensive_final.py',
        'test_financial_agent_comprehensive_windows.py',
        'test_rag_agent_comprehensive.py',
        'test_hybrid_agent_comprehensive.py'
    ]
    
    fixed_count = 0
    for script in test_scripts:
        if os.path.exists(script):
            if fix_file_encoding(script):
                fixed_count += 1
        else:
            print(f"✗ 文件不存在: {script}")
    
    print("="*60)
    print(f"修复完成! 共修复了 {fixed_count} 个文件")
    print("\n注意：")
    print("1. 原文件已备份为 .backup 文件")
    print("2. 请重新运行测试脚本")

if __name__ == "__main__":
    main()