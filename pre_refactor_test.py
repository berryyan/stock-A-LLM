#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构前的完整测试 - 确保当前系统正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import traceback
from datetime import datetime


def test_current_system():
    """测试当前系统的基本功能"""
    print("="*80)
    print("重构前系统测试")
    print(f"时间: {datetime.now()}")
    print("="*80)
    
    results = {
        "hybrid_agent": False,
        "sql_queries": [],
        "errors": []
    }
    
    try:
        # 1. 测试HybridAgent能否正常初始化
        print("\n1. 测试HybridAgent初始化...")
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        print("✅ HybridAgent初始化成功")
        results["hybrid_agent"] = True
        
        # 2. 测试基本查询
        test_queries = [
            ("贵州茅台的最新股价", "sql"),
            ("市值排名前3", "sql"),
            ("贵州茅台最新的公告", "rag")
        ]
        
        print("\n2. 测试基本查询功能...")
        for query, expected_type in test_queries:
            print(f"\n查询: {query}")
            try:
                result = agent.query(query)
                success = result.get('success', False)
                query_type = result.get('query_type', 'unknown')
                
                print(f"  成功: {success}")
                print(f"  类型: {query_type} (期望: {expected_type})")
                
                results["sql_queries"].append({
                    "query": query,
                    "success": success,
                    "type": query_type,
                    "expected_type": expected_type
                })
                
                if not success:
                    print(f"  错误: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {str(e)}")
                results["errors"].append({
                    "query": query,
                    "error": str(e)
                })
                
    except Exception as e:
        print(f"\n❌ 系统测试失败: {str(e)}")
        traceback.print_exc()
        results["errors"].append({
            "component": "system",
            "error": str(e)
        })
    
    # 3. 保存测试结果
    print("\n3. 保存测试结果...")
    with open("pre_refactor_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ 测试结果已保存到 pre_refactor_test_results.json")
    
    # 4. 测试总结
    print("\n" + "="*80)
    print("测试总结:")
    print(f"- HybridAgent初始化: {'✅ 成功' if results['hybrid_agent'] else '❌ 失败'}")
    print(f"- 查询测试: {len([q for q in results['sql_queries'] if q['success']])}/{len(test_queries)} 成功")
    print(f"- 错误数量: {len(results['errors'])}")
    
    if results['errors']:
        print("\n错误列表:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return len(results['errors']) == 0


def check_git_status():
    """检查Git状态"""
    print("\n" + "="*80)
    print("Git状态检查")
    print("="*80)
    
    import subprocess
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.stdout:
            print("⚠️ 警告：有未提交的更改")
            print("建议先提交当前更改，以便需要时可以回滚")
            print("\n未提交的文件:")
            print(result.stdout)
        else:
            print("✅ 工作目录干净，没有未提交的更改")
            
        # 显示最近的提交
        result = subprocess.run(["git", "log", "--oneline", "-5"], 
                              capture_output=True, text=True)
        print("\n最近的提交:")
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ 无法检查Git状态: {e}")


def main():
    """主函数"""
    print("重构前检查清单")
    print("="*80)
    
    # 1. 检查Git状态
    check_git_status()
    
    # 2. 测试当前系统
    print("\n准备测试当前系统...")
    input("按Enter继续，或Ctrl+C取消...")
    
    success = test_current_system()
    
    if success:
        print("\n✅ 当前系统测试通过，可以进行重构")
        print("\n建议:")
        print("1. 先提交当前所有更改")
        print("2. 运行 refactor_agents.py 进行重构")
        print("3. 重构后立即运行 post_refactor_test.py 验证")
    else:
        print("\n❌ 当前系统有问题，不建议进行重构")
        print("请先修复现有问题")


if __name__ == "__main__":
    main()