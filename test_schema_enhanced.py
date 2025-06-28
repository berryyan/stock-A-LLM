#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Schema知识库增强功能
验证中文字段识别和表建议功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent

def test_chinese_field_recognition():
    """测试中文字段识别"""
    print("="*60)
    print("测试Schema知识库中文字段识别功能")
    print("="*60)
    
    # 创建SQL Agent
    agent = SQLAgent()
    
    # 测试包含多个中文字段的查询
    test_queries = [
        "查询贵州茅台的营业收入和净利润",
        "比较茅台和五粮液的总资产和总负债",
        "分析中国平安的市盈率和市净率",
        "查看比亚迪最近的成交量和成交额"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 测试查询: {query}")
        print("-"*50)
        
        try:
            # 直接调用预处理方法看效果
            processed = agent._preprocess_question(query)
            print(f"   预处理后: {processed}")
            
            # 执行查询
            result = agent.query(query)
            
            if result['success']:
                print(f"   查询成功!")
                # 只显示结果的前100个字符
                result_preview = str(result['result'])[:100] + "..." if len(str(result['result'])) > 100 else str(result['result'])
                print(f"   结果预览: {result_preview}")
            else:
                print(f"   查询失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   错误: {e}")

def check_schema_mapping():
    """检查Schema知识库的中文映射"""
    print("\n\n" + "="*60)
    print("Schema知识库中文映射检查")
    print("="*60)
    
    from utils.schema_knowledge_base import schema_kb
    
    print("\n当前支持的中文字段映射:")
    for chinese, english in list(schema_kb.chinese_mapping.items())[:15]:  # 显示前15个
        print(f"   {chinese} -> {english}")
    
    print(f"\n共支持 {len(schema_kb.chinese_mapping)} 个中文字段映射")
    
    # 测试数据定位
    test_fields = ["营业收入", "净利润", "总资产", "成交量", "市盈率"]
    print("\n数据定位测试:")
    for field in test_fields:
        location = schema_kb.locate_data(field)
        if location:
            print(f"   {field} -> {location['table']}.{location['field']}")
        else:
            print(f"   {field} -> 未找到")

if __name__ == "__main__":
    test_chinese_field_recognition()
    check_schema_mapping()
    
    print("\n" + "="*60)
    print("增强测试完成！")
    print("="*60)