#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主测试运行器 - 所有Agent
执行所有5个Agent的综合测试套件并生成汇总报告
"""
import subprocess
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any


class MasterTestRunner:
    """主测试运行器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.agents = [
            {
                "name": "SQL Agent",
                "script": "test_sql_agent_comprehensive.py",
                "result_file": "sql_agent_comprehensive_results.json"
            },
            {
                "name": "RAG Agent", 
                "script": "test_rag_agent_comprehensive.py",
                "result_file": "rag_agent_comprehensive_results.json"
            },
            {
                "name": "Financial Agent",
                "script": "test_financial_agent_comprehensive.py", 
                "result_file": "financial_agent_comprehensive_results.json"
            },
            {
                "name": "Money Flow Agent",
                "script": "test_money_flow_agent_comprehensive.py",
                "result_file": "money_flow_agent_comprehensive_results.json"
            },
            {
                "name": "Hybrid Agent",
                "script": "test_hybrid_agent_comprehensive.py",
                "result_file": "hybrid_agent_comprehensive_results.json"
            }
        ]
        self.overall_results = {
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "agents": {},
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "duration": None
        }
        
    def run_agent_tests(self, agent_info: Dict[str, str]) -> Dict[str, Any]:
        """运行单个Agent的测试"""
        print(f"\n{'='*80}")
        print(f"开始测试: {agent_info['name']}")
        print(f"测试脚本: {agent_info['script']}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*80)
        
        start_time = time.time()
        
        try:
            # 运行测试脚本
            result = subprocess.run(
                [sys.executable, agent_info['script']],
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            elapsed = time.time() - start_time
            
            # 读取测试结果
            if os.path.exists(agent_info['result_file']):
                with open(agent_info['result_file'], 'r', encoding='utf-8') as f:
                    test_results = json.load(f)
                    
                return {
                    "success": True,
                    "elapsed": elapsed,
                    "results": test_results,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "elapsed": elapsed,
                    "error": "结果文件未生成",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "elapsed": elapsed,
                "error": "测试超时（30分钟）"
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "elapsed": elapsed,
                "error": str(e)
            }
            
    def analyze_results(self):
        """分析所有测试结果"""
        print(f"\n{'='*80}")
        print("所有Agent测试汇总")
        print('='*80)
        
        # 按Agent打印详细结果
        print("\n按Agent分类的测试结果:")
        print("-"*80)
        print(f"{'Agent':<20} {'总计':<10} {'通过':<10} {'失败':<10} {'通过率':<10} {'耗时':<10}")
        print("-"*80)
        
        for agent_name, agent_data in self.overall_results["agents"].items():
            if agent_data.get("success", False) and "results" in agent_data:
                results = agent_data["results"]
                total = results["total"]
                passed = results["passed"]
                failed = results["failed"]
                pass_rate = f"{passed/total*100:.1f}%" if total > 0 else "0%"
                elapsed = f"{agent_data['elapsed']:.1f}s"
            else:
                total = passed = failed = 0
                pass_rate = "N/A"
                elapsed = f"{agent_data.get('elapsed', 0):.1f}s"
                
            print(f"{agent_name:<20} {total:<10} {passed:<10} {failed:<10} {pass_rate:<10} {elapsed:<10}")
            
        # 打印总体统计
        print("\n" + "="*80)
        print("整体测试统计")
        print("="*80)
        print(f"Agent数量: {len(self.agents)}")
        print(f"总测试用例数: {self.overall_results['total_tests']}")
        print(f"总通过数: {self.overall_results['total_passed']}")
        print(f"总失败数: {self.overall_results['total_failed']}")
        if self.overall_results['total_tests'] > 0:
            overall_pass_rate = self.overall_results['total_passed'] / self.overall_results['total_tests'] * 100
            print(f"整体通过率: {overall_pass_rate:.1f}%")
        print(f"总耗时: {self.overall_results['duration']:.2f}秒")
        
        # 失败测试详情
        if self.overall_results['total_failed'] > 0:
            print("\n" + "="*80)
            print("失败测试详情")
            print("="*80)
            
            for agent_name, agent_data in self.overall_results["agents"].items():
                if agent_data.get("success", False) and "results" in agent_data:
                    results = agent_data["results"]
                    if results["failed"] > 0:
                        print(f"\n{agent_name} 失败的测试:")
                        print("-"*40)
                        
                        # 统计失败的功能
                        for func_name, func_stats in results["functions"].items():
                            if func_stats["failed"] > 0:
                                print(f"  - {func_name}: {func_stats['failed']} 失败")
                                
        # Agent执行错误
        print("\n" + "="*80)
        print("Agent执行状态")
        print("="*80)
        
        for agent_name, agent_data in self.overall_results["agents"].items():
            if not agent_data.get("success", False):
                print(f"❌ {agent_name}: {agent_data.get('error', '未知错误')}")
            else:
                print(f"✅ {agent_name}: 测试执行成功")
                
    def save_overall_results(self):
        """保存整体测试结果"""
        with open("all_agents_comprehensive_results.json", "w", encoding="utf-8") as f:
            json.dump(self.overall_results, f, ensure_ascii=False, indent=2)
        print(f"\n整体测试结果已保存至: all_agents_comprehensive_results.json")
        
    def run_all_tests(self):
        """运行所有Agent测试"""
        print("所有Agent综合测试套件")
        print("="*80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试配置: {len(self.agents)} 个Agent，预计400+测试用例")
        print(f"预计耗时: 20-30分钟")
        
        # 运行每个Agent的测试
        for agent_info in self.agents:
            agent_result = self.run_agent_tests(agent_info)
            self.overall_results["agents"][agent_info["name"]] = agent_result
            
            # 更新总体统计
            if agent_result.get("success", False) and "results" in agent_result:
                results = agent_result["results"]
                self.overall_results["total_tests"] += results["total"]
                self.overall_results["total_passed"] += results["passed"]
                self.overall_results["total_failed"] += results["failed"]
                
        # 记录结束时间
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        self.overall_results["end_time"] = end_time.isoformat()
        self.overall_results["duration"] = duration
        
        # 分析并显示结果
        self.analyze_results()
        
        # 保存结果
        self.save_overall_results()
        
        print(f"\n结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 返回是否所有测试都通过
        return self.overall_results["total_failed"] == 0


def main():
    """主函数"""
    runner = MasterTestRunner()
    
    # 添加用户确认
    print("\n⚠️ 警告: 即将运行所有Agent的综合测试套件")
    print("预计包含400+测试用例，耗时20-30分钟")
    print("建议在系统负载较低时运行")
    
    response = input("\n是否继续？ (y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
        
    # 运行所有测试
    all_passed = runner.run_all_tests()
    
    # 返回适当的退出码
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()