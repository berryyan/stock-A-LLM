#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试修复效果
测试之前失败的关键用例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

def test_fixes():
    """测试修复效果"""
    agent = SQLAgentModular()
    
    test_cases = [
        # 参数提取问题修复测试
        ("宁德时代从2025/06/01到2025/06/30的K线", "斜杠日期格式", True),
        ("贵州茅台本月的K线", "本月", True),
        ("平安银行上个月的K线", "上个月", True),
        ("比亚迪去年的K线", "去年", True),
        ("中国平安前十天的走势", "中文数字", True),
        
        # 查询验证测试（应该失败）
        ("涨幅前0只股票", "数量为0", False),
        ("贵州茅台涨幅排名", "个股排名", False),
        ("贵州茅台2099年的成交量", "未来日期", False),
        ("银行的主力资金", "缺少板块后缀", False),
        
        # 修正预期的测试（应该成功）
        ("成交量排名", "成交量排名有效", True),
        ("成交额排行", "成交额排行有效", True),
    ]
    
    print("快速测试修复效果")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for query, test_name, should_succeed in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        print(f"预期: {'成功' if should_succeed else '失败'}")
        
        try:
            result = agent.query(query)
            success = result.get('success', False)
            
            # 判断是否符合预期
            if success == should_succeed:
                if success:
                    print("✅ 通过（成功执行）")
                else:
                    print(f"✅ 通过（正确拒绝）: {result.get('error', '')}")
                passed += 1
            else:
                if success:
                    print("❌ 失败（应该拒绝但成功了）")
                else:
                    print(f"❌ 失败（应该成功但失败了）: {result.get('error', '未知错误')}")
                failed += 1
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"总计: {passed + failed}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = test_fixes()
    
    if failed == 0:
        print("\n🎉 所有修复测试通过！")
        print("\n建议运行完整测试:")
        print("python clear_cache_simple.py")
        print("python test_sql_agent_comprehensive.py")
    else:
        print("\n⚠️ 部分测试仍有问题，需要进一步调试")