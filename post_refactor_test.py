#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构后的验证测试 - 确保重构没有破坏系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import traceback
from datetime import datetime


def compare_with_baseline():
    """与重构前的测试结果对比"""
    print("\n与重构前对比...")
    
    try:
        with open("pre_refactor_test_results.json", "r", encoding="utf-8") as f:
            baseline = json.load(f)
        
        print("✅ 找到基准测试结果")
        return baseline
    except:
        print("⚠️ 没有找到基准测试结果")
        return None


def test_refactored_system():
    """测试重构后的系统"""
    print("="*80)
    print("重构后系统测试")
    print(f"时间: {datetime.now()}")
    print("="*80)
    
    results = {
        "hybrid_agent": False,
        "sql_queries": [],
        "errors": [],
        "agent_types": {}
    }
    
    try:
        # 1. 测试HybridAgent
        print("\n1. 测试HybridAgent初始化...")
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        print("✅ HybridAgent初始化成功")
        results["hybrid_agent"] = True
        
        # 检查使用的Agent类型
        print("\n检查Agent类型:")
        print(f"  SQL Agent: {type(agent.sql_agent).__name__}")
        print(f"  RAG Agent: {type(agent.rag_agent).__name__}")
        print(f"  Financial Agent: {type(agent.financial_agent).__name__}")
        print(f"  Money Flow Agent: {type(agent.money_flow_agent).__name__}")
        
        results["agent_types"] = {
            "sql": type(agent.sql_agent).__name__,
            "rag": type(agent.rag_agent).__name__,
            "financial": type(agent.financial_agent).__name__,
            "money_flow": type(agent.money_flow_agent).__name__
        }
        
        # 2. 测试相同的查询
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
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                
    except Exception as e:
        print(f"\n❌ 系统测试失败: {str(e)}")
        traceback.print_exc()
        results["errors"].append({
            "component": "system",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    # 3. 保存测试结果
    print("\n3. 保存测试结果...")
    with open("post_refactor_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ 测试结果已保存到 post_refactor_test_results.json")
    
    # 4. 与基准对比
    baseline = compare_with_baseline()
    
    # 5. 测试总结
    print("\n" + "="*80)
    print("测试总结:")
    print(f"- HybridAgent初始化: {'✅ 成功' if results['hybrid_agent'] else '❌ 失败'}")
    print(f"- 查询测试: {len([q for q in results['sql_queries'] if q['success']])}/{len(test_queries)} 成功")
    print(f"- 错误数量: {len(results['errors'])}")
    
    if baseline:
        print("\n与重构前对比:")
        baseline_success = len([q for q in baseline.get('sql_queries', []) if q['success']])
        current_success = len([q for q in results['sql_queries'] if q['success']])
        
        if current_success >= baseline_success:
            print(f"✅ 功能正常 (重构前: {baseline_success}, 重构后: {current_success})")
        else:
            print(f"❌ 功能退化 (重构前: {baseline_success}, 重构后: {current_success})")
    
    if results['errors']:
        print("\n❌ 错误列表:")
        for error in results['errors']:
            print(f"\n错误: {error.get('query', error.get('component', 'unknown'))}")
            print(f"信息: {error.get('error')}")
            if 'traceback' in error:
                print("调用栈:")
                print(error['traceback'])
    
    return len(results['errors']) == 0


def verify_file_structure():
    """验证文件结构"""
    print("\n验证文件结构...")
    
    expected_files = [
        "agents/sql_agent.py",
        "agents/sql_agent_modular.py",  # 应该是重命名后的v2
        "agents/rag_agent.py",
        "agents/rag_agent_modular.py",
        "agents/financial_agent.py",
        "agents/financial_agent_modular.py",
        "agents/money_flow_agent.py",
        "agents/money_flow_agent_modular.py",
    ]
    
    missing_files = []
    for filepath in expected_files:
        if not os.path.exists(filepath):
            missing_files.append(filepath)
            print(f"❌ 缺失: {filepath}")
        else:
            print(f"✅ 存在: {filepath}")
    
    # 检查不应该存在的文件
    should_not_exist = [
        "agents/sql_agent_v2.py",  # 应该被重命名了
    ]
    
    for filepath in should_not_exist:
        if os.path.exists(filepath):
            print(f"⚠️ 不应存在: {filepath}")
    
    return len(missing_files) == 0


def main():
    """主函数"""
    print("重构后验证测试")
    print("="*80)
    
    # 1. 验证文件结构
    print("\n1. 验证文件结构")
    structure_ok = verify_file_structure()
    
    if not structure_ok:
        print("\n❌ 文件结构有问题，请检查重构是否正确完成")
        return
    
    # 2. 测试系统功能
    print("\n2. 测试系统功能")
    success = test_refactored_system()
    
    if success:
        print("\n✅ 重构验证通过！")
        print("\n下一步:")
        print("1. 检查所有测试是否通过")
        print("2. 提交代码变更")
        print("3. 更新文档说明新的架构")
    else:
        print("\n❌ 重构验证失败！")
        print("\n建议:")
        print("1. 检查错误日志")
        print("2. 如果问题严重，考虑回滚: git checkout -- .")
        print("3. 或者逐个修复问题")


if __name__ == "__main__":
    main()