#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
排名查询快速路径综合测试
测试新增的财务指标排名模板
"""

import time
import sys
from datetime import datetime
from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent
from utils.query_templates import match_query_template
from utils.logger import setup_logger


# 设置测试超时时间为5分钟
TEST_TIMEOUT = 300  # 5分钟


def test_new_ranking_templates():
    """测试新增的财务排名模板"""
    
    print("=" * 80)
    print("财务指标排名查询快速路径测试")
    print(f"测试时间: {datetime.now()}")
    print(f"超时设置: {TEST_TIMEOUT}秒")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    logger = setup_logger("test_ranking")
    
    # 测试用例设计
    test_categories = {
        "PE排名测试": [
            ("PE最高的前10", "PE排名-最高前10"),
            ("市盈率排名前20", "PE排名-最高前20"), 
            ("PE最低的前10", "PE排名-最低前10"),
            ("PE排名", "PE排名-默认前10"),
            ("市盈率TOP5", "PE排名-TOP5格式"),
        ],
        
        "PB排名测试": [
            ("PB最低的前10", "PB排名-最低前10"),
            ("市净率排名前20", "PB排名-最高前20"),
            ("破净股排名", "PB排名-破净股"),
            ("PB最高的前5", "PB排名-最高前5"),
            ("市净率排行榜", "PB排名-默认前10"),
        ],
        
        "净利润排名测试": [
            ("利润排名前20", "净利润排名-前20"),
            ("净利润最高的前10", "净利润排名-最高前10"),
            ("亏损最多的前10", "净利润排名-亏损前10"),
            ("盈利排名", "净利润排名-默认前10"),
            ("净利润TOP30", "净利润排名-TOP30"),
        ],
        
        "营收排名测试": [
            ("营收排名前10", "营收排名-前10"),
            ("营业收入最高的前20", "营收排名-最高前20"),
            ("收入排名", "营收排名-默认前10"),
            ("营收TOP15", "营收排名-TOP15"),
            ("营业收入排行", "营收排名-排行榜"),
        ],
        
        "ROE排名测试": [
            ("ROE排名前10", "ROE排名-前10"),
            ("净资产收益率最高的前20", "ROE排名-最高前20"),
            ("ROE排行榜", "ROE排名-默认前10"),
            ("净资产收益率TOP5", "ROE排名-TOP5"),
            ("ROE最高的前15", "ROE排名-最高前15"),
        ]
    }
    
    # 统计结果
    total_tests = 0
    success_count = 0
    fail_count = 0
    performance_stats = {}
    
    # 执行测试
    for category, test_cases in test_categories.items():
        print(f"\n\n### {category}")
        print("-" * 60)
        
        category_stats = {
            "total": len(test_cases),
            "success": 0,
            "fail": 0,
            "avg_time": 0,
            "times": []
        }
        
        for query, description in test_cases:
            total_tests += 1
            print(f"\n{total_tests}. {description}")
            print(f"   查询: {query}")
            
            start_time = time.time()
            timeout_flag = False
            
            try:
                # 设置超时检查
                if time.time() - start_time > TEST_TIMEOUT:
                    timeout_flag = True
                    raise TimeoutError(f"测试超时（>{TEST_TIMEOUT}秒）")
                
                # 测试模板匹配
                template_match = match_query_template(query)
                if not template_match:
                    print("   ❌ 未匹配到模板")
                    fail_count += 1
                    category_stats["fail"] += 1
                    continue
                
                template, params = template_match
                print(f"   ✅ 匹配模板: {template.name}")
                
                # 测试快速路径
                result = sql_agent._try_quick_query(query)
                elapsed = time.time() - start_time
                
                if result and result.get('success'):
                    print(f"   ✅ 快速路径成功 - 耗时: {elapsed:.2f}秒")
                    success_count += 1
                    category_stats["success"] += 1
                    category_stats["times"].append(elapsed)
                    
                    # 显示结果预览
                    result_lines = result['result'].split('\n')
                    print("   结果预览:")
                    for line in result_lines[:5]:
                        if line.strip():
                            print(f"      {line}")
                    
                else:
                    print(f"   ❌ 快速路径失败 - 耗时: {elapsed:.2f}秒")
                    if result:
                        print(f"      错误: {result.get('error', '未知错误')}")
                    fail_count += 1
                    category_stats["fail"] += 1
                    
            except TimeoutError as e:
                print(f"   ❌ {e}")
                fail_count += 1
                category_stats["fail"] += 1
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"   ❌ 异常 - 耗时: {elapsed:.2f}秒")
                print(f"      错误: {str(e)[:100]}...")
                fail_count += 1
                category_stats["fail"] += 1
                logger.error(f"测试异常: {e}")
        
        # 计算类别平均时间
        if category_stats["times"]:
            category_stats["avg_time"] = sum(category_stats["times"]) / len(category_stats["times"])
        
        performance_stats[category] = category_stats
        
        # 类别小结
        print(f"\n{category}小结:")
        print(f"   总测试: {category_stats['total']}")
        print(f"   成功: {category_stats['success']}")
        print(f"   失败: {category_stats['fail']}")
        if category_stats["avg_time"] > 0:
            print(f"   平均耗时: {category_stats['avg_time']:.2f}秒")
    
    # 总体测试报告
    print("\n\n" + "=" * 80)
    print("测试报告总结")
    print("=" * 80)
    print(f"总测试用例: {total_tests}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/total_tests*100:.1f}%")
    
    print("\n各类别性能分析:")
    for category, stats in performance_stats.items():
        if stats["avg_time"] > 0:
            print(f"   {category}: 平均{stats['avg_time']:.2f}秒")
    
    return success_count, fail_count


def test_edge_cases():
    """测试边界情况和异常用例"""
    
    print("\n\n" + "=" * 80)
    print("边界情况和异常测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    edge_cases = [
        # 无效指标
        ("XYZ排名前10", "无效指标测试"),
        ("随机指标最高的前10", "不存在的指标"),
        
        # 参数边界
        ("PE排名前0", "limit为0"),
        ("PB排名前-5", "limit为负数"),
        ("ROE排名前1000", "limit过大"),
        
        # 混合查询
        ("PE和PB排名前10", "多指标混合"),
        
        # 特殊表达
        ("PE最最最高的前10", "重复修饰词"),
        ("昨天的今天的PE排名", "矛盾时间"),
    ]
    
    print("\n测试用例:")
    for query, case_type in edge_cases:
        print(f"\n- {case_type}: {query}")
        
        template_match = match_query_template(query)
        if template_match:
            template, params = template_match
            print(f"  ⚠️ 意外匹配到模板: {template.name}")
            print(f"  提取参数: {params}")
        else:
            print(f"  ✅ 正确拒绝（未匹配到模板）")


def test_performance_comparison():
    """对比快速路径与LLM路由的性能"""
    
    print("\n\n" + "=" * 80)
    print("性能对比测试（快速路径 vs LLM路由）")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    hybrid_agent = HybridAgent()
    
    # 选择典型查询进行对比
    test_queries = [
        "PE排名前10",
        "净利润最高的前20",
        "ROE排行榜"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        print("-" * 40)
        
        # 测试快速路径
        start_time = time.time()
        fast_result = sql_agent._try_quick_query(query)
        fast_time = time.time() - start_time
        
        if fast_result and fast_result.get('success'):
            print(f"快速路径: {fast_time:.2f}秒 ✅")
        else:
            print(f"快速路径: 失败")
            continue
        
        # 测试LLM路由（通过SQL Agent的正常query方法）
        start_time = time.time()
        try:
            # 强制不使用快速路径，直接调用agent
            llm_result = sql_agent.agent.invoke({"input": query})
            llm_time = time.time() - start_time
            print(f"LLM路由: {llm_time:.2f}秒")
            
            # 计算性能提升
            if llm_time > 0:
                speedup = llm_time / fast_time
                print(f"性能提升: {speedup:.1f}倍")
        except Exception as e:
            print(f"LLM路由: 失败 - {str(e)[:50]}...")


def main():
    """主测试函数"""
    start_time = time.time()
    
    try:
        # 1. 测试新增排名模板
        success, fail = test_new_ranking_templates()
        
        # 2. 测试边界情况
        test_edge_cases()
        
        # 3. 性能对比（可选，避免超时可注释）
        # test_performance_comparison()
        
        # 测试总耗时
        total_time = time.time() - start_time
        print(f"\n\n总测试耗时: {total_time:.2f}秒")
        
        # 判断是否通过
        if fail == 0:
            print("\n✅ 所有测试通过!")
            return 0
        else:
            print(f"\n⚠️ 有{fail}个测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 2
    except Exception as e:
        print(f"\n\n测试异常: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())