#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证测试脚本是否能在正确位置运行
"""

import os
import sys
import subprocess

def test_script_in_correct_location(script_name):
    """测试脚本在正确位置是否能运行"""
    print(f"\n测试 {script_name}:")
    print("-" * 50)
    
    # 在根目录下运行脚本
    cmd = f"cd /mnt/e/PycharmProjects/stock_analysis_system && source venv/bin/activate && python {script_name} 2>&1 | head -20"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/mnt/e/PycharmProjects/stock_analysis_system"
        )
        
        if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
            print("❌ 导入错误（可能是环境问题）")
        elif result.returncode == 0:
            print("✅ 运行成功")
            print("输出预览:")
            print(result.stdout[:200] + "...")
        else:
            print("❌ 运行失败")
            if result.stderr:
                print("错误信息:", result.stderr[:200])
                
    except subprocess.TimeoutExpired:
        print("⏱️ 超时（可能正在正常运行）")
    except Exception as e:
        print(f"❌ 异常: {e}")

# 测试几个关键脚本
test_scripts = [
    "baseline_test.py",
    "comprehensive_verification.py", 
    "test_financial_agent.py"
]

print("验证脚本位置问题")
print("=" * 60)
print(f"当前目录: {os.getcwd()}")
print(f"Python路径: {sys.path[0]}")

for script in test_scripts:
    script_path = os.path.join("..", script)
    if os.path.exists(script_path):
        print(f"\n✓ {script} 存在于根目录")
        # 检查脚本的导入语句
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'sys.path.append' in content:
                print("  脚本包含路径调整代码")
            if 'from agents' in content or 'import agents' in content:
                print("  脚本导入agents模块")
    else:
        print(f"\n✗ {script} 不存在")