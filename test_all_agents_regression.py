#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面回归测试脚本
测试所有Agent确保修改后仍然保持高通过率
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import subprocess
import time
import json
from datetime import datetime


def run_test_script(script_name, timeout=600):
    """运行测试脚本并返回结果"""
    print(f"\n{'='*80}")
    print(f"运行测试: {script_name}")
    print(f"{'='*80}")
    
    try:
        # 在虚拟环境中运行测试脚本
        cmd = f"source venv/bin/activate && timeout {timeout} python {script_name}"
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            executable='/bin/bash'
        )
        
        # 检查是否成功
        if result.returncode == 0:
            print("✅ 测试脚本执行成功")
            return True, "成功"
        else:
            print("❌ 测试脚本执行失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False, str(e)


def run_quick_tests():
    """运行快速测试以验证基本功能"""
    print("=" * 100)
    print("股票分析系统 v2.3.0 发布前回归测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    
    # 定义要测试的脚本
    test_scripts = [
        {
            "name": "SQL Agent快速测试",
            "script": "test_sql_agent_quick.py",
            "timeout": 120,
            "critical": True
        },
        {
            "name": "Money Flow Agent快速测试",
            "script": "test_money_flow_quick.py",
            "timeout": 120,
            "critical": True
        },
        {
            "name": "Financial Agent快速测试",
            "script": "test_financial_agent_quick.py",
            "timeout": 180,
            "critical": True
        },
        {
            "name": "Hybrid Agent快速验证",
            "script": "test_hybrid_agent_quick_verify.py",
            "timeout": 300,
            "critical": True
        },
        {
            "name": "RAG Agent快速测试",
            "script": "test_rag_agent_quick.py",
            "timeout": 180,
            "critical": False
        }
    ]
    
    results = {
        "total": len(test_scripts),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for test in test_scripts:
        start_time = time.time()
        
        # 检查脚本是否存在
        if not os.path.exists(test["script"]):
            print(f"\n⚠️ 测试脚本不存在: {test['script']}")
            # 创建快速测试脚本
            create_quick_test_script(test["script"])
        
        success, error = run_test_script(test["script"], test["timeout"])
        elapsed = time.time() - start_time
        
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
            if test["critical"]:
                print(f"\n⚠️ 关键测试失败！{test['name']}")
        
        results["details"].append({
            "name": test["name"],
            "script": test["script"],
            "success": success,
            "elapsed": elapsed,
            "error": error if not success else None,
            "critical": test["critical"]
        })
        
        print(f"耗时: {elapsed:.2f}秒")
    
    # 打印总结
    print(f"\n{'='*100}")
    print("回归测试总结")
    print(f"{'='*100}")
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']}")
    print(f"失败: {results['failed']}")
    print(f"通过率: {results['passed']/results['total']*100:.1f}%")
    
    # 检查关键测试
    critical_failures = [d for d in results["details"] if d["critical"] and not d["success"]]
    if critical_failures:
        print("\n❌ 关键测试失败:")
        for failure in critical_failures:
            print(f"  - {failure['name']}")
        print("\n⚠️ 不建议发布！")
    else:
        print("\n✅ 所有关键测试通过！")
        print("🎉 可以发布v2.3.0！")
    
    # 保存结果
    with open('regression_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: regression_test_results.json")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results["failed"] == 0


def create_quick_test_script(script_name):
    """创建快速测试脚本"""
    agent_name = script_name.split('_')[1]  # 提取agent名称
    
    template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{agent_name.title()} Agent 快速测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.{agent_name}_agent_modular import {agent_name.title()}AgentModular

def quick_test():
    """运行快速测试"""
    print(f"\\n{agent_name.title()} Agent 快速测试")
    print("=" * 50)
    
    agent = {agent_name.title()}AgentModular()
    
    # 基本测试用例
    test_cases = [
        "贵州茅台的股价",
        "万科A的主要业务",
        "比亚迪的财务状况"
    ]
    
    passed = 0
    for query in test_cases:
        print(f"\\n测试: {{query}}")
        try:
            result = agent.query(query)
            if result.get('success'):
                print("✅ 通过")
                passed += 1
            else:
                print(f"❌ 失败: {{result.get('error')}}")
        except Exception as e:
            print(f"❌ 异常: {{str(e)}}")
    
    print(f"\\n通过率: {{passed}}/{{len(test_cases)}}")
    return passed == len(test_cases)

if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)
'''
    
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"创建快速测试脚本: {script_name}")


if __name__ == "__main__":
    success = run_quick_tests()
    exit(0 if success else 1)