#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试概念匹配器功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.concept.concept_matcher import ConceptMatcher
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_concept_expansion():
    """测试概念扩展功能"""
    print("="*60)
    print("测试概念扩展功能")
    print("="*60)
    
    matcher = ConceptMatcher()
    
    # 测试用例
    test_cases = [
        ["固态电池"],
        ["新能源汽车"],
        ["人工智能"],
        ["医药"],
        ["半导体"],
        ["充电桩"],
        ["光伏"],
        ["5G通信"]
    ]
    
    for concepts in test_cases:
        print(f"\n原始概念: {concepts}")
        try:
            # 测试LLM扩展
            expanded = matcher.expand_concepts(concepts)
            print(f"扩展结果 ({len(expanded)}个): {expanded}")
            
            # 检查是否包含原始概念
            for original in concepts:
                if original not in expanded:
                    print(f"  ⚠️ 警告：扩展结果未包含原始概念 '{original}'")
                    
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
    
    # 测试缓存
    print("\n\n测试缓存功能:")
    print("再次查询'固态电池'（应该从缓存返回）...")
    expanded = matcher.expand_concepts(["固态电池"])
    print(f"缓存结果: {expanded}")

def test_fuzzy_matching():
    """测试模糊匹配功能"""
    print("\n\n" + "="*60)
    print("测试模糊匹配功能")
    print("="*60)
    
    matcher = ConceptMatcher()
    
    # 模拟数据库概念
    db_concepts = [
        {"ts_code": "881157.TI", "name": "固态电池"},
        {"ts_code": "881158.TI", "name": "固态电池概念"},
        {"ts_code": "881159.TI", "name": "全固态电池"},
        {"ts_code": "881160.TI", "name": "锂电池"},
        {"ts_code": "881161.TI", "name": "新能源电池"},
        {"ts_code": "881162.TI", "name": "充电桩"},
        {"ts_code": "881163.TI", "name": "充电站"},
        {"ts_code": "881164.TI", "name": "人工智能"},
        {"ts_code": "881165.TI", "name": "AI概念"},
        {"ts_code": "881166.TI", "name": "新能源车"},
        {"ts_code": "881167.TI", "name": "新能源汽车"},
        {"ts_code": "881168.TI", "name": "半导体"},
        {"ts_code": "881169.TI", "name": "芯片概念"}
    ]
    
    # 测试查询
    test_queries = [
        ["电池"],
        ["固态电池", "锂电池"],
        ["充电"],
        ["人工智能", "AI"],
        ["新能源"],
        ["芯片"]
    ]
    
    for query_concepts in test_queries:
        print(f"\n查询概念: {query_concepts}")
        matched = matcher.match_concepts_in_database(query_concepts, db_concepts)
        
        if matched:
            print(f"匹配到 {len(matched)} 个概念:")
            for m in matched:
                print(f"  - {m['name']} ({m['ts_code']})")
        else:
            print("  未找到匹配的概念")

def test_rule_based_expansion():
    """测试规则扩展（降级方案）"""
    print("\n\n" + "="*60)
    print("测试规则扩展功能（降级方案）")
    print("="*60)
    
    matcher = ConceptMatcher()
    
    # 直接调用规则扩展
    test_concepts = [
        ["电池"],
        ["充电"],
        ["光伏"],
        ["人工智能"],
        ["5G"]
    ]
    
    for concepts in test_concepts:
        print(f"\n原始概念: {concepts}")
        expanded = matcher._rule_based_expand(concepts)
        print(f"规则扩展: {expanded}")

def test_edge_cases():
    """测试边界情况"""
    print("\n\n" + "="*60)
    print("测试边界情况")
    print("="*60)
    
    matcher = ConceptMatcher()
    
    # 测试空输入
    print("\n1. 测试空输入:")
    try:
        result = matcher.expand_concepts([])
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 测试特殊字符
    print("\n2. 测试特殊字符:")
    try:
        result = matcher.expand_concepts(["5G/6G", "AI+医疗"])
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 测试长概念名
    print("\n3. 测试长概念名:")
    try:
        result = matcher.expand_concepts(["新能源汽车充电基础设施建设"])
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 测试多个概念
    print("\n4. 测试多个概念:")
    try:
        result = matcher.expand_concepts(["电池", "充电", "新能源"])
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {str(e)}")


def main():
    """主测试函数"""
    print("开始测试ConceptMatcher...")
    print("="*80)
    
    # 运行各项测试
    test_concept_expansion()
    test_fuzzy_matching()
    test_rule_based_expansion()
    test_edge_cases()
    
    print("\n\n测试完成！")
    print("="*80)


if __name__ == "__main__":
    main()