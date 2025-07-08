#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复相对时间范围问题
针对K线查询等需要日期范围的查询，正确处理"上个月"、"去年"等表达
"""

import re
from datetime import datetime, timedelta
import calendar

def enhance_date_range_extraction():
    """增强参数提取器的日期范围提取功能"""
    
    # 读取parameter_extractor.py
    with open('utils/parameter_extractor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到_extract_date_range方法的位置
    method_start = content.find('def _extract_date_range(self, query: str, params: ExtractedParams) -> None:')
    if method_start == -1:
        print("未找到_extract_date_range方法")
        return
    
    # 找到方法的结束位置（下一个def或类结束）
    method_end = content.find('\n    def ', method_start + 1)
    if method_end == -1:
        method_end = len(content)
    
    # 获取方法内容
    method_content = content[method_start:method_end]
    
    # 在方法开始处添加相对时间范围处理
    new_method_content = method_content.replace(
        '"""提取日期范围"""',
        '''"""提取日期范围"""
        # 先处理相对时间范围（上个月、去年等）
        relative_range_patterns = [
            (r'上个月', lambda: self._get_last_month_range()),
            (r'本月', lambda: self._get_current_month_range()),
            (r'去年', lambda: self._get_last_year_range()),
            (r'今年', lambda: self._get_current_year_range()),
            (r'上一?个?季度', lambda: self._get_last_quarter_range()),
            (r'本季度', lambda: self._get_current_quarter_range()),
        ]
        
        for pattern, range_func in relative_range_patterns:
            if re.search(pattern, query):
                try:
                    start_date, end_date = range_func()
                    params.date_range = (start_date, end_date)
                    self.logger.info(f"提取到相对日期范围: {start_date} 至 {end_date}")
                    return
                except Exception as e:
                    self.logger.error(f"相对日期范围提取失败: {e}")
        '''
    )
    
    # 替换方法内容
    content = content[:method_start] + new_method_content + content[method_end:]
    
    # 在类中添加辅助方法
    class_end = content.rfind('\n\n')
    helper_methods = '''
    def _get_last_month_range(self):
        """获取上个月的日期范围"""
        today = datetime.now()
        # 计算上个月的第一天
        if today.month == 1:
            first_day = datetime(today.year - 1, 12, 1)
        else:
            first_day = datetime(today.year, today.month - 1, 1)
        # 计算上个月的最后一天
        last_day = datetime(today.year, today.month, 1) - timedelta(days=1)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def _get_current_month_range(self):
        """获取本月的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        last_day = datetime(today.year, today.month, last_day_num)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def _get_last_year_range(self):
        """获取去年的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year - 1, 1, 1)
        last_day = datetime(today.year - 1, 12, 31)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def _get_current_year_range(self):
        """获取今年的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year, 1, 1)
        last_day = datetime(today.year, 12, 31)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def _get_last_quarter_range(self):
        """获取上个季度的日期范围"""
        today = datetime.now()
        current_quarter = (today.month - 1) // 3 + 1
        
        if current_quarter == 1:
            # 上个季度是去年Q4
            year = today.year - 1
            quarter = 4
        else:
            year = today.year
            quarter = current_quarter - 1
        
        quarter_months = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12)
        }
        
        start_month, end_month = quarter_months[quarter]
        first_day = datetime(year, start_month, 1)
        last_day_num = calendar.monthrange(year, end_month)[1]
        last_day = datetime(year, end_month, last_day_num)
        
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def _get_current_quarter_range(self):
        """获取本季度的日期范围"""
        today = datetime.now()
        current_quarter = (today.month - 1) // 3 + 1
        
        quarter_months = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12)
        }
        
        start_month, end_month = quarter_months[current_quarter]
        first_day = datetime(today.year, start_month, 1)
        last_day_num = calendar.monthrange(today.year, end_month)[1]
        last_day = datetime(today.year, end_month, last_day_num)
        
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
'''
    
    content = content[:class_end] + helper_methods + content[class_end:]
    
    # 写回文件
    with open('utils/parameter_extractor.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("相对时间范围修复完成！")
    print("添加了以下功能：")
    print("1. 上个月 -> 上月第一天到最后一天")
    print("2. 本月 -> 本月第一天到最后一天")
    print("3. 去年 -> 去年1月1日到12月31日")
    print("4. 今年 -> 今年1月1日到12月31日")
    print("5. 上个季度 -> 上季度第一天到最后一天")
    print("6. 本季度 -> 本季度第一天到最后一天")

if __name__ == "__main__":
    enhance_date_range_extraction()