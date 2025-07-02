#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试资金流向数值精度问题
"""

from database.mysql_connector import MySQLConnector
from datetime import datetime, timedelta

def test_raw_data():
    """测试原始数据"""
    
    mysql_conn = MySQLConnector()
    
    # 测试查询
    ts_code = "600519.SH"
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    
    query = f"""
    SELECT 
        trade_date, ts_code, name, 
        buy_sm_amount, buy_md_amount, buy_lg_amount, buy_elg_amount,
        net_amount,
        buy_sm_amount_rate, buy_md_amount_rate, buy_lg_amount_rate, buy_elg_amount_rate
    FROM tu_moneyflow_dc
    WHERE ts_code = '{ts_code}'
    AND trade_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY trade_date DESC
    LIMIT 5
    """
    
    print(f"查询SQL: {query}")
    print("\n原始数据：")
    print("-" * 100)
    
    try:
        results = mysql_conn.execute_query(query)
        
        for row in results:
            print(f"\n日期: {row['trade_date']}")
            print(f"股票: {row['name']} ({row['ts_code']})")
            print(f"买入金额(万元):")
            print(f"  - 小单: {row['buy_sm_amount']}")
            print(f"  - 中单: {row['buy_md_amount']}")
            print(f"  - 大单: {row['buy_lg_amount']}")
            print(f"  - 超大单: {row['buy_elg_amount']}")
            print(f"净流入金额: {row['net_amount']} 万元")
            print(f"买入占比:")
            print(f"  - 小单: {row['buy_sm_amount_rate']}")
            print(f"  - 中单: {row['buy_md_amount_rate']}")
            print(f"  - 大单: {row['buy_lg_amount_rate']}")
            print(f"  - 超大单: {row['buy_elg_amount_rate']}")
            
            # 计算主力资金
            main_buy = float(row['buy_lg_amount'] or 0) + float(row['buy_elg_amount'] or 0)
            total_buy = (float(row['buy_sm_amount'] or 0) + float(row['buy_md_amount'] or 0) + 
                        float(row['buy_lg_amount'] or 0) + float(row['buy_elg_amount'] or 0))
            
            print(f"\n计算值:")
            print(f"  - 主力买入总额: {main_buy} 万元")
            print(f"  - 总买入额: {total_buy} 万元")
            
            if total_buy > 0:
                main_ratio = main_buy / total_buy
                main_net = float(row['net_amount'] or 0) * main_ratio
                print(f"  - 主力占比: {main_ratio:.2%}")
                print(f"  - 主力净流入(估算): {main_net:.2f} 万元")
            
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()


def test_calculation_flow():
    """测试计算流程"""
    from utils.money_flow_analyzer import MoneyFlowAnalyzer
    
    print("\n\n" + "="*100)
    print("测试MoneyFlowAnalyzer计算流程")
    print("="*100)
    
    analyzer = MoneyFlowAnalyzer()
    
    # 获取原始数据
    ts_code = "600519.SH"
    data = analyzer.fetch_money_flow_data(ts_code, days=5)
    
    print(f"\n获取到 {len(data)} 条数据")
    
    if data:
        # 测试主力资金计算
        main_analysis = analyzer.analyze_main_capital_flow(data)
        
        print(f"\n主力资金分析结果:")
        print(f"  - 总净流入: {main_analysis.get('main_capital_net_flow', 0):.2f} 万元")
        print(f"  - 流向趋势: {main_analysis.get('main_capital_flow_trend', 'unknown')}")
        print(f"  - 流向强度: {main_analysis.get('main_capital_flow_strength', 'unknown')}")
        print(f"  - 一致性: {main_analysis.get('main_capital_flow_consistency', 0):.2%}")
        
        # 显示每日流向
        daily_flows = main_analysis.get('daily_flows', [])
        print(f"\n每日主力资金流向:")
        for i, flow in enumerate(daily_flows):
            print(f"  Day {i+1}: {flow:.2f} 万元")


if __name__ == "__main__":
    print("开始调试资金流向数值精度问题...\n")
    
    # 测试原始数据
    test_raw_data()
    
    # 测试计算流程
    test_calculation_flow()