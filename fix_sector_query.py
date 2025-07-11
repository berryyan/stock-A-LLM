#!/usr/bin/env python3
"""修复板块查询问题"""

import sys
sys.path.append('.')

def main():
    print("板块查询问题分析：")
    print("=" * 60)
    
    # 1. 问题定位
    print("\n1. 问题定位：")
    print("   - 文件：agents/sql_agent_modular.py")
    print("   - 方法：_execute_sector_money_flow")
    print("   - 行号：1183-1184")
    print("   - 问题：sector_name已经包含'板块'后缀，但代码又添加了一次")
    
    # 2. 错误示例
    print("\n2. 错误示例：")
    print("   - 用户输入：'银行板块昨天的主力资金'")
    print("   - 提取的sector：'银行板块'")
    print("   - 错误的SQL参数：'银行板块板块'")
    print("   - 导致查询失败")
    
    # 3. 修复方案
    print("\n3. 修复方案：")
    print("   在_execute_sector_money_flow方法中，需要检查sector_name是否已经包含'板块'后缀")
    print("   如果已经包含，则不再添加；如果不包含，才添加")
    
    # 4. 具体修改
    print("\n4. 需要修改的代码（第1183-1184行）：")
    print("   原代码：")
    print("   ```python")
    print("   result = self.mysql_connector.execute_query(sql, {")
    print("       'sector_name': sector_name + '板块',  # 数据库中可能存储为\"银行板块\"")
    print("       'trade_date': trade_date")
    print("   })")
    print("   ```")
    print("\n   修改为：")
    print("   ```python")
    print("   # 检查是否已经包含板块后缀")
    print("   if not sector_name.endswith('板块'):")
    print("       sector_name = sector_name + '板块'")
    print("   ")
    print("   result = self.mysql_connector.execute_query(sql, {")
    print("       'sector_name': sector_name,")
    print("       'trade_date': trade_date")
    print("   })")
    print("   ```")
    
    # 5. 同时需要修改第1189-1192行的重试逻辑
    print("\n5. 同时需要修改重试逻辑（第1189-1192行）：")
    print("   原代码会尝试去掉'板块'后缀，但如果原始输入就没有后缀，这个逻辑是正确的")
    print("   保持现有逻辑不变")
    
    print("\n" + "=" * 60)
    print("建议：执行修复后，测试以下查询：")
    print("1. '银行板块昨天的主力资金'")
    print("2. '银行昨天的主力资金'")
    print("3. '房地产板块的主力资金'")
    print("4. '房地产的主力资金'")

if __name__ == "__main__":
    main()