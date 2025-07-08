#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理缓存并运行综合测试
"""

import os
import shutil
import subprocess
import sys

def clean_cache():
    """清理Python缓存"""
    print("正在清理Python缓存...")
    
    # 清理__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"删除: {cache_path}")
                except Exception as e:
                    print(f"无法删除 {cache_path}: {e}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_path = os.path.join(root, file_name)
                try:
                    os.remove(pyc_path)
                    print(f"删除: {pyc_path}")
                except Exception as e:
                    print(f"无法删除 {pyc_path}: {e}")
    
    # 清理pytest缓存
    if os.path.exists('.pytest_cache'):
        try:
            shutil.rmtree('.pytest_cache')
            print("删除: .pytest_cache")
        except Exception as e:
            print(f"无法删除 .pytest_cache: {e}")
    
    print("缓存清理完成！\n")

def run_test():
    """运行综合测试"""
    print("正在运行SQL Agent综合测试...")
    print("="*80)
    
    # 激活虚拟环境并运行测试
    if sys.platform == 'win32':
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    cmd = f"{activate_cmd}python test_sql_agent_comprehensive.py"
    
    # 使用subprocess运行命令
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 实时输出
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # 获取返回码
    rc = process.poll()
    
    # 输出错误信息（如果有）
    stderr = process.stderr.read()
    if stderr:
        print("\n错误输出:")
        print(stderr)
    
    return rc

def main():
    """主函数"""
    print("SQL Agent 修复后测试验证")
    print("="*80)
    
    # 1. 清理缓存
    clean_cache()
    
    # 2. 运行测试
    return_code = run_test()
    
    if return_code == 0:
        print("\n✅ 测试运行成功完成！")
    else:
        print(f"\n❌ 测试运行失败，返回码: {return_code}")
    
    print("\n请查看生成的测试报告文件 test_report_*.json 了解详细结果。")

if __name__ == "__main__":
    main()