#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent综合测试启动器
自动检测环境并运行测试
"""

import os
import sys
import platform
import subprocess
from datetime import datetime


def check_environment():
    """检查运行环境"""
    print("="*60)
    print("环境检查")
    print("="*60)
    
    # 系统信息
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查必要的包
    required_packages = [
        'langchain',
        'langchain_openai',
        'fastapi',
        'pymysql',
        'pandas',
        'numpy'
    ]
    
    print("\n依赖包检查:")
    missing_packages = []
    for package in required_packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {package}: {version}")
        except ImportError:
            print(f"  ✗ {package}: 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n警告: 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请先安装缺失的包: pip install " + ' '.join(missing_packages))
        return False
    
    # 检查数据库配置
    print("\n配置文件检查:")
    if os.path.exists('.env'):
        print("  ✓ .env 文件存在")
    else:
        print("  ✗ .env 文件不存在")
        print("  请确保配置文件包含数据库连接信息")
        return False
    
    return True


def run_tests():
    """运行测试"""
    print("\n" + "="*60)
    print("开始运行Concept Agent综合测试")
    print("="*60)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("预计运行时间: 5-10分钟")
    print("-"*60)
    
    # 运行测试脚本
    try:
        # 使用当前Python解释器运行测试
        result = subprocess.run(
            [sys.executable, 'test_concept_agent_comprehensive_windows.py'],
            check=False,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("\n✅ 测试成功完成！")
        else:
            print(f"\n⚠️ 测试完成，但有错误 (返回码: {result.returncode})")
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 运行测试时出错: {e}")
        return False
    
    return True


def show_results():
    """显示测试结果"""
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    
    # 查找最新的日志文件
    log_files = [f for f in os.listdir('.') if f.startswith('concept_agent_test_') and f.endswith('.log')]
    if log_files:
        latest_log = max(log_files, key=os.path.getctime)
        print(f"日志文件: {latest_log}")
        
        # 显示日志的最后几行
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                summary_start = -1
                for i, line in enumerate(lines):
                    if 'Concept Agent综合测试报告' in line:
                        summary_start = i
                        break
                
                if summary_start >= 0:
                    print("\n测试摘要:")
                    print("-"*60)
                    for line in lines[summary_start:]:
                        print(line.rstrip())
        except Exception as e:
            print(f"读取日志文件失败: {e}")
    
    # 查找测试报告
    report_files = [f for f in os.listdir('.') if f.startswith('concept_agent_test_report_') and f.endswith('.json')]
    if report_files:
        latest_report = max(report_files, key=os.path.getctime)
        print(f"\n详细报告: {latest_report}")
        print("可以使用文本编辑器或浏览器查看JSON报告")


def main():
    """主函数"""
    print("Concept Agent 综合测试启动器")
    print("="*80)
    
    # 1. 检查环境
    if not check_environment():
        print("\n环境检查未通过，请修复问题后重试")
        input("\n按Enter键退出...")
        return
    
    # 2. 运行测试
    print("\n环境检查通过，准备运行测试...")
    input("按Enter键开始测试，或按Ctrl+C取消...")
    
    if run_tests():
        # 3. 显示结果
        show_results()
    
    input("\n按Enter键退出...")


if __name__ == "__main__":
    main()