#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复市值排名的日期处理问题
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_date_issue():
    """分析日期处理问题"""
    
    print("市值排名日期处理问题分析")
    print("=" * 80)
    
    # 1. 检查_get_last_trading_date的实现
    print("\n1. _get_last_trading_date 问题：")
    print("   - 查询 tu_daily_basic 表可能返回过时数据")
    print("   - 建议：改用 tu_daily_detail 表或使用日期智能解析的缓存")
    
    # 2. 分析日期提取逻辑
    print("\n2. 日期提取逻辑问题：")
    print("   - 日期智能解析后的格式可能不被 _extract_date_from_query 识别")
    print("   - 例如：'2025-07-01总市值...' 中的日期格式")
    
    # 3. 提出修复方案
    print("\n3. 修复方案：")
    print("   A. 修改 _get_last_trading_date 方法：")
    print("      - 使用 date_intelligence.get_latest_trading_day()")
    print("      - 或改查询 tu_daily_detail 表")
    print("")
    print("   B. 增强 _extract_date_from_query 方法：")
    print("      - 支持更多日期格式")
    print("      - 特别是连续的日期格式（如：2025-07-01总市值）")
    print("")
    print("   C. 在快速路由中直接使用日期智能解析的结果：")
    print("      - 检查 parsing_result 中是否有日期信息")
    print("      - 优先使用解析后的日期")
    
    # 4. 生成修复代码
    print("\n4. 建议的代码修改：")
    print("-" * 40)
    print("""
# 在 sql_agent.py 的 _get_last_trading_date 方法中：
def _get_last_trading_date(self) -> str:
    \"\"\"获取最近的交易日期\"\"\"
    try:
        # 优先使用日期智能解析
        from utils.date_intelligence import date_intelligence
        latest_date = date_intelligence.get_latest_trading_day()
        if latest_date:
            return latest_date.strftime('%Y%m%d')
    except Exception as e:
        self.logger.warning(f"使用日期智能解析失败: {e}")
    
    # 回退到数据库查询
    try:
        # 改用 tu_daily_detail 表，数据更新更及时
        result = self.mysql_connector.execute_query(
            'SELECT DISTINCT trade_date FROM tu_daily_detail ORDER BY trade_date DESC LIMIT 1'
        )
        if result and result[0]['trade_date']:
            return str(result[0]['trade_date'])
    except Exception as e:
        self.logger.error(f"获取最新交易日失败: {e}")
        # 使用默认逻辑...
""")
    
    print("\n" + "-" * 40)
    print("""
# 在 _extract_date_from_query 方法中添加新的模式：
def _extract_date_from_query(self, query: str) -> Optional[str]:
    \"\"\"从查询中提取日期（YYYYMMDD格式）\"\"\"
    # 匹配各种日期格式
    date_patterns = [
        (r'(\\d{8})', lambda m: m.group(1)),  # 20250627
        (r'(\\d{4})-(\\d{2})-(\\d{2})', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}"),  # 2025-06-27
        (r'(\\d{4})年(\\d{2})月(\\d{2})日', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}"),  # 2025年06月27日
        # 新增：连续的日期格式（无空格）
        (r'(\\d{4})-(\\d{1,2})-(\\d{1,2})(?=[^\\s\\d])', lambda m: f"{m.group(1)}{m.group(2).zfill(2)}{m.group(3).zfill(2)}"),
    ]
    # ...
""")


if __name__ == "__main__":
    analyze_date_issue()