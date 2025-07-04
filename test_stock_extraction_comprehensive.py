#!/usr/bin/env python3
"""
股票提取和验证逻辑综合测试脚本
========================================

功能说明：
    本脚本用于测试UnifiedStockValidator的所有股票识别和验证功能，
    确保系统能够正确处理各种股票输入格式，并给出准确的错误提示。

测试范围：
    1. 正确格式的股票代码、证券代码、股票名称
    2. 各种错误格式（大小写、长度、后缀等）
    3. 股票简称/昵称的处理
    4. 边界情况和特殊场景

使用方法：
    python test_stock_extraction_comprehensive.py
    
输出说明：
    - ✅ 表示测试通过
    - ❌ 表示测试失败
    - 最后会生成测试报告汇总

维护说明：
    当添加新的股票验证规则或错误类型时，请在相应的测试类别中添加测试用例。
    
作者：Stock Analysis System Team
版本：v1.0
更新日期：2025-07-05
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_stock_validator import UnifiedStockValidator
from utils.stock_code_mapper import convert_to_ts_code

class TestResult:
    """测试结果记录类"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = time.time()
        
    def add_success(self, test_name: str):
        """记录成功的测试"""
        self.total += 1
        self.passed += 1
        
    def add_failure(self, test_name: str, expected: str, actual: str):
        """记录失败的测试"""
        self.total += 1
        self.failed += 1
        self.errors.append({
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'time': datetime.now().isoformat()
        })
        
    def get_summary(self) -> Dict:
        """获取测试汇总"""
        duration = time.time() - self.start_time
        return {
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': f"{(self.passed/self.total*100):.1f}%" if self.total > 0 else "0%",
            'duration': f"{duration:.2f}秒",
            'errors': self.errors
        }


def test_stock_extraction_scenarios() -> TestResult:
    """
    测试各种股票提取场景
    
    测试说明：
        本函数测试UnifiedStockValidator的核心功能，包括：
        - 股票代码格式验证
        - 证券代码格式验证
        - 股票名称识别
        - 错误提示的准确性
    
    Returns:
        TestResult: 测试结果统计
    """
    
    # 测试用例结构：(输入, 预期结果类型, 预期值/错误信息)
    test_cases = [
        # ========== 1. 正确格式测试 ==========
        ("正确的证券代码格式", [
            ("600519.SH", "success", "600519.SH"),  # 沪市
            ("000001.SZ", "success", "000001.SZ"),  # 深市
            ("002047.SZ", "success", "002047.SZ"),  # 中小板
            ("300750.SZ", "success", "300750.SZ"),  # 创业板
            ("430047.BJ", "success", "430047.BJ"),  # 北交所
        ]),
        
        # ========== 2. 纯数字股票代码 ==========
        ("纯数字股票代码（应自动补充后缀）", [
            ("600519", "success", "600519.SH"),     # 应转为600519.SH
            ("000001", "success", "000001.SZ"),     # 应转为000001.SZ
            ("002047", "success", "002047.SZ"),     # 应转为002047.SZ
            ("300750", "success", "300750.SZ"),     # 应转为300750.SZ
            ("430047", "success", "430047.BJ"),     # 应转为430047.BJ
        ]),
        
        # ========== 3. 大小写错误 ==========
        ("证券代码大小写错误", [
            ("600519.sh", "error", "证券代码后缀大小写错误，应为.SH"),
            ("000001.sz", "error", "证券代码后缀大小写错误，应为.SZ"),
            ("430047.bj", "error", "证券代码后缀大小写错误，应为.BJ"),
            ("600519.Sh", "error", "证券代码后缀大小写错误，应为.SH"),
            ("600519.sH", "error", "证券代码后缀大小写错误，应为.SH"),
        ]),
        
        # ========== 4. 后缀错误 ==========
        ("证券代码后缀错误", [
            ("600519.SX", "error", "证券代码格式错误：后缀'SX'不正确，应为.SZ/.SH/.BJ"),
            ("600519.ZS", "error", "证券代码格式错误：后缀'ZS'不正确，应为.SZ/.SH/.BJ"),
            ("600519.HK", "error", "证券代码格式错误：后缀'HK'不正确，应为.SZ/.SH/.BJ"),
            ("600519.", "error", "证券代码格式错误：缺少后缀，应添加.SZ/.SH/.BJ"),
        ]),
        
        # ========== 5. 长度错误 ==========
        ("股票代码长度错误", [
            ("60051", "error", "股票代码应为6位数字，您输入了5位"),
            ("6005199", "error", "股票代码应为6位数字，您输入了7位"),
            ("123", "error", "股票代码应为6位数字，您输入了3位"),
            ("12345678", "error", "股票代码应为6位数字，您输入了8位"),
        ]),
        
        # ========== 6. 不存在的股票代码 ==========
        ("不存在的股票代码", [
            ("999999.SH", "error", "股票代码999999.SH不存在，请检查是否输入正确"),
            ("123456.SZ", "error", "股票代码123456.SZ不存在，请检查是否输入正确"),
        ]),
        
        # ========== 7. 完整股票名称 ==========
        ("完整股票名称", [
            ("贵州茅台", "success", "600519.SH"),
            ("平安银行", "success", "000001.SZ"),
            ("万科A", "success", "000002.SZ"),
            ("宁德时代", "success", "300750.SZ"),
            ("比亚迪", "success", "002594.SZ"),
            ("中国平安", "success", "601318.SH"),
            ("招商银行", "success", "600036.SH"),
            ("五粮液", "success", "000858.SZ"),
        ]),
        
        # ========== 8. 股票简称/昵称 ==========
        ("股票简称（应提示使用完整名称）", [
            ("茅台", "error", "请使用完整公司名称，如：贵州茅台"),
            ("平安", "error", "请使用完整公司名称，如：中国平安"),
            ("万科", "error", "请使用完整公司名称，如：万科A"),
            ("宁德", "error", "请使用完整公司名称，如：宁德时代"),
            ("招行", "error", "请使用完整公司名称，如：招商银行"),
            ("建行", "error", "请使用完整公司名称，如：建设银行"),
            ("工行", "error", "请使用完整公司名称，如：工商银行"),
            ("中行", "error", "请使用完整公司名称，如：中国银行"),
        ]),
        
        # ========== 9. 无效输入 ==========
        ("无效输入", [
            ("abc", "error", "无法识别输入内容"),
            ("股票", "error", "无法识别输入内容"),
            ("123", "error", "股票代码应为6位数字，您输入了3位"),
            ("", "error", "查询内容不能为空"),
            ("   ", "error", "查询内容不能为空"),
        ]),
        
        # ========== 10. 特殊格式（带后缀的名称） ==========
        ("带后缀的公司名称", [
            ("贵州茅台股份", "success", "600519.SH"),
            ("平安银行股份", "success", "000001.SZ"),
            ("中国平安保险", "success", "601318.SH"),
            ("宁德时代新能源", "success", "300750.SZ"),
            ("比亚迪汽车", "success", "002594.SZ"),
        ]),
    ]
    
    validator = UnifiedStockValidator()
    result = TestResult()
    
    print("=" * 80)
    print("股票提取和验证逻辑测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    for category, cases in test_cases:
        print(f"\n【{category}】")
        category_passed = 0
        category_total = 0
        
        for input_text, expected_type, expected_value in cases:
            category_total += 1
            success, ts_code, error_info = validator.validate_and_extract(input_text)
            
            if expected_type == "success":
                if success and ts_code == expected_value:
                    print(f"✅ '{input_text}' → {ts_code}")
                    result.add_success(f"{category}/{input_text}")
                    category_passed += 1
                else:
                    actual = ts_code if success else error_info.get('error', '未知错误')
                    print(f"❌ '{input_text}' → 预期: {expected_value}, 实际: {actual}")
                    result.add_failure(f"{category}/{input_text}", expected_value, actual)
            else:  # expected_type == "error"
                if not success:
                    actual_error = error_info.get('error', '')
                    if expected_value in actual_error:
                        print(f"✅ '{input_text}' → {actual_error}")
                        result.add_success(f"{category}/{input_text}")
                        category_passed += 1
                    else:
                        print(f"❌ '{input_text}' → 预期错误: {expected_value}, 实际错误: {actual_error}")
                        result.add_failure(f"{category}/{input_text}", f"包含'{expected_value}'的错误", actual_error)
                else:
                    print(f"❌ '{input_text}' → 预期失败但成功了: {ts_code}")
                    result.add_failure(f"{category}/{input_text}", "应该失败", f"成功: {ts_code}")
        
        # 显示类别统计
        print(f"  小计: {category_passed}/{category_total} 通过")
    
    return result


def test_stock_extraction_in_queries() -> TestResult:
    """
    测试在完整查询句子中的股票提取
    
    测试说明：
        模拟实际使用场景，测试在完整的查询语句中提取股票信息的能力。
        这些测试用例反映了用户实际的查询方式。
    
    业务场景：
        - 股价查询：用户询问股票价格
        - 财务分析：用户请求财务指标
        - 资金流向：用户查询主力资金
        
    Returns:
        TestResult: 测试结果统计
    """
    
    test_queries = [
        # ========== 基础查询格式 ==========
        ("基础查询格式", [
            ("贵州茅台最新股价", "600519.SH"),
            ("600519最新股价", "600519.SH"),
            ("600519.SH最新股价", "600519.SH"),
            ("查询平安银行的股价", "000001.SZ"),
            ("万科A今天的股价是多少", "000002.SZ"),
        ]),
        
        # ========== 带日期的查询 ==========
        ("带日期的查询", [
            ("贵州茅台昨天的股价", "600519.SH"),
            ("600519前天的股价", "600519.SH"),
            ("平安银行2025-07-04的股价", "000001.SZ"),
            ("万科A最近5天的股价", "000002.SZ"),
            ("中国平安上个月的股价", "601318.SH"),
        ]),
        
        # ========== 复杂查询格式 ==========
        ("复杂查询格式", [
            ("分析贵州茅台的财务状况", "600519.SH"),
            ("比亚迪的PE是多少", "002594.SZ"),
            ("宁德时代的市盈率", "300750.SZ"),
            ("查询招商银行的主力资金", "600036.SH"),
            ("五粮液的成交量如何", "000858.SZ"),
        ]),
        
        # ========== 错误格式应该被捕获 ==========
        ("错误格式检测", [
            ("600519.sh的股价", "大小写错误"),
            ("茅台的股价", "简称错误"),
            ("60051的股价", "长度错误"),
            ("999999.SH的股价", "不存在"),
        ]),
    ]
    
    validator = UnifiedStockValidator()
    result = TestResult()
    
    print("\n" + "=" * 80)
    print("完整查询中的股票提取测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    for category, queries in test_queries:
        print(f"\n【{category}】")
        category_passed = 0
        category_total = 0
        
        for query, expected in queries:
            category_total += 1
            # 使用extract_multiple_stocks模拟SQL Agent的第一层提取
            stocks = validator.extract_multiple_stocks(query)
            
            if "错误" in expected:
                # 预期应该提取失败或返回错误
                if not stocks:
                    print(f"✅ '{query}' → 正确识别为{expected}")
                    result.add_success(f"{category}/{query}")
                    category_passed += 1
                else:
                    print(f"❌ '{query}' → 应该识别错误，但提取到了: {stocks}")
                    result.add_failure(f"{category}/{query}", expected, f"提取到: {stocks}")
            else:
                # 预期应该成功提取
                if stocks and stocks[0] == expected:
                    print(f"✅ '{query}' → {stocks[0]}")
                    result.add_success(f"{category}/{query}")
                    category_passed += 1
                else:
                    actual = stocks[0] if stocks else "未提取到"
                    print(f"❌ '{query}' → 预期: {expected}, 实际: {actual}")
                    result.add_failure(f"{category}/{query}", expected, actual)
        
        print(f"  小计: {category_passed}/{category_total} 通过")
    
    return result


def test_edge_cases() -> TestResult:
    """
    测试边界情况
    
    测试说明：
        测试一些特殊和边界情况，确保系统的健壮性。
        
    边界场景：
        - 多股票提取：查询中包含多个股票
        - 数字干扰：查询中包含日期等数字
        - 特殊字符：括号、空格等特殊字符
        - 简称歧义：可能产生歧义的简称
        
    Returns:
        TestResult: 测试结果统计
    """
    
    edge_cases = [
        ("边界情况", [
            # 多个股票
            ("对比贵州茅台和五粮液", ["600519.SH", "000858.SZ"]),
            ("茅台、五粮液、泸州老窖", "应该失败"),  # 简称
            
            # 特殊分隔
            ("贵州茅台,平安银行", ["600519.SH", "000001.SZ"]),
            ("贵州茅台、中国平安", ["600519.SH", "601318.SH"]),
            ("贵州茅台与比亚迪", ["600519.SH", "002594.SZ"]),
            
            # 数字干扰
            ("贵州茅台2025年的财报", "600519.SH"),
            ("600519从2025-06-01到2025-07-01的K线", "600519.SH"),
            
            # 空格和标点
            ("贵州茅台 的股价", "600519.SH"),
            ("（贵州茅台）", "600519.SH"),
            ("【600519.SH】", "600519.SH"),
        ]),
    ]
    
    validator = UnifiedStockValidator()
    result = TestResult()
    
    print("\n" + "=" * 80)
    print("边界情况测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    for category, cases in edge_cases:
        print(f"\n【{category}】")
        category_passed = 0
        category_total = 0
        
        for query, expected in cases:
            category_total += 1
            stocks = validator.extract_multiple_stocks(query)
            
            if isinstance(expected, list):
                if stocks == expected:
                    print(f"✅ '{query}' → {stocks}")
                    result.add_success(f"{category}/{query}")
                    category_passed += 1
                else:
                    print(f"❌ '{query}' → 预期: {expected}, 实际: {stocks}")
                    result.add_failure(f"{category}/{query}", str(expected), str(stocks))
            elif "失败" in expected:
                if not stocks or len(stocks) == 0:
                    print(f"✅ '{query}' → 正确失败")
                    result.add_success(f"{category}/{query}")
                    category_passed += 1
                else:
                    print(f"❌ '{query}' → 应该失败但提取到: {stocks}")
                    result.add_failure(f"{category}/{query}", "应该失败", f"提取到: {stocks}")
            else:
                if stocks and stocks[0] == expected:
                    print(f"✅ '{query}' → {stocks[0]}")
                    result.add_success(f"{category}/{query}")
                    category_passed += 1
                else:
                    actual = stocks[0] if stocks else "未提取到"
                    print(f"❌ '{query}' → 预期: {expected}, 实际: {actual}")
                    result.add_failure(f"{category}/{query}", expected, actual)
        
        print(f"  小计: {category_passed}/{category_total} 通过")
    
    return result


def generate_test_report(results: List[Tuple[str, TestResult]]) -> str:
    """
    生成测试报告
    
    Args:
        results: [(测试名称, 测试结果), ...]
        
    Returns:
        str: 格式化的测试报告
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("股票提取和验证逻辑测试报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 汇总统计
    total_tests = sum(r.total for _, r in results)
    total_passed = sum(r.passed for _, r in results)
    total_failed = sum(r.failed for _, r in results)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    report_lines.append("【测试汇总】")
    report_lines.append(f"  总测试数: {total_tests}")
    report_lines.append(f"  通过数: {total_passed}")
    report_lines.append(f"  失败数: {total_failed}")
    report_lines.append(f"  通过率: {overall_pass_rate:.1f}%")
    report_lines.append("")
    
    # 各模块详情
    report_lines.append("【模块详情】")
    for test_name, result in results:
        summary = result.get_summary()
        report_lines.append(f"\n{test_name}:")
        report_lines.append(f"  测试数: {summary['total']}")
        report_lines.append(f"  通过率: {summary['pass_rate']}")
        report_lines.append(f"  耗时: {summary['duration']}")
        
        if summary['errors']:
            report_lines.append(f"  失败用例:")
            for error in summary['errors'][:5]:  # 只显示前5个错误
                report_lines.append(f"    - {error['test']}")
                report_lines.append(f"      预期: {error['expected']}")
                report_lines.append(f"      实际: {error['actual']}")
            if len(summary['errors']) > 5:
                report_lines.append(f"    ... 还有 {len(summary['errors']) - 5} 个错误")
    
    # 测试建议
    report_lines.append("\n【测试建议】")
    if overall_pass_rate == 100:
        report_lines.append("  ✅ 所有测试通过，系统运行正常！")
    elif overall_pass_rate >= 90:
        report_lines.append("  ⚠️  测试通过率较高，但仍有少量问题需要修复。")
    else:
        report_lines.append("  ❌ 测试通过率较低，建议优先修复失败的测试用例。")
    
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
        filename = f"test_report_stock_extraction_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n测试报告已保存到: {filename}")
    except Exception as e:
        print(f"\n保存测试报告失败: {e}")


if __name__ == "__main__":
    print("开始执行股票提取和验证逻辑测试...")
    print("=" * 80)
    
    # 收集所有测试结果
    test_results = []
    
    # 1. 基础验证测试
    print("\n[1/3] 执行基础验证测试...")
    result1 = test_stock_extraction_scenarios()
    test_results.append(("基础验证测试", result1))
    
    # 2. 查询句子测试
    print("\n[2/3] 执行查询句子测试...")
    result2 = test_stock_extraction_in_queries()
    test_results.append(("查询句子测试", result2))
    
    # 3. 边界情况测试
    print("\n[3/3] 执行边界情况测试...")
    result3 = test_edge_cases()
    test_results.append(("边界情况测试", result3))
    
    # 生成测试报告
    print("\n生成测试报告...")
    report = generate_test_report(test_results)
    
    # 显示报告
    print("\n" + report)
    
    # 保存报告
    save_test_report(report)
    
    print("\n测试完成！")