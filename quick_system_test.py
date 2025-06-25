#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速系统功能测试脚本
用于快速验证系统核心功能是否正常运行
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

class QuickSystemTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def print_header(self, text: str):
        """打印测试头"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
        
    def print_test(self, name: str, status: str, details: str = ""):
        """打印测试结果"""
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {name}: {status}")
        if details:
            print(f"   └─ {details}")
        
        self.test_results.append({
            "name": name,
            "status": status,
            "details": details
        })
        
    def test_api_health(self) -> bool:
        """测试API健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test("API健康检查", "PASS", 
                              f"MySQL: {data.get('mysql')}, Milvus: {data.get('milvus')}")
                return True
            else:
                self.print_test("API健康检查", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("API健康检查", "FAIL", str(e))
            return False
            
    def test_query(self, query: str, query_type: str, test_name: str, expected_keywords: List[str] = None):
        """测试单个查询"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/query",
                json={"question": query, "query_type": query_type},
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 检查预期关键词
                    content = str(data.get("answer", "")) + str(data.get("content", ""))
                    keywords_found = []
                    if expected_keywords:
                        keywords_found = [kw for kw in expected_keywords if kw in content]
                    
                    details = f"响应时间: {response_time:.1f}s"
                    if expected_keywords:
                        details += f", 关键词: {len(keywords_found)}/{len(expected_keywords)}"
                    
                    self.print_test(test_name, "PASS", details)
                else:
                    self.print_test(test_name, "FAIL", data.get("error", "Unknown error"))
            else:
                self.print_test(test_name, "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.print_test(test_name, "FAIL", str(e))
            
    def run_tests(self):
        """运行所有测试"""
        print("\n🚀 股票分析系统快速功能测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.base_url}")
        
        # 1. API健康检查
        self.print_header("1. 系统健康检查")
        if not self.test_api_health():
            print("\n⚠️  API服务未正常运行，请先启动服务:")
            print("   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
            return
            
        # 2. SQL查询功能
        self.print_header("2. SQL查询功能测试")
        self.test_query(
            "贵州茅台最新股价",
            "sql",
            "股价查询",
            ["600519", "茅台"]
        )
        self.test_query(
            "A股市值排名前5",
            "sql",
            "排行查询",
            ["排名", "市值"]
        )
        
        # 3. RAG查询功能
        self.print_header("3. RAG文档查询测试")
        self.test_query(
            "贵州茅台最新公告",
            "rag",
            "公告查询",
            ["茅台", "公告"]
        )
        self.test_query(
            "分析茅台的竞争优势",
            "rag",
            "定性分析",
            ["茅台"]
        )
        
        # 4. 财务分析功能
        self.print_header("4. 财务分析功能测试")
        self.test_query(
            "分析贵州茅台的财务健康度",
            "financial",
            "财务健康度",
            ["健康度", "评分"]
        )
        self.test_query(
            "茅台的杜邦分析",
            "financial",
            "杜邦分析",
            ["ROE"]
        )
        
        # 5. 混合查询功能
        self.print_header("5. 混合查询功能测试")
        self.test_query(
            "分析茅台的投资价值",
            "hybrid",
            "综合分析",
            ["茅台", "投资"]
        )
        
        # 6. 智能日期解析
        self.print_header("6. 智能日期解析测试")
        self.test_query(
            "茅台现在的股价",
            "sql",
            "智能时间识别",
            ["600519"]
        )
        
        # 7. 股票代码映射
        self.print_header("7. 股票代码映射测试")
        self.test_query(
            "诺德股份最新股价",
            "sql",
            "名称映射",
            ["600110"]
        )
        
        # 打印测试总结
        self.print_summary()
        
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"通过率: {pass_rate:.1f}%")
        
        if failed > 0:
            print(f"\n失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['name']}: {result['details']}")
                    
        if pass_rate >= 90:
            print("\n✅ 系统核心功能运行正常！")
        elif pass_rate >= 70:
            print("\n⚠️  系统基本可用，但存在一些问题需要修复")
        else:
            print("\n❌ 系统存在较多问题，请检查日志并修复")

def main():
    """主函数"""
    tester = QuickSystemTest()
    tester.run_tests()

if __name__ == "__main__":
    main()