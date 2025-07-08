#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证SQL模板是否正确添加
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sql_templates import SQLTemplates

def verify_templates():
    """验证新添加的SQL模板"""
    print("验证SQL模板...")
    print("-" * 50)
    
    # 检查新添加的模板
    templates_to_check = [
        ('PROFIT_LATEST', '个股利润查询模板'),
        ('MONEY_FLOW_RANKING_IN', '主力净流入排名模板'),
        ('MONEY_FLOW_RANKING_OUT', '主力净流出排名模板')
    ]
    
    all_passed = True
    
    for template_name, description in templates_to_check:
        if hasattr(SQLTemplates, template_name):
            print(f"✅ {template_name} ({description}) - 存在")
            # 获取SQL内容并显示前100个字符
            sql_content = getattr(SQLTemplates, template_name)
            preview = sql_content.strip()[:100].replace('\n', ' ')
            print(f"   SQL预览: {preview}...")
        else:
            print(f"❌ {template_name} ({description}) - 不存在")
            all_passed = False
    
    print("-" * 50)
    
    # 检查其他重要模板
    print("\n检查其他相关模板：")
    other_templates = [
        'STOCK_PRICE_LATEST',
        'FINANCIAL_LATEST', 
        'MAIN_FORCE_RANKING',
        'PE_RANKING',
        'PB_RANKING',
        'PROFIT_RANKING',
        'REVENUE_RANKING',
        'ROE_RANKING'
    ]
    
    for template_name in other_templates:
        if hasattr(SQLTemplates, template_name):
            print(f"✅ {template_name} - 存在")
        else:
            print(f"❌ {template_name} - 不存在")
    
    print("-" * 50)
    
    if all_passed:
        print("\n✅ 所有新模板都已成功添加！")
    else:
        print("\n❌ 有些模板未成功添加，请检查sql_templates.py文件")
    
    return all_passed

if __name__ == "__main__":
    verify_templates()