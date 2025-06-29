#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析数据库表结构，为快速查询模板提出建议
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.schema_knowledge_base import schema_kb
import json

def analyze_tables_for_templates():
    """分析所有表结构，提出查询模板建议"""
    
    print("=== 数据库表结构分析报告 ===\n")
    
    # 获取统计信息
    stats = schema_kb.get_statistics()
    print(f"数据库概况：")
    print(f"- 表数量：{stats['table_count']}")
    print(f"- 字段总数：{stats['field_count']}")
    print(f"- 中文映射数：{stats['chinese_mapping_count']}")
    print(f"\n")
    
    # 分析每个表
    for table_name in sorted(schema_kb.table_knowledge.keys()):
        table_info = schema_kb.table_knowledge[table_name]
        print(f"\n{'='*60}")
        print(f"表名：{table_name}")
        print(f"描述：{table_info.get('comment', '无描述')}")
        print(f"记录数：{table_info.get('row_count', 0):,}")
        print(f"主要字段：{', '.join(table_info.get('primary_fields', []))}")
        
        # 获取中文映射
        mappings = schema_kb.table_field_mappings.get(table_name, {})
        if mappings:
            print(f"\n字段中文映射（前10个）：")
            for i, (chinese, english) in enumerate(list(mappings.items())[:10]):
                field_info = table_info['fields'].get(english, {})
                field_type = field_info.get('type', 'unknown')
                print(f"  {chinese} -> {english} ({field_type})")
                
        # 查看主题分类
        topics = []
        for topic, topic_info in schema_kb.topic_knowledge.items():
            if table_name in topic_info['tables']:
                topics.append(topic)
        if topics:
            print(f"\n所属主题：{', '.join(topics)}")
    
    # 输出主题分类总结
    print(f"\n\n{'='*60}")
    print("主题分类总结：")
    for topic, info in schema_kb.topic_knowledge.items():
        print(f"\n{topic}：")
        print(f"  相关表：{', '.join(info['tables'])}")
        print(f"  关键字段：{', '.join(info['key_fields'][:5])}")

if __name__ == "__main__":
    analyze_tables_for_templates()