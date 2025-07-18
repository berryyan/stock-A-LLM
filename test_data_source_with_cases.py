#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用调查结果测试数据源
验证各数据源是否正常返回数据
"""

import logging
import sys
import json

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_data_collector import ConceptDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourceTester:
    """数据源测试器"""
    
    def __init__(self):
        self.collector = ConceptDataCollector()
        self.test_results = []
    
    def test_common_concepts(self):
        """测试通用概念（三个数据源都有）"""
        logger.info("\n=== 测试通用概念 ===")
        
        # 选择几个通用概念进行测试
        common_concepts = [
            "英伟达概念",
            "DeepSeek概念",
            "智能电网",
            "宠物经济",
            "西部大开发"
        ]
        
        for concept in common_concepts:
            logger.info(f"\n测试概念: {concept}")
            self._test_concept(concept, expect_all=True)
    
    def test_partial_concepts(self):
        """测试部分共有概念"""
        logger.info("\n=== 测试部分共有概念 ===")
        
        test_cases = [
            ("职业教育", ["THS", "DC"]),
            ("液冷服务器", ["THS", "KPL"]),
            ("影视概念", ["DC", "KPL"])
        ]
        
        for concept, expected_sources in test_cases:
            logger.info(f"\n测试概念: {concept} (期望数据源: {expected_sources})")
            self._test_concept(concept, expected_sources=expected_sources)
    
    def test_unique_concepts(self):
        """测试独有概念"""
        logger.info("\n=== 测试独有概念 ===")
        
        test_cases = [
            ("华为海思概念股", ["THS"]),
            ("贵金属", ["DC"]),
            ("AI算力基建", ["KPL"])
        ]
        
        for concept, expected_sources in test_cases:
            logger.info(f"\n测试概念: {concept} (期望数据源: {expected_sources})")
            self._test_concept(concept, expected_sources=expected_sources)
    
    def test_naming_variations(self):
        """测试命名差异"""
        logger.info("\n=== 测试命名差异 ===")
        
        # 测试不同的命名方式
        variations = [
            ("储能", "储能概念"),  # 同花顺用"储能概念"，其他用"储能"
            ("新能源", "新能源汽车"),  # 东财可能只有"新能源"
            ("光伏", "光伏概念"),  # 类似的差异
        ]
        
        for short_name, long_name in variations:
            logger.info(f"\n测试命名差异: {short_name} vs {long_name}")
            
            # 测试短名称
            logger.info(f"查询: {short_name}")
            result1 = self.collector.get_concept_stocks([short_name])
            
            # 测试长名称
            logger.info(f"查询: {long_name}")
            result2 = self.collector.get_concept_stocks([long_name])
            
            # 分析结果
            sources1 = self._extract_data_sources(result1)
            sources2 = self._extract_data_sources(result2)
            
            logger.info(f"{short_name} 数据源: {sources1}")
            logger.info(f"{long_name} 数据源: {sources2}")
            
            self.test_results.append({
                "type": "naming_variation",
                "test": f"{short_name} vs {long_name}",
                "results": {
                    short_name: {"count": len(result1), "sources": sources1},
                    long_name: {"count": len(result2), "sources": sources2}
                }
            })
    
    def _test_concept(self, concept, expect_all=False, expected_sources=None):
        """测试单个概念"""
        try:
            # 获取概念股
            stocks = self.collector.get_concept_stocks([concept])
            
            # 分析数据源
            data_sources = self._extract_data_sources(stocks)
            
            # 记录结果
            result = {
                "concept": concept,
                "total_stocks": len(stocks),
                "data_sources": data_sources,
                "success": True
            }
            
            # 验证期望
            if expect_all:
                # 期望三个数据源都有数据
                expected = ["THS", "DC", "KPL"]
                missing = set(expected) - set(data_sources.keys())
                if missing:
                    logger.warning(f"⚠️ 缺少数据源: {missing}")
                    result["missing_sources"] = list(missing)
            elif expected_sources:
                # 期望特定数据源有数据
                missing = set(expected_sources) - set(data_sources.keys())
                extra = set(data_sources.keys()) - set(expected_sources)
                if missing:
                    logger.warning(f"⚠️ 缺少期望的数据源: {missing}")
                    result["missing_sources"] = list(missing)
                if extra:
                    logger.info(f"ℹ️ 额外的数据源: {extra}")
                    result["extra_sources"] = list(extra)
            
            # 显示结果
            logger.info(f"找到 {len(stocks)} 只股票")
            for source, count in data_sources.items():
                logger.info(f"  {source}: {count} 只")
            
            # 显示前3只股票作为示例
            if stocks:
                logger.info("示例股票:")
                for i, stock in enumerate(stocks[:3], 1):
                    logger.info(f"  {i}. {stock['name']} ({stock['ts_code']}) - 数据源: {stock['data_source']}")
            
            self.test_results.append(result)
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            self.test_results.append({
                "concept": concept,
                "success": False,
                "error": str(e)
            })
    
    def _extract_data_sources(self, stocks):
        """提取数据源统计"""
        data_source_count = {}
        for stock in stocks:
            for source in stock.get('data_source', []):
                data_source_count[source] = data_source_count.get(source, 0) + 1
        return data_source_count
    
    def save_results(self):
        """保存测试结果"""
        filename = "data_source_test_results.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_time": "2025-07-18",
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"\n测试结果已保存到: {filename}")
    
    def analyze_results(self):
        """分析测试结果"""
        logger.info("\n=== 测试结果分析 ===")
        
        total_tests = len(self.test_results)
        successful = sum(1 for r in self.test_results if r.get('success', False))
        
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"成功: {successful}")
        logger.info(f"失败: {total_tests - successful}")
        
        # 统计数据源覆盖
        source_coverage = {"THS": 0, "DC": 0, "KPL": 0}
        for result in self.test_results:
            if result.get('success') and 'data_sources' in result:
                for source in result['data_sources']:
                    if source in source_coverage:
                        source_coverage[source] += 1
        
        logger.info("\n数据源覆盖率:")
        for source, count in source_coverage.items():
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            logger.info(f"  {source}: {count}/{total_tests} ({percentage:.1f}%)")
        
        # 问题总结
        problems = []
        for result in self.test_results:
            if 'missing_sources' in result:
                problems.append(f"{result['concept']}: 缺少 {result['missing_sources']}")
        
        if problems:
            logger.info("\n发现的问题:")
            for problem in problems[:10]:  # 只显示前10个
                logger.info(f"  - {problem}")


def main():
    """主函数"""
    tester = DataSourceTester()
    
    # 执行测试
    tester.test_common_concepts()
    tester.test_partial_concepts()
    tester.test_unique_concepts()
    tester.test_naming_variations()
    
    # 分析和保存结果
    tester.analyze_results()
    tester.save_results()
    
    logger.info("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()