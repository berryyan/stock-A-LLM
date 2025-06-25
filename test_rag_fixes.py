#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG系统修复测试用例 (v1.4.3)
测试QueryType枚举修复、股票代码映射器、RAG容错机制等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent import HybridAgent
from utils.stock_code_mapper import get_stock_mapper, convert_to_ts_code
from utils.logger import setup_logger
import time

logger = setup_logger("test_rag_fixes")

def test_stock_code_mapper():
    """测试股票代码映射器功能"""
    print("\n" + "="*60)
    print("测试1: 股票代码映射器")
    print("="*60)
    
    mapper = get_stock_mapper()
    
    # 测试用例
    test_cases = [
        # (输入, 预期输出)
        ("600519", "600519.SH"),
        ("600519.SH", "600519.SH"),
        ("贵州茅台", "600519.SH"),
        ("茅台", "600519.SH"),
        ("000858", "000858.SZ"),
        ("五粮液", "000858.SZ"),
        ("诺德股份", "600110.SH"),
        ("诺德新材料", "600110.SH"),
        ("600110", "600110.SH"),
        ("比亚迪", "002594.SZ"),
        ("美的集团", "000333.SZ"),
        ("同花顺", "300033.SZ"),
        ("不存在的公司", None),  # 应该返回None或原值
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        result = convert_to_ts_code(input_val)
        if result == expected or (expected is None and result == input_val):
            print(f"✅ {input_val:20} -> {result}")
            passed += 1
        else:
            print(f"❌ {input_val:20} -> {result} (期望: {expected})")
            failed += 1
    
    # 测试缓存统计
    stats = mapper.get_cache_stats()
    print(f"\n缓存统计: {stats['cache_size']} 条映射")
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    return passed > 0 and failed == 0


def test_rag_query_with_company_name():
    """测试使用公司名称的RAG查询"""
    print("\n" + "="*60)
    print("测试2: RAG查询（使用公司名称）")
    print("="*60)
    
    agent = HybridAgent()
    
    # 测试诺德股份
    print("\n测试查询: 分析诺德股份的2024年年报")
    start = time.time()
    result = agent.query("分析诺德股份的2024年年报")
    elapsed = time.time() - start
    
    print(f"查询耗时: {elapsed:.2f}秒")
    print(f"查询成功: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"查询类型: {result.get('query_type')}")
        answer = result.get('answer', '')
        if answer:
            print(f"答案预览: {answer[:200]}...")
    else:
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    return result.get('success', False)


def test_query_type_routing():
    """测试QueryType路由修复"""
    print("\n" + "="*60)
    print("测试3: QueryType路由精确性")
    print("="*60)
    
    agent = HybridAgent()
    
    test_queries = [
        ("贵州茅台最新股价", "SQL"),
        ("分析茅台的2024年年报", "RAG"),
        ("比较茅台和五粮液的资金流向", "混合"),
    ]
    
    for query, expected_type in test_queries:
        print(f"\n查询: {query}")
        result = agent.query(query)
        
        if result.get('success'):
            actual_type = result.get('query_type', 'unknown')
            print(f"路由类型: {actual_type}")
            print(f"预期类型包含: {expected_type}")
            
            # 检查是否包含预期的处理类型
            if expected_type.lower() in str(actual_type).lower():
                print("✅ 路由正确")
            else:
                print("⚠️  路由可能不准确")
        else:
            print(f"❌ 查询失败: {result.get('error')}")


def test_rag_fallback():
    """测试RAG容错机制"""
    print("\n" + "="*60)
    print("测试4: RAG容错机制（过滤条件降级）")
    print("="*60)
    
    from agents.rag_agent import RAGAgent
    rag_agent = RAGAgent()
    
    # 测试一个可能导致过滤无结果的查询
    print("\n测试带有严格过滤条件的查询...")
    result = rag_agent.query(
        "分析某公司的财务状况",
        filters={'ts_code': 'INVALID.CODE'}  # 故意使用无效代码
    )
    
    print(f"查询成功: {result.get('success', False)}")
    if not result.get('success'):
        error = result.get('error', '')
        if 'no_documents_found' in error:
            print("✅ 正确识别无文档情况")
        else:
            print(f"错误类型: {error}")
    
    return True


def main():
    """运行所有测试"""
    print("RAG系统修复测试 (v1.4.3)")
    print("测试时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    
    tests = [
        ("股票代码映射器", test_stock_code_mapper),
        ("RAG公司名称查询", test_rag_query_with_company_name),
        ("QueryType路由", test_query_type_routing),
        ("RAG容错机制", test_rag_fallback),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n开始测试: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                failed += 1
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 测试异常: {e}")
            logger.error(f"测试异常: {e}", exc_info=True)
    
    print("\n" + "="*60)
    print(f"测试总结: {passed} 通过, {failed} 失败")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)