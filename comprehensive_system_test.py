#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合系统功能测试脚本
测试所有已开发功能的完整性和正确性
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger

# 测试结果统计
class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.response_times = []
        
    def add_success(self, test_name: str, response_time: float):
        self.total += 1
        self.passed += 1
        self.response_times.append(response_time)
        
    def add_failure(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def get_summary(self) -> Dict:
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": f"{(self.passed/self.total*100):.1f}%" if self.total > 0 else "0%",
            "avg_response_time": f"{avg_response_time:.2f}s",
            "errors": self.errors
        }

class ComprehensiveSystemTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = setup_logger("comprehensive_test")
        self.results = {
            "sql": TestResult(),
            "rag": TestResult(),
            "financial": TestResult(),
            "moneyflow": TestResult(),
            "hybrid": TestResult(),
            "websocket": TestResult(),
            "auxiliary": TestResult()
        }
        
    def log_test(self, category: str, test_name: str, status: str, details: str = ""):
        """记录测试日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{category.upper()}] {test_name}: {status}"
        if details:
            log_msg += f" - {details}"
        
        if status == "PASS":
            self.logger.info(log_msg)
        elif status == "FAIL":
            self.logger.error(log_msg)
        else:
            self.logger.warning(log_msg)
            
    async def test_api_health(self) -> bool:
        """测试API健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("auxiliary", "API健康检查", "PASS", 
                            f"MySQL: {data.get('mysql')}, Milvus: {data.get('milvus')}")
                return True
            else:
                self.log_test("auxiliary", "API健康检查", "FAIL", 
                            f"Status Code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("auxiliary", "API健康检查", "ERROR", str(e))
            return False
            
    async def test_sql_queries(self):
        """测试SQL查询功能"""
        test_cases = [
            ("贵州茅台最新股价", "实时股价查询"),
            ("A股市值排名前10", "市值排行查询"),
            ("今日涨幅最大的10只股票", "涨跌幅排行"),
            ("平安银行最近5日股价", "历史数据查询"),
            ("茅台最近一个月的平均成交量", "统计查询"),
            ("比较茅台和五粮液的市盈率", "对比查询")
        ]
        
        for query, test_name in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": "sql"},
                    timeout=60
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.results["sql"].add_success(test_name, response_time)
                        self.log_test("sql", test_name, "PASS", 
                                    f"响应时间: {response_time:.2f}s")
                    else:
                        self.results["sql"].add_failure(test_name, data.get("error", "Unknown error"))
                        self.log_test("sql", test_name, "FAIL", data.get("error"))
                else:
                    self.results["sql"].add_failure(test_name, f"HTTP {response.status_code}")
                    self.log_test("sql", test_name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["sql"].add_failure(test_name, str(e))
                self.log_test("sql", test_name, "ERROR", str(e))
                
    async def test_rag_queries(self):
        """测试RAG查询功能"""
        test_cases = [
            ("贵州茅台2024年第一季度营收情况", "季度报告查询"),
            ("分析茅台的高端化战略", "战略分析查询"),
            ("比较茅台和五粮液的毛利率", "财务指标对比"),
            ("诺德股份最新公告", "公告查询"),
            ("茅台的品牌价值分析", "定性分析查询")
        ]
        
        for query, test_name in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": "rag"},
                    timeout=60
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.results["rag"].add_success(test_name, response_time)
                        self.log_test("rag", test_name, "PASS", 
                                    f"响应时间: {response_time:.2f}s")
                    else:
                        self.results["rag"].add_failure(test_name, data.get("error", "Unknown error"))
                        self.log_test("rag", test_name, "FAIL", data.get("error"))
                else:
                    self.results["rag"].add_failure(test_name, f"HTTP {response.status_code}")
                    self.log_test("rag", test_name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["rag"].add_failure(test_name, str(e))
                self.log_test("rag", test_name, "ERROR", str(e))
                
    async def test_financial_analysis(self):
        """测试财务分析功能"""
        test_cases = [
            # 财务健康度分析
            ("分析贵州茅台的财务健康度", "财务健康度-茅台"),
            ("600036.SH的财务健康度评分", "财务健康度-招商银行"),
            
            # 杜邦分析
            ("平安银行杜邦分析", "杜邦分析-平安银行"),
            ("对茅台进行杜邦分析", "杜邦分析-茅台"),
            
            # 现金流质量分析
            ("万科现金流质量分析", "现金流分析-万科"),
            ("分析茅台的现金流质量", "现金流分析-茅台"),
            
            # 多期财务对比
            ("分析茅台的多期财务对比", "多期对比-茅台"),
            ("比较招商银行不同时期的财务数据", "多期对比-招商银行")
        ]
        
        for query, test_name in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": "financial"},
                    timeout=60
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.results["financial"].add_success(test_name, response_time)
                        self.log_test("financial", test_name, "PASS", 
                                    f"响应时间: {response_time:.2f}s")
                    else:
                        self.results["financial"].add_failure(test_name, data.get("error", "Unknown error"))
                        self.log_test("financial", test_name, "FAIL", data.get("error"))
                else:
                    self.results["financial"].add_failure(test_name, f"HTTP {response.status_code}")
                    self.log_test("financial", test_name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["financial"].add_failure(test_name, str(e))
                self.log_test("financial", test_name, "ERROR", str(e))
                
    async def test_moneyflow_analysis(self):
        """测试资金流向分析功能"""
        test_cases = [
            ("茅台最近30天资金流向", "单股资金流向"),
            ("对比茅台和五粮液资金流向", "多股资金对比"),
            ("分析茅台今日的主力资金动向", "当日资金分析"),
            ("茅台最近5天的超大单分析", "超大单分析")
        ]
        
        for query, test_name in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": "sql"},  # 资金流向通过SQL查询
                    timeout=60
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.results["moneyflow"].add_success(test_name, response_time)
                        self.log_test("moneyflow", test_name, "PASS", 
                                    f"响应时间: {response_time:.2f}s")
                    else:
                        self.results["moneyflow"].add_failure(test_name, data.get("error", "Unknown error"))
                        self.log_test("moneyflow", test_name, "FAIL", data.get("error"))
                else:
                    self.results["moneyflow"].add_failure(test_name, f"HTTP {response.status_code}")
                    self.log_test("moneyflow", test_name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["moneyflow"].add_failure(test_name, str(e))
                self.log_test("moneyflow", test_name, "ERROR", str(e))
                
    async def test_hybrid_queries(self):
        """测试混合查询功能"""
        test_cases = [
            ("分析贵州茅台的投资价值", "综合投资分析"),
            ("茅台的财务状况和股价表现如何", "财务+股价分析"),
            ("比较茅台和五粮液的综合实力", "多维度对比分析"),
            ("分析平安银行的业务发展和财务表现", "业务+财务分析")
        ]
        
        for query, test_name in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": "hybrid"},
                    timeout=90
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.results["hybrid"].add_success(test_name, response_time)
                        self.log_test("hybrid", test_name, "PASS", 
                                    f"响应时间: {response_time:.2f}s")
                    else:
                        self.results["hybrid"].add_failure(test_name, data.get("error", "Unknown error"))
                        self.log_test("hybrid", test_name, "FAIL", data.get("error"))
                else:
                    self.results["hybrid"].add_failure(test_name, f"HTTP {response.status_code}")
                    self.log_test("hybrid", test_name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["hybrid"].add_failure(test_name, str(e))
                self.log_test("hybrid", test_name, "ERROR", str(e))
                
    async def test_edge_cases(self):
        """测试边界情况和错误处理"""
        test_cases = [
            # 空查询测试
            ("", "空查询", "sql"),
            ("   ", "空白查询", "rag"),
            
            # 无效股票代码
            ("分析99999的财务健康度", "无效股票代码", "financial"),
            ("INVALID.XX的股价", "错误证券代码", "sql"),
            
            # 超长查询
            ("分析" + "茅台" * 100 + "的财务状况", "超长查询", "hybrid"),
            
            # 特殊字符
            ("分析<script>alert('test')</script>的股价", "XSS测试", "sql"),
            ("'; DROP TABLE stocks; --", "SQL注入测试", "sql")
        ]
        
        for query, test_name, query_type in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"question": query, "query_type": query_type},
                    timeout=30
                )
                response_time = time.time() - start_time
                
                # 对于边界测试，期望返回错误而不是崩溃
                if response.status_code in [200, 400, 422]:
                    self.results["auxiliary"].add_success(test_name, response_time)
                    self.log_test("auxiliary", test_name, "PASS", 
                                f"正确处理边界情况")
                else:
                    self.results["auxiliary"].add_failure(test_name, f"未预期的状态码: {response.status_code}")
                    self.log_test("auxiliary", test_name, "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results["auxiliary"].add_failure(test_name, str(e))
                self.log_test("auxiliary", test_name, "ERROR", str(e))
                
    async def test_websocket_functionality(self):
        """测试WebSocket功能"""
        import websockets
        
        try:
            uri = f"ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # 测试连接
                self.results["websocket"].add_success("WebSocket连接", 0.1)
                self.log_test("websocket", "WebSocket连接", "PASS")
                
                # 发送测试查询
                test_query = {
                    "type": "query",
                    "question": "茅台最新股价",
                    "id": 1
                }
                await websocket.send(json.dumps(test_query))
                
                # 接收响应
                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                data = json.loads(response)
                
                if data.get("type") in ["welcome", "processing", "analysis_result"]:
                    self.results["websocket"].add_success("WebSocket查询", 0.5)
                    self.log_test("websocket", "WebSocket查询", "PASS", 
                                f"响应类型: {data.get('type')}")
                else:
                    self.results["websocket"].add_failure("WebSocket查询", "未预期的响应类型")
                    self.log_test("websocket", "WebSocket查询", "FAIL", 
                                f"响应类型: {data.get('type')}")
                    
        except Exception as e:
            self.results["websocket"].add_failure("WebSocket功能", str(e))
            self.log_test("websocket", "WebSocket功能", "ERROR", str(e))
            
    def generate_test_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 80)
        report.append("股票分析系统综合测试报告")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # 总体统计
        total_tests = sum(r.total for r in self.results.values())
        total_passed = sum(r.passed for r in self.results.values())
        total_failed = sum(r.failed for r in self.results.values())
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.append("【总体测试结果】")
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过数: {total_passed}")
        report.append(f"失败数: {total_failed}")
        report.append(f"通过率: {overall_pass_rate:.1f}%")
        report.append("")
        
        # 各模块详细结果
        report.append("【模块测试详情】")
        module_names = {
            "sql": "SQL查询模块",
            "rag": "RAG查询模块",
            "financial": "财务分析模块",
            "moneyflow": "资金流向模块",
            "hybrid": "混合查询模块",
            "websocket": "WebSocket模块",
            "auxiliary": "辅助功能模块"
        }
        
        for module, name in module_names.items():
            if module in self.results:
                summary = self.results[module].get_summary()
                report.append(f"\n{name}:")
                report.append(f"  - 测试数: {summary['total']}")
                report.append(f"  - 通过数: {summary['passed']}")
                report.append(f"  - 失败数: {summary['failed']}")
                report.append(f"  - 通过率: {summary['pass_rate']}")
                if summary['avg_response_time'] != "0.00s":
                    report.append(f"  - 平均响应时间: {summary['avg_response_time']}")
                
                if summary['errors']:
                    report.append("  - 错误详情:")
                    for error in summary['errors']:
                        report.append(f"    * {error}")
        
        # 性能统计
        all_response_times = []
        for result in self.results.values():
            all_response_times.extend(result.response_times)
        
        if all_response_times:
            report.append("\n【性能统计】")
            report.append(f"最快响应: {min(all_response_times):.2f}s")
            report.append(f"最慢响应: {max(all_response_times):.2f}s")
            report.append(f"平均响应: {sum(all_response_times)/len(all_response_times):.2f}s")
        
        # 问题总结
        all_errors = []
        for result in self.results.values():
            all_errors.extend(result.errors)
        
        if all_errors:
            report.append("\n【发现的问题】")
            report.append("以下测试用例失败，需要进一步调查:")
            for i, error in enumerate(all_errors, 1):
                report.append(f"{i}. {error}")
        
        # 建议
        report.append("\n【测试建议】")
        if overall_pass_rate >= 95:
            report.append("✅ 系统整体运行良好，可以进行下一阶段开发")
        elif overall_pass_rate >= 80:
            report.append("⚠️ 系统基本功能正常，但存在一些问题需要修复")
        else:
            report.append("❌ 系统存在较多问题，建议优先修复后再继续开发")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始综合系统测试...")
        print("-" * 50)
        
        # 1. API健康检查
        print("1. 检查API健康状态...")
        if not await self.test_api_health():
            print("❌ API服务未启动，请先启动服务")
            return
        
        # 2. SQL查询测试
        print("\n2. 测试SQL查询功能...")
        await self.test_sql_queries()
        
        # 3. RAG查询测试
        print("\n3. 测试RAG查询功能...")
        await self.test_rag_queries()
        
        # 4. 财务分析测试
        print("\n4. 测试财务分析功能...")
        await self.test_financial_analysis()
        
        # 5. 资金流向测试
        print("\n5. 测试资金流向分析...")
        await self.test_moneyflow_analysis()
        
        # 6. 混合查询测试
        print("\n6. 测试混合查询功能...")
        await self.test_hybrid_queries()
        
        # 7. WebSocket测试
        print("\n7. 测试WebSocket功能...")
        await self.test_websocket_functionality()
        
        # 8. 边界测试
        print("\n8. 测试边界情况处理...")
        await self.test_edge_cases()
        
        # 生成报告
        print("\n" + "-" * 50)
        report = self.generate_test_report()
        print(report)
        
        # 保存报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n测试报告已保存到: {report_file}")

def main():
    """主函数"""
    tester = ComprehensiveSystemTest()
    
    # 运行异步测试
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main()