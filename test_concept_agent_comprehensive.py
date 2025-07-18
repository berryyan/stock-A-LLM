#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent综合测试套件
测试Day 5的所有改进
"""

import logging
import sys
import time
import json
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_data_collector import ConceptDataCollector
from utils.concept.concept_data_collector_optimized import ConceptDataCollectorOptimized
from utils.concept.concept_matcher_v2 import ConceptMatcherV2
from utils.concept.concept_scorer import ConceptScorer
from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConceptAgentTester:
    """Concept Agent测试器"""
    
    def __init__(self):
        self.results = {
            "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tests": []
        }
    
    def add_test_result(self, test_name: str, status: str, details: dict):
        """添加测试结果"""
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    def test_data_sources(self):
        """测试数据源是否正常"""
        logger.info("\n=== 测试数据源 ===")
        test_name = "数据源测试"
        
        try:
            collector = ConceptDataCollector()
            
            # 测试不同概念
            test_concepts = [
                ["储能"],
                ["固态电池"], 
                ["人工智能"],
                ["新能源汽车"]
            ]
            
            all_passed = True
            details = {"concepts": {}}
            
            for concepts in test_concepts:
                stocks = collector.get_concept_stocks(concepts)
                concept_name = concepts[0]
                
                if stocks:
                    # 统计数据源
                    source_stats = {}
                    for stock in stocks:
                        for source in stock['data_source']:
                            source_stats[source] = source_stats.get(source, 0) + 1
                    
                    details["concepts"][concept_name] = {
                        "total_stocks": len(stocks),
                        "sources": source_stats,
                        "sample": [f"{s['name']}({s['ts_code']})" for s in stocks[:3]]
                    }
                    logger.info(f"{concept_name}: {len(stocks)}只股票, 数据源: {source_stats}")
                else:
                    all_passed = False
                    details["concepts"][concept_name] = {"error": "未找到股票"}
                    logger.warning(f"{concept_name}: 未找到股票")
            
            self.add_test_result(test_name, "PASS" if all_passed else "PARTIAL", details)
            
        except Exception as e:
            logger.error(f"数据源测试失败: {e}")
            self.add_test_result(test_name, "FAIL", {"error": str(e)})
    
    def test_performance_optimization(self):
        """测试性能优化效果"""
        logger.info("\n=== 测试性能优化 ===")
        test_name = "性能优化测试"
        
        try:
            # 测试概念
            concepts = ["储能", "固态电池", "人工智能"]
            
            # 测试原版
            logger.info("测试原版数据采集器...")
            collector_v1 = ConceptDataCollector()
            start_time = time.time()
            stocks_v1 = collector_v1.get_concept_stocks(concepts)
            time_v1 = time.time() - start_time
            
            # 测试优化版
            logger.info("测试优化版数据采集器...")
            collector_v2 = ConceptDataCollectorOptimized()
            start_time = time.time()
            stocks_v2 = collector_v2.get_concept_stocks(concepts, show_progress=False)
            time_v2 = time.time() - start_time
            
            # 计算提升
            improvement = (time_v1 - time_v2) / time_v1 * 100 if time_v1 > 0 else 0
            
            details = {
                "original": {
                    "time": f"{time_v1:.2f}秒",
                    "stocks": len(stocks_v1)
                },
                "optimized": {
                    "time": f"{time_v2:.2f}秒", 
                    "stocks": len(stocks_v2),
                    "max_per_concept": collector_v2.MAX_STOCKS_PER_CONCEPT
                },
                "improvement": f"{improvement:.1f}%"
            }
            
            logger.info(f"原版: {time_v1:.2f}秒, 优化版: {time_v2:.2f}秒, 提升: {improvement:.1f}%")
            
            self.add_test_result(test_name, "PASS", details)
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            self.add_test_result(test_name, "FAIL", {"error": str(e)})
    
    def test_concept_matcher_v2(self):
        """测试概念匹配器V2"""
        logger.info("\n=== 测试概念匹配器V2 ===")
        test_name = "概念匹配器V2测试"
        
        try:
            matcher = ConceptMatcherV2()
            
            # 测试用例
            test_cases = [
                {
                    "input": "储能相关的股票",
                    "expected_contains": ["储能"]
                },
                {
                    "input": "人工智能和AI概念",
                    "expected_contains": ["人工智能", "AI"]
                },
                {
                    "input": "新能源汽车产业链",
                    "expected_contains": ["新能源"]
                }
            ]
            
            all_passed = True
            details = {"cases": []}
            
            for case in test_cases:
                concepts = matcher.extract_concepts(case["input"])
                
                # 检查是否包含期望的概念
                found_all = all(
                    any(exp in concept for concept in concepts) 
                    for exp in case["expected_contains"]
                )
                
                case_result = {
                    "input": case["input"],
                    "concepts": concepts,
                    "expected": case["expected_contains"],
                    "passed": found_all
                }
                details["cases"].append(case_result)
                
                if not found_all:
                    all_passed = False
                
                logger.info(f"输入: {case['input']} -> 概念: {concepts}")
            
            self.add_test_result(test_name, "PASS" if all_passed else "PARTIAL", details)
            
        except Exception as e:
            logger.error(f"概念匹配器测试失败: {e}")
            self.add_test_result(test_name, "FAIL", {"error": str(e)})
    
    def test_scoring_system(self):
        """测试评分系统"""
        logger.info("\n=== 测试评分系统 ===")
        test_name = "评分系统测试"
        
        try:
            # 获取测试数据
            collector = ConceptDataCollector()
            stocks = collector.get_concept_stocks(["储能"])[:20]  # 只测试前20只
            
            if not stocks:
                self.add_test_result(test_name, "SKIP", {"reason": "无测试数据"})
                return
            
            # 创建评分器
            scorer = ConceptScorer()
            
            # 评分
            scores = scorer.calculate_scores(stocks, ["储能"])
            
            # 统计
            score_values = [s['total_score'] for s in scores]
            avg_score = sum(score_values) / len(score_values) if score_values else 0
            max_score = max(score_values) if score_values else 0
            min_score = min(score_values) if score_values else 0
            
            # 获取前3名
            top_3 = sorted(scores, key=lambda x: x['total_score'], reverse=True)[:3]
            
            details = {
                "total_stocks": len(scores),
                "avg_score": f"{avg_score:.1f}",
                "max_score": f"{max_score:.1f}",
                "min_score": f"{min_score:.1f}",
                "top_3": [
                    {
                        "name": s['name'],
                        "code": s['ts_code'],
                        "score": f"{s['total_score']:.1f}"
                    }
                    for s in top_3
                ]
            }
            
            logger.info(f"评分完成: 平均分={avg_score:.1f}, 最高分={max_score:.1f}")
            
            self.add_test_result(test_name, "PASS", details)
            
        except Exception as e:
            logger.error(f"评分系统测试失败: {e}")
            self.add_test_result(test_name, "FAIL", {"error": str(e)})
    
    def test_concept_agent(self):
        """测试Concept Agent端到端功能"""
        logger.info("\n=== 测试Concept Agent ===")
        test_name = "Concept Agent端到端测试"
        
        try:
            agent = ConceptAgent()
            
            # 测试查询
            test_queries = [
                "储能概念股有哪些？",
                "分析固态电池概念的投资机会",
                "人工智能相关股票"
            ]
            
            details = {"queries": []}
            all_passed = True
            
            for query in test_queries:
                logger.info(f"\n测试查询: {query}")
                
                try:
                    start_time = time.time()
                    response = agent.process_query(query)
                    elapsed_time = time.time() - start_time
                    
                    if response.get("success"):
                        # 统计结果
                        result_text = response.get("result", "")
                        stock_count = result_text.count("(") if isinstance(result_text, str) else 0
                        
                        query_result = {
                            "query": query,
                            "status": "SUCCESS",
                            "time": f"{elapsed_time:.2f}秒",
                            "stock_count": stock_count,
                            "result_length": len(str(result_text))
                        }
                        logger.info(f"成功: 耗时{elapsed_time:.2f}秒")
                    else:
                        query_result = {
                            "query": query,
                            "status": "FAIL",
                            "error": response.get("error", "Unknown error")
                        }
                        all_passed = False
                        logger.error(f"失败: {response.get('error')}")
                    
                except Exception as e:
                    query_result = {
                        "query": query,
                        "status": "ERROR",
                        "error": str(e)
                    }
                    all_passed = False
                    logger.error(f"异常: {e}")
                
                details["queries"].append(query_result)
            
            self.add_test_result(test_name, "PASS" if all_passed else "PARTIAL", details)
            
        except Exception as e:
            logger.error(f"Agent测试失败: {e}")
            self.add_test_result(test_name, "FAIL", {"error": str(e)})
    
    def save_results(self):
        """保存测试结果"""
        filename = f"concept_agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n测试结果已保存到: {filename}")
        
        # 打印摘要
        logger.info("\n=== 测试摘要 ===")
        passed = sum(1 for t in self.results["tests"] if t["status"] == "PASS")
        partial = sum(1 for t in self.results["tests"] if t["status"] == "PARTIAL")
        failed = sum(1 for t in self.results["tests"] if t["status"] == "FAIL")
        total = len(self.results["tests"])
        
        logger.info(f"总测试数: {total}")
        logger.info(f"通过: {passed}")
        logger.info(f"部分通过: {partial}")
        logger.info(f"失败: {failed}")
        
        return filename


def main():
    """主函数"""
    tester = ConceptAgentTester()
    
    # 运行所有测试
    tester.test_data_sources()
    tester.test_performance_optimization()
    tester.test_concept_matcher_v2()
    tester.test_scoring_system()
    tester.test_concept_agent()
    
    # 保存结果
    tester.save_results()


if __name__ == "__main__":
    main()