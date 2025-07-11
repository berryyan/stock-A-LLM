#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证资金流向数值精度修复
"""

from agents.money_flow_agent import MoneyFlowAgent
import time

def test_money_flow_fix():
    """测试资金流向修复"""
    
    print("=" * 80)
    print("资金流向数值精度修复验证")
    print("=" * 80)
    
    agent = MoneyFlowAgent()
    
    # 测试用例
    test_cases = [
        "贵州茅台的主力资金流向",
        "平安银行的资金流向分析",
        "比亚迪最近7天的主力资金"
    ]
    
    all_success = True
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {query}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result['success']:
                print(f"✅ 成功 (耗时: {elapsed:.2f}秒)")
                
                # 检查结果中的数值
                if 'money_flow_data' in result and result['money_flow_data']:
                    data = result['money_flow_data']
                    main_capital = data.get('main_capital', {})
                    net_flow = main_capital.get('net_flow', 0)
                    
                    print(f"主力资金净流向: {net_flow:.2f} 万元")
                    
                    # 检查数值是否合理（不应该是极大值）
                    if abs(net_flow) > 1e10:  # 大于100亿的异常值
                        print("❌ 数值异常：净流向金额过大")
                        all_success = False
                    else:
                        print("✅ 数值正常")
                        
                    # 显示部分分析结果
                    if 'result' in result:
                        result_text = result['result']
                        # 找到主力资金部分
                        lines = result_text.split('\n')
                        for line in lines:
                            if '主力资金' in line and '万元' in line:
                                print(f"报告显示: {line.strip()}")
                                break
                                
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                all_success = False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            all_success = False
    
    print("\n" + "=" * 80)
    print(f"测试完成: {'✅ 全部通过' if all_success else '❌ 有失败'}")
    print("=" * 80)
    
    return all_success


if __name__ == "__main__":
    test_money_flow_fix()