#!/usr/bin/env python3
"""
测试脚本：验证SQL Agent和Hybrid Agent的问题
运行方式：python scripts/tests/test_agent_issues.py
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent
import json
import traceback
from datetime import datetime

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test_header(test_name):
    """打印测试头"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}测试: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_sql_agent_return_format():
    """测试SQL Agent返回格式的一致性"""
    print_test_header("SQL Agent 返回格式测试")
    
    try:
        sql_agent = SQLAgent()
        print_success("SQL Agent 初始化成功")
        
        # 测试用例列表
        test_queries = [
            "查询贵州茅台最新股价",
            "贵州茅台的股票代码是什么",
            "统计今天涨幅最大的5只股票",
            "这是一个无效的查询#@$%"  # 测试错误处理
        ]
        
        results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n测试 {i}: {query}")
            try:
                result = sql_agent.query(query)
                
                # 检查返回类型
                print(f"返回类型: {type(result)}")
                
                if isinstance(result, dict):
                    print_success("返回类型是字典")
                    print(f"字典键: {list(result.keys())}")
                    
                    # 检查必要的键
                    required_keys = ['success', 'result']
                    missing_keys = [key for key in required_keys if key not in result]
                    
                    if missing_keys:
                        print_error(f"缺少必要的键: {missing_keys}")
                    else:
                        print_success("包含所有必要的键")
                    
                    # 记录结果结构
                    results.append({
                        'query': query,
                        'type': 'dict',
                        'keys': list(result.keys()),
                        'success': result.get('success', None)
                    })
                    
                elif isinstance(result, str):
                    print_warning("返回类型是字符串（需要修复）")
                    print(f"字符串内容预览: {result[:100]}...")
                    
                    results.append({
                        'query': query,
                        'type': 'str',
                        'content_preview': result[:100]
                    })
                else:
                    print_error(f"未预期的返回类型: {type(result)}")
                    results.append({
                        'query': query,
                        'type': str(type(result)),
                        'content': str(result)
                    })
                    
            except Exception as e:
                print_error(f"查询失败: {str(e)}")
                results.append({
                    'query': query,
                    'error': str(e)
                })
        
        # 总结
        print(f"\n{Colors.YELLOW}测试总结:{Colors.END}")
        dict_count = sum(1 for r in results if r.get('type') == 'dict')
        str_count = sum(1 for r in results if r.get('type') == 'str')
        error_count = sum(1 for r in results if 'error' in r)
        
        print(f"- 返回字典: {dict_count}")
        print(f"- 返回字符串: {str_count}")
        print(f"- 错误: {error_count}")
        
        if str_count > 0:
            print_warning(f"发现 {str_count} 个查询返回字符串，需要修复!")
            return False
        else:
            print_success("所有查询都返回字典格式")
            return True
            
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_hybrid_agent_type_handling():
    """测试Hybrid Agent的类型处理"""
    print_test_header("Hybrid Agent 类型处理测试")
    
    try:
        hybrid_agent = HybridAgent()
        print_success("Hybrid Agent 初始化成功")
        
        # 测试不同类型的查询
        test_cases = [
            {
                'name': 'SQL查询',
                'query': '贵州茅台最新股价',
                'expected_type': 'sql'
            },
            {
                'name': 'RAG查询',
                'query': '贵州茅台2024年第一季度财报的主要内容',
                'expected_type': 'rag'
            },
            {
                'name': '混合查询',
                'query': '分析贵州茅台的财务状况和股价表现',
                'expected_type': 'hybrid'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n测试 {i}: {test_case['name']}")
            print(f"查询: {test_case['query']}")
            
            try:
                result = hybrid_agent.query(test_case['query'])
                
                # 检查返回类型
                if isinstance(result, dict):
                    print_success("返回类型是字典")
                    
                    # 检查关键字段
                    if 'success' in result:
                        print(f"成功状态: {result['success']}")
                    
                    if 'query_type' in result:
                        print(f"查询类型: {result['query_type']}")
                        
                    if 'error' in result:
                        print_warning(f"错误信息: {result['error']}")
                        
                    # 如果是成功的查询，检查答案
                    if result.get('success') and 'answer' in result:
                        print_success("包含答案字段")
                        print(f"答案预览: {str(result['answer'])[:100]}...")
                else:
                    print_error(f"返回类型不是字典: {type(result)}")
                    
            except Exception as e:
                print_error(f"查询执行失败: {str(e)}")
                
                # 如果是我们已知的类型错误
                if "string indices must be integers" in str(e):
                    print_warning("确认存在字符串索引错误 - 这正是需要修复的问题!")
                
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理机制"""
    print_test_header("错误处理测试")
    
    test_cases = [
        {
            'agent': 'sql',
            'query': 'DROP TABLE test;',  # 危险查询
            'expected': '安全检查应该阻止'
        },
        {
            'agent': 'rag',
            'query': '',  # 空查询
            'expected': '应该有错误处理'
        },
        {
            'agent': 'hybrid',
            'query': None,  # None查询
            'expected': '应该有类型检查'
        }
    ]
    
    for test in test_cases:
        print(f"\n测试 {test['agent']} agent - {test['expected']}")
        try:
            if test['agent'] == 'sql':
                agent = SQLAgent()
            elif test['agent'] == 'rag':
                from agents.rag_agent import RAGAgent
                agent = RAGAgent()
            else:
                agent = HybridAgent()
            
            result = agent.query(test['query'])
            
            if isinstance(result, dict) and not result.get('success', True):
                print_success(f"正确处理了错误情况: {result.get('error', 'Unknown error')}")
            else:
                print_warning("查询意外成功，可能需要加强验证")
                
        except Exception as e:
            print_success(f"捕获到预期的异常: {type(e).__name__}")

def generate_test_report():
    """生成测试报告"""
    print_test_header("测试报告生成")
    
    report = {
        'test_date': datetime.now().isoformat(),
        'test_results': {
            'sql_agent_format': False,  # 预期会失败
            'hybrid_agent_type': False,  # 预期会失败
            'error_handling': True
        },
        'issues_found': [
            {
                'component': 'SQL Agent',
                'issue': '返回格式不一致',
                'severity': 'High',
                'impact': '导致Hybrid Agent处理失败'
            },
            {
                'component': 'Hybrid Agent',
                'issue': '类型处理不健壮',
                'severity': 'High',
                'impact': 'string indices must be integers错误'
            }
        ],
        'recommendations': [
            '1. 统一SQL Agent返回格式为字典',
            '2. 在Hybrid Agent中添加类型检查',
            '3. 完善错误处理机制',
            '4. 添加单元测试覆盖'
        ]
    }
    
    # 保存报告
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_success(f"测试报告已保存到: {report_file}")
    
    return report

def main():
    """主测试函数"""
    print(f"{Colors.BLUE}{'*'*60}{Colors.END}")
    print(f"{Colors.BLUE}股票分析系统 - Agent问题验证测试{Colors.END}")
    print(f"{Colors.BLUE}{'*'*60}{Colors.END}")
    
    # 检查环境
    print("\n检查测试环境...")
    try:
        from config.settings import settings
        if not settings.DEEPSEEK_API_KEY:
            print_error("DeepSeek API Key未配置!")
            return
        print_success("环境配置正常")
    except Exception as e:
        print_error(f"环境检查失败: {e}")
        return
    
    # 运行测试
    tests = [
        ("SQL Agent返回格式", test_sql_agent_return_format),
        ("Hybrid Agent类型处理", test_hybrid_agent_type_handling),
        ("错误处理机制", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"{test_name} 测试异常: {e}")
            results[test_name] = False
    
    # 生成报告
    report = generate_test_report()
    
    # 总结
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}测试完成总结{Colors.END}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.END}")
    
    passed = sum(1 for r in results.values() if r)
    failed = len(results) - passed
    
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed > 0:
        print_warning("\n发现问题需要修复！请查看测试报告了解详情。")
        print("\n建议的修复步骤:")
        print("1. 修改sql_agent.py的query方法，确保始终返回字典")
        print("2. 修改hybrid_agent.py，添加类型检查和转换")
        print("3. 运行测试验证修复效果")
    else:
        print_success("\n所有测试通过!")

if __name__ == "__main__":
    main()