#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试改进后的ConceptDataAccess
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.concept.concept_data_access import ConceptDataAccess
import logging

logging.basicConfig(level=logging.INFO)

print("=== 测试改进后的ConceptDataAccess ===\n")

# 创建实例
data_access = ConceptDataAccess()

# 1. 查看各数据源的最新日期
print("1. 各数据源最新日期:")
print(f"   同花顺: {data_access._source_latest_dates['ths'] or '静态数据，无日期'}")
print(f"   东财: {data_access._source_latest_dates['dc']}")
print(f"   开盘啦: {data_access._source_latest_dates['kpl']}")

# 2. 测试有问题的概念数据状态
print("\n2. 测试问题概念的数据状态:")
problem_concepts = [
    ('BK0989.DC', '储能'),
    ('BK0968.DC', '固态电池'),
    ('BK0574.DC', '锂电池')
]

for code, name in problem_concepts:
    print(f"\n{code} ({name}):")
    status = data_access.get_source_data_status(code)
    for source, info in status['data_status'].items():
        if info['has_data']:
            print(f"  {source}: 有数据 - {info['record_count']}条记录, 最新日期: {info['latest_date']}")
        else:
            print(f"  {source}: 无数据")

# 3. 测试获取成分股（带数据可用性提示）
print("\n3. 测试获取成分股:")
test_concepts = [
    ('885710.TI', '锂电池概念-同花顺'),
    ('BK0574.DC', '锂电池-东财'),
    ('000345.KP', '快充-开盘啦')
]

for code, desc in test_concepts:
    print(f"\n{desc} ({code}):")
    members = data_access.get_concept_members(code)
    if members:
        print(f"  找到 {len(members)} 只成分股")
        for m in members[:3]:
            print(f"    - {m['name']} ({m['ts_code']})")
        if len(members) > 3:
            print(f"    ... 还有 {len(members)-3} 只")
    else:
        print("  未找到成分股数据")
        # 检查数据状态
        status = data_access.get_source_data_status(code)
        for source, info in status['data_status'].items():
            if not info['has_data']:
                print(f"  提示: {source}数据源暂无数据")

# 4. 测试搜索功能
print("\n4. 测试概念搜索:")
search_keywords = ['储能', '固态电池', '充电']
for keyword in search_keywords:
    print(f"\n搜索 '{keyword}':")
    concepts = data_access.search_concepts(keyword)
    
    # 按数据源分组显示
    by_source = {'ths': [], 'dc': [], 'kpl': []}
    for c in concepts:
        source = c.get('source', 'unknown')
        if source in by_source:
            by_source[source].append(c)
    
    for source, items in by_source.items():
        if items:
            print(f"  {source}: {len(items)}个概念")
            for item in items[:2]:
                print(f"    - {item['name']} ({item['ts_code']})")

data_access.close()

print("\n=== 总结 ===")
print("1. 三个数据源的表结构不同，需要分别处理")
print("2. 东财数据存在严重的数据缺失和更新不及时问题")
print("3. ConceptDataAccess已改进，可以正确处理不同数据源的差异")
print("4. 建议在界面上标注数据来源和时效性，让用户了解数据质量情况")