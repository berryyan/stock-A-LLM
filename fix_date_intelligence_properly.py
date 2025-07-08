#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确地在date_intelligence模块中添加相对日期范围功能
而不是在parameter_extractor中硬编码
"""

def add_relative_date_ranges_to_date_intelligence():
    """向date_intelligence模块添加相对日期范围功能"""
    
    # 读取date_intelligence.py
    with open('utils/date_intelligence.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到TradingDayCalculator类
    class_pos = content.find('class TradingDayCalculator:')
    if class_pos == -1:
        print("未找到TradingDayCalculator类")
        return
    
    # 找到类的结束位置（下一个class或文件结束）
    next_class = content.find('\nclass ', class_pos + 1)
    if next_class == -1:
        class_end_pos = len(content)
    else:
        class_end_pos = next_class
    
    # 在类的末尾添加方法
    insert_pos = class_end_pos - 1
    
    new_methods = '''
    
    def get_last_month_range(self) -> Tuple[str, str]:
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
    
    def get_current_month_range(self) -> Tuple[str, str]:
        """获取本月的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        import calendar
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        last_day = datetime(today.year, today.month, last_day_num)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def get_last_year_range(self) -> Tuple[str, str]:
        """获取去年的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year - 1, 1, 1)
        last_day = datetime(today.year - 1, 12, 31)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def get_current_year_range(self) -> Tuple[str, str]:
        """获取今年的日期范围"""
        today = datetime.now()
        first_day = datetime(today.year, 1, 1)
        last_day = datetime(today.year, 12, 31)
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def get_last_quarter_range(self) -> Tuple[str, str]:
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
        import calendar
        last_day_num = calendar.monthrange(year, end_month)[1]
        last_day = datetime(year, end_month, last_day_num)
        
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
    
    def get_current_quarter_range(self) -> Tuple[str, str]:
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
        import calendar
        last_day_num = calendar.monthrange(today.year, end_month)[1]
        last_day = datetime(today.year, end_month, last_day_num)
        
        return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
'''
    
    # 插入新方法
    content = content[:insert_pos] + new_methods + content[insert_pos:]
    
    # 确保导入了Tuple
    if 'from typing import' in content and 'Tuple' not in content:
        content = content.replace('from typing import', 'from typing import Tuple, ')
    
    # 写回文件
    with open('utils/date_intelligence.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("成功在date_intelligence.py中添加相对日期范围方法！")
    
    # 现在修改parameter_extractor.py，让它调用date_intelligence的方法
    update_parameter_extractor()

def update_parameter_extractor():
    """更新parameter_extractor.py，使用date_intelligence的方法"""
    
    with open('utils/parameter_extractor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除硬编码的方法（从_get_last_month_range到_get_current_quarter_range）
    # 查找第一个方法
    start_pos = content.find('    def _get_last_month_range(self):')
    if start_pos != -1:
        # 查找最后一个方法的结束
        end_pos = content.find('        return first_day.strftime', start_pos)
        if end_pos != -1:
            # 找到这行的结束
            line_end = content.find('\n', end_pos + 50)
            if line_end != -1:
                # 删除这些方法
                content = content[:start_pos] + content[line_end + 1:]
    
    # 更新调用方式
    replacements = [
        ('self._get_last_month_range()', 'date_intelligence.calculator.get_last_month_range()'),
        ('self._get_current_month_range()', 'date_intelligence.calculator.get_current_month_range()'),
        ('self._get_last_year_range()', 'date_intelligence.calculator.get_last_year_range()'),
        ('self._get_current_year_range()', 'date_intelligence.calculator.get_current_year_range()'),
        ('self._get_last_quarter_range()', 'date_intelligence.calculator.get_last_quarter_range()'),
        ('self._get_current_quarter_range()', 'date_intelligence.calculator.get_current_quarter_range()'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 写回文件
    with open('utils/parameter_extractor.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("成功更新parameter_extractor.py，现在使用date_intelligence的方法！")

if __name__ == "__main__":
    add_relative_date_ranges_to_date_intelligence()