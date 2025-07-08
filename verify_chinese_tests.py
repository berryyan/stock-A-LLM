#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证中文测试文件是否正常工作
"""
import subprocess
import sys
import os

def verify_test_file(test_file):
    """验证单个测试文件"""
    print(f"\n{'='*60}")
    print(f"验证文件: {test_file}")
    print('-'*60)
    
    if not os.path.exists(test_file):
        print(f"❌ 文件不存在: {test_file}")
        return False
    
    try:
        # 尝试导入文件检查语法
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含中文字符
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
        has_emoji = any(char in '✅❌⚠️🎉' for char in content)
        
        print(f"包含中文: {'✅ 是' if has_chinese else '❌ 否'}")
        print(f"包含emoji: {'✅ 是' if has_emoji else '❌ 否'}")
        
        # 尝试编译文件
        compile(content, test_file, 'exec')
        print("✅ 语法检查通过")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主函数"""
    print("中文测试文件验证工具")
    print("="*60)
    
    # 测试文件列表
    test_files = [
        'test_sql_agent_comprehensive.py',
        'test_rag_agent_comprehensive.py',
        'test_financial_agent_comprehensive.py',
        'test_money_flow_agent_comprehensive.py',
        'test_hybrid_agent_comprehensive.py',
        'test_all_agents_comprehensive.py'
    ]
    
    results = []
    for test_file in test_files:
        success = verify_test_file(test_file)
        results.append((test_file, success))
    
    # 打印总结
    print(f"\n{'='*60}")
    print("验证总结")
    print('-'*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for file, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{file:<40} {status}")
    
    print('-'*60)
    print(f"总计: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有文件验证通过！可以开始测试了。")
        print("\n建议的测试步骤：")
        print("1. 先运行单个Agent测试：")
        print("   python test_sql_agent_comprehensive.py")
        print("\n2. 如果成功，再运行全部测试：")
        print("   python test_all_agents_comprehensive.py")
    else:
        print(f"\n⚠️ 有 {total-passed} 个文件验证失败，请检查。")

if __name__ == "__main__":
    main()