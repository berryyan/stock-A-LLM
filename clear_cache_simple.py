#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python脚本清除缓存
"""

import os
import shutil
import sys

def clear_python_cache():
    """清除Python缓存"""
    print("清除Python缓存...")
    print("=" * 50)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 统计
    pycache_count = 0
    pyc_count = 0
    pyo_count = 0
    
    # 遍历所有子目录
    for root, dirs, files in os.walk(current_dir):
        # 删除__pycache__目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                pycache_count += 1
                print(f"删除: {pycache_path}")
            except Exception as e:
                print(f"无法删除 {pycache_path}: {e}")
        
        # 删除.pyc和.pyo文件
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    pyc_count += 1
                except Exception as e:
                    print(f"无法删除 {file_path}: {e}")
            elif file.endswith('.pyo'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    pyo_count += 1
                except Exception as e:
                    print(f"无法删除 {file_path}: {e}")
        
        # 删除.pytest_cache目录
        if '.pytest_cache' in dirs:
            pytest_cache_path = os.path.join(root, '.pytest_cache')
            try:
                shutil.rmtree(pytest_cache_path)
                print(f"删除: {pytest_cache_path}")
            except Exception as e:
                print(f"无法删除 {pytest_cache_path}: {e}")
    
    print("\n" + "=" * 50)
    print(f"清除完成!")
    print(f"- 删除了 {pycache_count} 个 __pycache__ 目录")
    print(f"- 删除了 {pyc_count} 个 .pyc 文件")
    print(f"- 删除了 {pyo_count} 个 .pyo 文件")
    print("\n现在可以运行综合测试了：")
    print("python test_sql_agent_comprehensive.py")

if __name__ == "__main__":
    clear_python_cache()