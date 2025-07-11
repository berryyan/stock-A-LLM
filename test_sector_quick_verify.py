#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证板块分析功能
"""
import sys
sys.path.append('.')

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from database.mysql_connector import MySQLConnector

def test_sector_features():
    """测试板块相关功能"""
    print("="*60)
    print("Money Flow Agent 板块功能快速验证")
    print("="*60)
    
    # 初始化Agent
    mysql_conn = MySQLConnector()
    agent = MoneyFlowAgentModular(mysql_conn)
    
    # 测试用例
    test_cases = [
        # SQL路由测试（应该返回错误）
        {
            'query': '银行板块的主力资金',
            'type': 'SQL路由',
            'expected': '应该由SQL Agent处理'
        },
        # 深度分析测试（应该成功）
        {
            'query': '分析银行板块的资金流向',
            'type': '板块深度分析',
            'expected': '成功'
        },
        {
            'query': '评估新能源板块的资金趋势',
            'type': '板块趋势评估',
            'expected': '成功'
        },
        # 错误板块名称
        {
            'query': '分析银行的资金流向',
            'type': '缺少板块后缀',
            'expected': '错误提示'
        }
    ]
    
    # 执行测试
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['type']}")
        print(f"查询: {test['query']}")
        print(f"预期: {test['expected']}")
        
        try:
            result = agent.query(test['query'])
            
            if result.get('success'):
                print("✅ 查询成功")
                # 打印部分结果
                result_str = str(result.get('result', ''))
                if len(result_str) > 200:
                    print(f"结果预览: {result_str[:200]}...")
                else:
                    print(f"结果: {result_str}")
                    
                # 检查板块数据
                if 'sector_data' in result:
                    sector_data = result['sector_data']
                    print(f"板块名称: {sector_data.get('sector_name')}")
                    print(f"板块代码: {sector_data.get('sector_code')}")
                    print(f"总净流入: {sector_data.get('total_net_flow')}万元")
                    print(f"流向趋势: {sector_data.get('flow_trend')}")
                    print(f"板块排名: 第{sector_data.get('sector_rank')}名")
            else:
                error = result.get('error', '未知错误')
                print(f"❌ 查询失败: {error}")
                
                # 检查是否是预期的错误
                if 'SQL Agent' in error and 'SQL路由' in test['type']:
                    print("✅ 正确识别为SQL查询")
                elif '板块' in error and '缺少板块后缀' in test['type']:
                    print("✅ 正确识别板块名称错误")
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print("\n" + "="*60)
    print("板块功能验证完成")
    print("="*60)

if __name__ == "__main__":
    test_sector_features()