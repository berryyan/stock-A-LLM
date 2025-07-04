#!/usr/bin/env python3
"""
SQL模板股票提取功能测试脚本
========================================

功能说明：
    本脚本测试所有需要个股参数的SQL模板，验证统一的股票提取方法
    在各个模板中的表现，包括功能正确性和性能指标。

测试范围：
    1. 股价查询模板 - 查询个股最新或历史股价
    2. 成交量查询模板 - 查询个股成交量和成交额
    3. 估值指标查询模板 - 查询PE、PB等估值指标
    4. K线查询模板 - 查询个股K线数据
    5. 个股主力资金模板 - 查询个股资金流向
    6. 利润查询模板 - 查询个股财务利润数据
    7. 公告查询模板 - 查询个股公告列表

测试维度：
    - 功能测试：各种输入格式是否正确处理
    - 性能测试：记录每个查询的响应时间
    - 一致性测试：同一股票不同表达的一致性
    - 错误测试：错误信息的准确性

使用方法：
    python test_stock_templates_extraction.py
    
输出说明：
    - ✅ 表示测试通过
    - ❌ 表示测试失败
    - ⚠️ 表示异常或警告
    - 生成详细的测试报告，包含性能指标

维护说明：
    当添加新的SQL模板或修改现有模板时，请更新相应的测试用例。
    注意保持测试用例与实际业务场景的一致性。
    
作者：Stock Analysis System Team
版本：v1.0
更新日期：2025-07-05
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent


class TemplateTestResult:
    """模板测试结果记录类"""
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.performance_metrics = []  # 记录响应时间
        self.start_time = time.time()
        
    def add_success(self, query: str, response_time: float):
        """记录成功的测试"""
        self.total += 1
        self.passed += 1
        self.performance_metrics.append({
            'query': query,
            'response_time': response_time,
            'status': 'success'
        })
        
    def add_failure(self, query: str, expected: str, actual: str, response_time: float = 0):
        """记录失败的测试"""
        self.total += 1
        self.failed += 1
        self.errors.append({
            'query': query,
            'expected': expected,
            'actual': actual,
            'time': datetime.now().isoformat()
        })
        self.performance_metrics.append({
            'query': query,
            'response_time': response_time,
            'status': 'failed'
        })
        
    def get_summary(self) -> Dict:
        """获取测试汇总"""
        duration = time.time() - self.start_time
        avg_response_time = sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics) if self.performance_metrics else 0
        
        return {
            'template_name': self.template_name,
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': f"{(self.passed/self.total*100):.1f}%" if self.total > 0 else "0%",
            'duration': f"{duration:.2f}秒",
            'avg_response_time': f"{avg_response_time:.3f}秒",
            'errors': self.errors,
            'performance_metrics': self.performance_metrics
        }


def test_individual_stock_templates() -> List[TemplateTestResult]:
    """
    测试所有需要个股的SQL模板
    
    测试说明：
        每个模板都会测试以下场景：
        1. 正常格式查询（股票名称、代码、证券代码）
        2. 带日期的查询（如适用）
        3. 错误格式查询（简称、大小写错误等）
        4. 无股票的查询
    
    业务意义：
        确保用户使用各种查询方式时，系统都能正确识别股票并返回结果。
        记录性能指标，确保查询响应时间在可接受范围内。
    
    Returns:
        List[TemplateTestResult]: 各模板的测试结果
    """
    
    # 初始化SQL Agent
    agent = SQLAgent()
    
    # 定义测试用例：每个模板的各种查询格式
    template_tests = {
        "股价查询": [
            # 正常格式
            ("贵州茅台最新股价", True),
            ("600519最新股价", True),
            ("600519.SH的股价", True),
            ("平安银行今天的股价", True),
            ("万科A昨天的股价", True),
            
            # 错误格式
            ("茅台最新股价", False),  # 简称
            ("600519.sh的股价", False),  # 大小写
            ("60051的股价", False),  # 长度错误
            ("999999.SH的股价", False),  # 不存在
        ],
        
        "成交量查询": [
            # 正常格式
            ("贵州茅台的成交量", True),
            ("600519今天的成交量", True),
            ("平安银行的成交额", True),
            ("万科A昨天的成交量", True),
            ("中国平安最新成交额", True),
            
            # 带日期
            ("贵州茅台2025-07-04的成交量", True),
            ("600519前天的成交额", True),
            
            # 错误格式
            ("茅台的成交量", False),
            ("平安的成交额", False),
        ],
        
        "估值指标查询": [
            # 正常格式
            ("贵州茅台的市盈率", True),
            ("600519的PE", True),
            ("平安银行的市净率", True),
            ("万科A的PB", True),
            ("比亚迪的PE是多少", True),
            
            # 错误格式
            ("茅台的PE", False),
            ("600519.sh的市盈率", False),
        ],
        
        "K线查询": [
            # 正常格式
            ("贵州茅台最近10天的K线", True),
            ("600519最近30天的走势", True),
            ("平安银行前5天的K线", True),
            ("万科A本月的K线", True),
            
            # 日期范围
            ("贵州茅台2025-06-01至2025-06-30的K线", True),
            ("600519从6月1日到6月30日的K线", True),
            
            # 错误格式
            ("茅台的K线", False),
            ("最近10天的K线", False),  # 无股票
        ],
        
        "个股主力资金": [
            # 正常格式
            ("贵州茅台的主力资金", True),
            ("600519的主力资金", True),
            ("平安银行的主力净流入", True),
            ("万科A的主力净流出", True),
            
            # 带日期
            ("贵州茅台昨天的主力资金", True),
            ("600519今天的主力净流入", True),
            
            # 错误格式
            ("茅台的主力资金", False),
            ("主力资金", False),  # 无股票
        ],
        
        "利润查询": [
            # 正常格式
            ("贵州茅台的利润", True),
            ("600519的净利润", True),
            ("平安银行的营收", True),
            ("万科A的营业收入", True),
            
            # 带时间
            ("贵州茅台2024年的净利润", True),
            ("600519最新的营收", True),
            
            # 错误格式
            ("茅台的利润", False),
            ("利润", False),  # 无股票
        ],
        
        "公告查询": [
            # 正常格式
            ("贵州茅台最新公告", True),
            ("600519的公告", True),
            ("平安银行昨天的公告", True),
            ("万科A本月公告", True),
            
            # 日期范围
            ("贵州茅台6月到7月的公告", True),
            ("600519最近7天的公告", True),
            
            # 错误格式
            ("茅台的公告", False),
            ("最新公告", False),  # 无股票
        ],
    }
    
    print("=" * 80)
    print("SQL模板股票提取测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    # 测试每个模板
    for template_name, test_cases in template_tests.items():
        print(f"\n【{template_name}模板测试】")
        template_result = TemplateTestResult(template_name)
        
        for query, should_succeed in test_cases:
            start_time = time.time()
            
            try:
                # 调用SQL Agent的查询方法
                result = agent.query(query)
                response_time = time.time() - start_time
                
                # 检查结果
                if should_succeed:
                    if result.get('success'):
                        print(f"✅ '{query}' → 成功 ({response_time:.3f}秒)")
                        template_result.add_success(query, response_time)
                    else:
                        error = result.get('error', '未知错误')
                        print(f"❌ '{query}' → 应该成功但失败了: {error}")
                        template_result.add_failure(query, "成功", f"失败: {error}", response_time)
                else:
                    if not result.get('success'):
                        error = result.get('error', '错误')
                        print(f"✅ '{query}' → 正确失败: {error} ({response_time:.3f}秒)")
                        template_result.add_success(query, response_time)
                    else:
                        print(f"❌ '{query}' → 应该失败但成功了")
                        template_result.add_failure(query, "失败", "成功", response_time)
                        
            except Exception as e:
                response_time = time.time() - start_time
                print(f"⚠️ '{query}' → 异常: {str(e)}")
                template_result.add_failure(query, "正常执行", f"异常: {str(e)}", response_time)
        
        # 显示模板统计
        summary = template_result.get_summary()
        print(f"\n小计: {summary['passed']}/{summary['total']} 通过")
        print(f"平均响应时间: {summary['avg_response_time']}")
        
        results.append(template_result)
    
    return results


def test_stock_extraction_consistency() -> TemplateTestResult:
    """
    测试股票提取的一致性
    
    测试说明：
        验证同一只股票的不同表达方式（名称、代码、证券代码）
        在不同模板中是否都能被正确识别。
        
    业务意义：
        确保用户无论使用哪种方式表达股票，系统都能给出一致的结果，
        避免因输入格式不同而导致的查询失败。
    
    Returns:
        TemplateTestResult: 一致性测试结果
    """
    
    agent = SQLAgent()
    result = TemplateTestResult("股票提取一致性测试")
    
    # 同一只股票的不同表达方式，应该都能正确识别
    stock_variations = {
        "贵州茅台": [
            "贵州茅台",
            "600519",
            "600519.SH",
            "贵州茅台股份",
        ],
        "平安银行": [
            "平安银行",
            "000001",
            "000001.SZ",
            "平安银行股份",
        ],
        "万科A": [
            "万科A",
            "000002",
            "000002.SZ",
        ],
    }
    
    print("\n" + "=" * 80)
    print("股票提取一致性测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试每个股票的不同表达在不同模板中的一致性
    templates = ["最新股价", "的成交量", "的PE", "最近5天的K线", "的主力资金"]
    
    for stock_name, variations in stock_variations.items():
        print(f"\n【{stock_name}的一致性测试】")
        
        for template_suffix in templates:
            variation_results = []
            times = []
            
            for variation in variations:
                query = f"{variation}{template_suffix}"
                start_time = time.time()
                
                try:
                    query_result = agent.query(query)
                    response_time = time.time() - start_time
                    times.append(response_time)
                    
                    if query_result.get('success'):
                        variation_results.append("成功")
                    else:
                        variation_results.append(f"失败: {query_result.get('error', '未知')}")
                except Exception as e:
                    response_time = time.time() - start_time
                    times.append(response_time)
                    variation_results.append(f"异常: {str(e)}")
            
            # 检查一致性
            avg_time = sum(times) / len(times) if times else 0
            test_name = f"{stock_name}/{template_suffix}"
            
            if all(r == "成功" for r in variation_results):
                print(f"✅ {template_suffix}: 所有变体都成功 (平均{avg_time:.3f}秒)")
                result.add_success(test_name, avg_time)
            else:
                print(f"❌ {template_suffix}: 不一致")
                for i, (var, res) in enumerate(zip(variations, variation_results)):
                    if res != "成功":
                        print(f"   - '{var}' → {res}")
                result.add_failure(test_name, "所有变体成功", f"部分失败: {variation_results}", avg_time)
    
    return result


def test_error_messages() -> TemplateTestResult:
    """
    测试错误信息的准确性
    
    测试说明：
        验证系统对各种错误输入的处理能力，确保返回的错误信息准确、
        有助于用户理解和修正错误。
    
    测试场景：
        1. 大小写错误 - 证券代码后缀大小写不正确
        2. 简称错误 - 使用股票简称而非完整名称
        3. 长度错误 - 股票代码位数不正确
        4. 存在性错误 - 不存在的股票代码
        5. 格式错误 - 错误的后缀或格式
        6. 空查询错误 - 缺少股票信息
    
    业务意义：
        良好的错误提示可以帮助用户快速理解问题所在，提升用户体验。
        
    Returns:
        TemplateTestResult: 错误测试结果
    """
    
    agent = SQLAgent()
    result = TemplateTestResult("错误信息准确性测试")
    
    # 定义错误测试用例：(查询, 预期错误关键词, 错误类型说明)
    error_test_cases = [
        # 大小写错误
        ("600519.sh最新股价", "大小写错误", "证券代码后缀大小写错误"),
        ("000001.sz的成交量", "大小写错误", "证券代码后缀大小写错误"),
        ("300750.sZ的PE", "大小写错误", "证券代码后缀大小写错误"),
        
        # 简称错误
        ("茅台最新股价", "请使用完整公司名称", "使用了股票简称"),
        ("平安的成交量", "请使用完整公司名称", "使用了股票简称"),
        ("万科的市盈率", "请使用完整公司名称", "使用了股票简称"),
        
        # 长度错误
        ("60051最新股价", "股票代码应为6位数字", "股票代码长度不足"),
        ("6005199的成交量", "股票代码应为6位数字", "股票代码长度超出"),
        ("123的PE", "股票代码应为6位数字", "股票代码长度错误"),
        
        # 存在性错误
        ("999999.SH最新股价", "不存在", "股票代码不存在"),
        ("123456.SZ的成交量", "不存在", "股票代码不存在"),
        
        # 格式错误
        ("600519.SX最新股价", "后缀", "错误的交易所后缀"),
        ("600519.的股价", "缺少后缀", "证券代码缺少后缀"),
        
        # 空查询错误
        ("最新股价", "未找到股票", "查询中没有股票信息"),
        ("成交量", "未找到股票", "查询中没有股票信息"),
        ("主力资金", "未找到股票", "查询中没有股票信息"),
    ]
    
    print("\n" + "=" * 80)
    print("错误信息准确性测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    for query, expected_error, error_type_desc in error_test_cases:
        start_time = time.time()
        
        try:
            # 调用SQL Agent
            query_result = agent.query(query)
            response_time = time.time() - start_time
            
            if not query_result.get('success'):
                error_msg = query_result.get('error', '')
                # 检查错误信息是否包含预期的关键词
                if expected_error in error_msg:
                    print(f"✅ '{query}' → {error_msg} ({response_time:.3f}秒)")
                    result.add_success(query, response_time)
                else:
                    print(f"❌ '{query}' → 预期包含'{expected_error}'，实际: {error_msg}")
                    result.add_failure(query, f"包含'{expected_error}'", error_msg, response_time)
            else:
                print(f"❌ '{query}' → 应该失败但成功了")
                result.add_failure(query, "应该失败", "成功执行", response_time)
                
        except Exception as e:
            response_time = time.time() - start_time
            print(f"⚠️ '{query}' → 异常: {str(e)}")
            result.add_failure(query, "正常错误", f"异常: {str(e)}", response_time)
    
    # 显示统计
    summary = result.get_summary()
    print(f"\n错误测试统计: {summary['passed']}/{summary['total']} 通过")
    print(f"平均响应时间: {summary['avg_response_time']}")
    
    return result


def generate_test_report(results: List[Tuple[str, TemplateTestResult]]) -> str:
    """
    生成综合测试报告
    
    Args:
        results: [(测试名称, 测试结果), ...]
        
    Returns:
        str: 格式化的测试报告
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("SQL模板股票提取功能测试报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 汇总统计
    total_templates = len(results)
    total_tests = sum(r.total for _, r in results)
    total_passed = sum(r.passed for _, r in results)
    total_failed = sum(r.failed for _, r in results)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # 计算总耗时和平均响应时间
    total_duration = sum(time.time() - r.start_time for _, r in results)
    all_response_times = []
    for _, result in results:
        all_response_times.extend([m['response_time'] for m in result.performance_metrics])
    avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
    
    report_lines.append("【测试汇总】")
    report_lines.append(f"  测试模块数: {total_templates}")
    report_lines.append(f"  总测试数: {total_tests}")
    report_lines.append(f"  通过数: {total_passed}")
    report_lines.append(f"  失败数: {total_failed}")
    report_lines.append(f"  通过率: {overall_pass_rate:.1f}%")
    report_lines.append(f"  总耗时: {total_duration:.2f}秒")
    report_lines.append(f"  平均响应时间: {avg_response_time:.3f}秒")
    report_lines.append("")
    
    # 性能分析
    report_lines.append("【性能分析】")
    
    # 找出响应最快和最慢的查询
    all_metrics = []
    for test_name, result in results:
        for metric in result.performance_metrics:
            all_metrics.append({
                'module': test_name,
                'query': metric['query'],
                'response_time': metric['response_time'],
                'status': metric['status']
            })
    
    if all_metrics:
        sorted_metrics = sorted(all_metrics, key=lambda x: x['response_time'])
        
        report_lines.append("\n  最快的5个查询:")
        for metric in sorted_metrics[:5]:
            report_lines.append(f"    - {metric['query'][:40]:40} {metric['response_time']:.3f}秒")
        
        report_lines.append("\n  最慢的5个查询:")
        for metric in sorted_metrics[-5:]:
            report_lines.append(f"    - {metric['query'][:40]:40} {metric['response_time']:.3f}秒")
    
    report_lines.append("")
    
    # 各模块详情
    report_lines.append("【模块详情】")
    
    # 按模板分组的结果
    template_results = {}
    
    for test_name, result in results:
        summary = result.get_summary()
        
        if "个股模板测试" in test_name:
            # 展开各个模板的详细结果
            for metric in result.performance_metrics:
                # 从查询中提取模板名称
                template_name = None
                if "股价" in metric['query'] and "成交" not in metric['query']:
                    template_name = "股价查询"
                elif "成交量" in metric['query'] or "成交额" in metric['query']:
                    template_name = "成交量查询"
                elif "PE" in metric['query'] or "市盈率" in metric['query'] or "PB" in metric['query'] or "市净率" in metric['query']:
                    template_name = "估值指标查询"
                elif "K线" in metric['query'] or "走势" in metric['query']:
                    template_name = "K线查询"
                elif "主力资金" in metric['query'] or "主力净流入" in metric['query'] or "主力净流出" in metric['query']:
                    template_name = "个股主力资金"
                elif "利润" in metric['query'] or "营收" in metric['query'] or "营业收入" in metric['query']:
                    template_name = "利润查询"
                elif "公告" in metric['query']:
                    template_name = "公告查询"
                
                if template_name:
                    if template_name not in template_results:
                        template_results[template_name] = {
                            'total': 0,
                            'passed': 0,
                            'failed': 0,
                            'response_times': []
                        }
                    
                    template_results[template_name]['total'] += 1
                    if metric['status'] == 'success':
                        template_results[template_name]['passed'] += 1
                    else:
                        template_results[template_name]['failed'] += 1
                    template_results[template_name]['response_times'].append(metric['response_time'])
        
        # 显示整体测试结果
        report_lines.append(f"\n{test_name}:")
        report_lines.append(f"  测试数: {summary['total']}")
        report_lines.append(f"  通过率: {summary['pass_rate']}")
        report_lines.append(f"  平均响应时间: {summary['avg_response_time']}")
        report_lines.append(f"  耗时: {summary['duration']}")
        
        if summary['errors'] and len(summary['errors']) > 0:
            report_lines.append(f"  失败用例:")
            for error in summary['errors'][:3]:  # 只显示前3个错误
                report_lines.append(f"    - {error.get('query', error.get('test', '未知查询'))}")
                report_lines.append(f"      预期: {error['expected']}")
                report_lines.append(f"      实际: {error['actual']}")
            if len(summary['errors']) > 3:
                report_lines.append(f"    ... 还有 {len(summary['errors']) - 3} 个错误")
    
    # 显示按模板分组的统计
    if template_results:
        report_lines.append("\n【模板性能统计】")
        for template_name, stats in sorted(template_results.items()):
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_time = sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
            report_lines.append(f"\n  {template_name}:")
            report_lines.append(f"    测试数: {stats['total']}")
            report_lines.append(f"    通过率: {pass_rate:.1f}%")
            report_lines.append(f"    平均响应时间: {avg_time:.3f}秒")
    
    # 测试建议
    report_lines.append("\n【测试建议】")
    if overall_pass_rate == 100:
        report_lines.append("  ✅ 所有测试通过，股票提取功能运行正常！")
    elif overall_pass_rate >= 90:
        report_lines.append("  ⚠️  测试通过率较高，但仍有少量问题需要关注。")
        report_lines.append("  建议重点检查失败的测试用例，特别是高频使用的模板。")
    else:
        report_lines.append("  ❌ 测试通过率较低，建议优先修复失败的测试用例。")
        report_lines.append("  重点关注：股票代码格式验证、错误提示准确性。")
    
    # 性能建议
    if avg_response_time > 1.0:
        report_lines.append("\n  ⚠️  平均响应时间较长，建议优化：")
        report_lines.append("     - 检查数据库查询性能")
        report_lines.append("     - 优化LLM调用策略")
        report_lines.append("     - 考虑增加缓存机制")
    
    report_lines.append("\n" + "=" * 80)
    
    return "\n".join(report_lines)


def save_test_report(report: str, filename: str = None):
    """
    保存测试报告到文件
    
    Args:
        report: 测试报告内容
        filename: 文件名（默认使用时间戳）
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_report_sql_templates_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n测试报告已保存到: {filename}")
    except Exception as e:
        print(f"\n保存测试报告失败: {e}")


def main():
    """
    主测试函数
    
    执行所有测试并生成综合报告
    """
    
    print("开始SQL模板股票提取功能测试...")
    print("=" * 80)
    
    # 收集所有测试结果
    test_results = []
    
    # 1. 测试各个模板
    print("\n[1/3] 执行个股模板测试...")
    template_results = test_individual_stock_templates()
    test_results.extend([("个股模板测试", r) for r in template_results])
    
    # 2. 测试一致性
    print("\n[2/3] 执行股票提取一致性测试...")
    consistency_result = test_stock_extraction_consistency()
    test_results.append(("股票提取一致性测试", consistency_result))
    
    # 3. 测试错误信息
    print("\n[3/3] 执行错误信息准确性测试...")
    error_result = test_error_messages()
    test_results.append(("错误信息准确性测试", error_result))
    
    # 生成测试报告
    print("\n生成测试报告...")
    report = generate_test_report(test_results)
    
    # 显示报告
    print("\n" + report)
    
    # 保存报告
    save_test_report(report)
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()