#!/usr/bin/env python3
"""
全面验证RAG Agent功能，确保没有破坏原有功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
import time

def verify_rag_functionality():
    """验证RAG核心功能"""
    
    print("=== 全面验证RAG Agent功能 ===\n")
    
    results = {
        'initialization': False,
        'basic_query': False,
        'filtered_query': False,
        'error_handling': False,
        'stats_working': False,
        'stats_accurate': False
    }
    
    try:
        # 1. 测试初始化
        print("1. 测试初始化...")
        rag_agent = RAGAgent()
        results['initialization'] = True
        print("✓ 初始化成功")
        
        # 检查统计变量是否存在
        has_stats = hasattr(rag_agent, 'query_count') and hasattr(rag_agent, 'success_count')
        print(f"  - 统计功能: {'已启用' if has_stats else '未找到'}")
        
        if has_stats:
            print(f"  - 初始查询数: {rag_agent.query_count}")
            print(f"  - 初始成功数: {rag_agent.success_count}")
        
        # 2. 测试基本查询（无过滤）
        print("\n2. 测试基本查询（无过滤）...")
        result1 = rag_agent.query("贵州茅台")
        
        if result1.get('success'):
            results['basic_query'] = True
            print("✓ 基本查询成功")
            print(f"  - 文档数: {result1.get('document_count', 0)}")
            print(f"  - 答案长度: {len(result1.get('answer', ''))}")
        else:
            print(f"✗ 基本查询失败: {result1.get('error', '未知错误')}")
        
        # 检查统计是否更新
        if has_stats:
            print(f"  - 查询后统计: 总数={rag_agent.query_count}, 成功={rag_agent.success_count}")
            if rag_agent.query_count > 0:
                results['stats_working'] = True
        
        # 3. 测试带过滤的查询
        print("\n3. 测试带过滤的查询...")
        result2 = rag_agent.query(
            "分析财务状况",
            filters={"ts_code": "600519.SH"}
        )
        
        if result2.get('success'):
            results['filtered_query'] = True
            print("✓ 过滤查询成功")
            print(f"  - 文档数: {result2.get('document_count', 0)}")
            print(f"  - 处理时间: {result2.get('processing_time', 0):.2f}秒")
        else:
            print(f"✗ 过滤查询失败: {result2.get('error', '未知错误')}")
        
        # 再次检查统计
        if has_stats:
            print(f"  - 查询后统计: 总数={rag_agent.query_count}, 成功={rag_agent.success_count}")
        
        # 4. 测试错误处理
        print("\n4. 测试错误处理...")
        result3 = rag_agent.query("")  # 空查询应该失败
        
        if not result3.get('success'):
            results['error_handling'] = True
            print("✓ 错误处理正常")
            print(f"  - 错误信息: {result3.get('error', '')[:50]}...")
        else:
            print("✗ 错误处理异常：空查询应该失败")
        
        # 5. 验证统计准确性
        if has_stats:
            print("\n5. 验证统计准确性...")
            expected_total = 3  # 我们执行了3次查询
            expected_success = 2  # 2次应该成功
            
            print(f"  - 期望总数: {expected_total}, 实际: {rag_agent.query_count}")
            print(f"  - 期望成功: {expected_success}, 实际: {rag_agent.success_count}")
            
            if rag_agent.query_count == expected_total and rag_agent.success_count == expected_success:
                results['stats_accurate'] = True
                print("✓ 统计准确")
            else:
                print("✗ 统计不准确")
            
            # 测试get_stats方法
            if hasattr(rag_agent, 'get_stats'):
                stats = rag_agent.get_stats()
                print(f"  - 成功率: {stats.get('success_rate', 0)*100:.0f}%")
                print(f"  - 平均响应时间: {stats.get('avg_response_time', 0):.2f}秒")
        
        # 6. 测试原始功能
        print("\n6. 验证原始功能完整性...")
        
        # 测试_format_sources
        if hasattr(rag_agent, '_format_sources'):
            print("  ✓ _format_sources方法存在")
        
        # 测试_get_chat_history
        if hasattr(rag_agent, '_get_chat_history'):
            print("  ✓ _get_chat_history方法存在")
        
        # 测试memory
        if hasattr(rag_agent, 'memory'):
            print("  ✓ memory对象存在")
        
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. 生成报告
    print("\n" + "="*50)
    print("验证报告:")
    print("="*50)
    
    for key, value in results.items():
        status = "✓" if value else "✗"
        print(f"{status} {key.replace('_', ' ').title()}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n✅ 所有验证通过！可以安全提交。")
    elif passed >= total - 1:
        print("\n⚠️ 大部分功能正常，但有小问题需要注意。")
    else:
        print("\n❌ 存在严重问题，不建议提交。")
    
    return results

def diagnose_stats_issue():
    """诊断统计功能问题"""
    
    print("\n\n=== 诊断统计功能 ===\n")
    
    rag_agent_path = os.path.join("agents", "rag_agent.py")
    
    print("检查代码中的统计更新...")
    
    with open(rag_agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键代码
    checks = {
        "统计变量初始化": "self.query_count = 0",
        "成功更新代码": "self.query_count += 1",
        "get_stats方法": "def get_stats(self)",
        "统计在return之前": "self.success_count += 1"
    }
    
    for name, code in checks.items():
        if code in content:
            print(f"✓ {name}: 找到")
            
            # 找到代码位置并显示上下文
            pos = content.find(code)
            if pos != -1:
                start = max(0, content.rfind('\n', 0, pos-50))
                end = min(len(content), content.find('\n', pos+50))
                context = content[start:end].strip()
                print(f"  位置: 第{content[:pos].count(chr(10))+1}行")
        else:
            print(f"✗ {name}: 未找到")
    
    # 检查是否在正确的位置更新统计
    if "self.query_count += 1" in content:
        # 检查是否在return语句之前
        stats_pos = content.find("self.query_count += 1")
        return_pos = content.find("return {", stats_pos-200, stats_pos+200)
        
        if return_pos != -1 and return_pos > stats_pos:
            print("\n✓ 统计更新在return之前（正确）")
        else:
            print("\n✗ 统计更新可能在错误的位置")

if __name__ == "__main__":
    # 运行全面验证
    results = verify_rag_functionality()
    
    # 如果统计不工作，诊断问题
    if not results.get('stats_working'):
        diagnose_stats_issue()
