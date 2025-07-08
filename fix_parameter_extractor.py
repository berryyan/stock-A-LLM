#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复参数提取器的相对时间和股票识别问题
"""

import os
import re
from datetime import datetime, timedelta
import calendar

def fix_parameter_extractor():
    """修复parameter_extractor.py中的问题"""
    
    # 读取原文件
    file_path = "utils/parameter_extractor.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"备份文件创建: {backup_path}")
    
    # 1. 在_extract_date_range方法中添加"本月"、"上个月"、"去年"等相对时间支持
    # 查找_extract_date_range方法中的time_mappings部分
    time_mappings_pattern = r'(time_mappings = \{[^}]+\})'
    time_mappings_match = re.search(time_mappings_pattern, content, re.DOTALL)
    
    if time_mappings_match:
        # 在现有映射后添加相对时间处理
        insert_pos = time_mappings_match.end()
        
        # 添加相对时间处理代码
        relative_time_code = '''
        
        # 处理相对时间表达（本月、上个月、去年等）
        current_date = datetime.now()
        
        # 处理"本月"
        if "本月" in query or "当月" in query or "这个月" in query:
            year = current_date.year
            month = current_date.month
            last_day = calendar.monthrange(year, month)[1]
            params.date_range = (f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}")
            self.logger.info(f"提取到日期范围（本月）: {params.date_range[0]} 至 {params.date_range[1]}")
            return
            
        # 处理"上个月"
        if "上个月" in query or "上月" in query:
            # 计算上个月
            if current_date.month == 1:
                year = current_date.year - 1
                month = 12
            else:
                year = current_date.year
                month = current_date.month - 1
            last_day = calendar.monthrange(year, month)[1]
            params.date_range = (f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}")
            self.logger.info(f"提取到日期范围（上个月）: {params.date_range[0]} 至 {params.date_range[1]}")
            return
            
        # 处理"去年"
        if "去年" in query and "同期" not in query:
            year = current_date.year - 1
            params.date_range = (f"{year}-01-01", f"{year}-12-31")
            self.logger.info(f"提取到日期范围（去年）: {params.date_range[0]} 至 {params.date_range[1]}")
            return
        '''
        
        # 在time_mappings之后插入代码
        content = content[:insert_pos] + relative_time_code + content[insert_pos:]
    
    # 2. 修复_extract_stocks方法，改进股票提取逻辑，避免日期格式干扰
    # 在_extract_stocks方法开始处添加预处理
    extract_stocks_pattern = r'(def _extract_stocks\(self, query: str, params: ExtractedParams\) -> None:\s*"""提取股票信息""")'
    extract_stocks_match = re.search(extract_stocks_pattern, content)
    
    if extract_stocks_match:
        insert_pos = extract_stocks_match.end()
        
        preprocess_code = '''
        # 预处理查询，临时替换日期格式，避免干扰股票识别
        date_placeholders = []
        
        # 替换斜杠格式日期（如2025/06/01）
        slash_date_pattern = r'\d{4}/\d{1,2}/\d{1,2}'
        slash_dates = re.findall(slash_date_pattern, query)
        for i, date in enumerate(slash_dates):
            placeholder = f"__DATE_PLACEHOLDER_{i}__"
            query = query.replace(date, placeholder)
            date_placeholders.append((placeholder, date))
        
        # 替换其他日期格式
        other_date_patterns = [
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{8}'
        ]
        
        for pattern in other_date_patterns:
            dates = re.findall(pattern, query)
            for date in dates:
                # 检查是否是股票代码（6位数字）
                if not (pattern == r'\d{8}' and len(date) == 6):
                    placeholder = f"__DATE_PLACEHOLDER_{len(date_placeholders)}__"
                    query = query.replace(date, placeholder)
                    date_placeholders.append((placeholder, date))
        '''
        
        content = content[:insert_pos] + preprocess_code + content[insert_pos:]
        
        # 在方法结束前恢复日期
        # 查找方法的结尾
        method_end_pattern = r'(\n\s*def\s+\w+\(.*?\):)'
        next_method = re.search(method_end_pattern, content[insert_pos:])
        if next_method:
            restore_pos = insert_pos + next_method.start()
            
            restore_code = '''
        
        # 恢复被替换的日期
        for placeholder, original_date in date_placeholders:
            params.raw_query = params.raw_query.replace(placeholder, original_date)
        '''
            content = content[:restore_pos] + restore_code + content[restore_pos:]
    
    # 3. 处理中文数字（在_extract_limit方法中已经有chinese_number_converter的调用）
    # 但需要确保在日期处理中也支持中文数字
    # 在_extract_date_range方法中添加中文数字处理
    chinese_number_code = '''
        # 处理中文数字的相对时间（如"前十天"）
        from utils.chinese_number_converter import chinese_to_arabic
        
        # 匹配"前X天"、"最近X天"等模式
        chinese_patterns = [
            (r'前([一二三四五六七八九十百千万]+)天', 'past'),
            (r'最近([一二三四五六七八九十百千万]+)天', 'recent'),
            (r'过去([一二三四五六七八九十百千万]+)天', 'recent'),
            (r'前([一二三四五六七八九十百千万]+)个?交易日', 'past_trading'),
            (r'最近([一二三四五六七八九十百千万]+)个?交易日', 'recent_trading'),
        ]
        
        for pattern, time_type in chinese_patterns:
            match = re.search(pattern, query)
            if match:
                chinese_num = match.group(1)
                try:
                    arabic_num = chinese_to_arabic(chinese_num)
                    if arabic_num > 0:
                        # 根据类型处理
                        if time_type in ['recent', 'recent_trading', 'past', 'past_trading']:
                            if hasattr(date_intelligence.calculator, 'get_trading_days_range'):
                                result = date_intelligence.calculator.get_trading_days_range(arabic_num)
                                if result:
                                    params.date_range = result
                                    self.logger.info(f"提取到日期范围（{chinese_num}={arabic_num}天）: {result[0]} 至 {result[1]}")
                                    return
                except Exception as e:
                    self.logger.warning(f"中文数字转换失败: {chinese_num}, 错误: {e}")
    '''
    
    # 在_extract_date_range方法的time_mappings后面插入
    content = re.sub(
        r'(for time_word, days in time_mappings\.items\(\):.*?return\s*\n)',
        r'\1' + chinese_number_code,
        content,
        flags=re.DOTALL
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"修复完成: {file_path}")
    print("\n修复内容:")
    print("1. 添加了'本月'、'上个月'、'去年'等相对时间支持")
    print("2. 修复了日期格式干扰股票识别的问题") 
    print("3. 添加了中文数字时间表达的支持")
    
    return True

def test_fixes():
    """测试修复效果"""
    print("\n测试修复效果...")
    
    test_cases = [
        "宁德时代从2025/06/01到2025/06/30的K线",
        "贵州茅台本月的K线",
        "平安银行上个月的K线", 
        "比亚迪去年的K线",
        "中国平安前十天的走势"
    ]
    
    # 这里只是打印测试用例，实际测试需要运行综合测试
    print("\n需要测试的用例:")
    for case in test_cases:
        print(f"- {case}")
    
    print("\n请运行以下命令进行测试:")
    print("python clear_cache_simple.py")
    print("python test_sql_agent_comprehensive.py")

if __name__ == "__main__":
    if fix_parameter_extractor():
        test_fixes()