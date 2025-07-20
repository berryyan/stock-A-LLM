#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent综合测试脚本 - Windows版本
不设置超时时间，完整测试所有功能
"""

import logging
import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到系统路径
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'concept_agent_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ConceptAgentComprehensiveTester:
    """Concept Agent综合测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.test_results = {
            'basic_tests': [],
            'performance_tests': [],
            'evidence_tests': [],
            'error_tests': [],
            'integration_tests': []
        }
        self.start_time = time.time()
        logger.info("="*80)
        logger.info("Concept Agent综合测试开始")
        logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
    
    def test_basic_functionality(self):
        """测试基本功能"""
        logger.info("\n" + "="*60)
        logger.info("第一部分：基本功能测试")
        logger.info("="*60)
        
        try:
            from agents.concept.concept_agent import ConceptAgent
            agent = ConceptAgent()
            logger.info("✅ ConceptAgent初始化成功")
        except Exception as e:
            logger.error(f"❌ ConceptAgent初始化失败: {e}")
            return
        
        # 基本测试用例
        test_cases = [
            {
                'id': 'basic_1',
                'name': '单一概念查询',
                'query': '概念股分析：充电宝',
                'expected_concepts': ['充电宝'],
                'min_stocks': 5
            },
            {
                'id': 'basic_2',
                'name': '多概念查询',
                'query': '概念股分析：白酒和消费概念股有哪些？',
                'expected_concepts': ['白酒', '消费'],
                'min_stocks': 10
            },
            {
                'id': 'basic_3',
                'name': '板块查询',
                'query': '概念股分析：新能源汽车板块',
                'expected_concepts': ['新能源汽车'],
                'min_stocks': 20
            },
            {
                'id': 'basic_4',
                'name': '问句形式',
                'query': '概念股分析：哪些股票涉及人工智能？',
                'expected_concepts': ['人工智能'],
                'min_stocks': 10
            }
        ]
        
        for case in test_cases:
            result = self._run_single_test(agent, case)
            self.test_results['basic_tests'].append(result)
            time.sleep(2)  # 避免请求过快
    
    def test_performance(self):
        """测试性能优化效果"""
        logger.info("\n" + "="*60)
        logger.info("第二部分：性能测试")
        logger.info("="*60)
        
        try:
            from agents.concept.concept_agent import ConceptAgent
            agent = ConceptAgent()
        except Exception as e:
            logger.error(f"❌ 性能测试初始化失败: {e}")
            return
        
        # 测试缓存效果
        cache_query = '概念股分析：储能概念股'
        
        logger.info("\n--- 缓存效果测试 ---")
        # 第一次查询
        start = time.time()
        result1 = agent.process_query(cache_query)
        time1 = time.time() - start
        
        if result1.success:
            logger.info(f"首次查询成功，耗时: {time1:.2f}秒")
            
            # 第二次查询（应该命中缓存）
            start = time.time()
            result2 = agent.process_query(cache_query)
            time2 = time.time() - start
            
            if result2.success:
                logger.info(f"缓存查询成功，耗时: {time2:.2f}秒")
                if time2 < time1:
                    speedup = time1 / time2
                    logger.info(f"✅ 缓存加速比: {speedup:.1f}x")
                    self.test_results['performance_tests'].append({
                        'test': 'cache_speedup',
                        'success': True,
                        'first_time': time1,
                        'cached_time': time2,
                        'speedup': speedup
                    })
                else:
                    logger.warning("⚠️ 缓存未生效")
        
        # 批量查询性能测试
        logger.info("\n--- 批量查询性能测试 ---")
        batch_queries = [
            '概念股分析：5G概念',
            '概念股分析：芯片概念',
            '概念股分析：医药概念'
        ]
        
        batch_start = time.time()
        batch_results = []
        for query in batch_queries:
            result = agent.process_query(query)
            if result.success:
                batch_results.append(result)
            time.sleep(1)
        
        batch_time = time.time() - batch_start
        avg_time = batch_time / len(batch_queries)
        logger.info(f"批量查询完成: 总耗时{batch_time:.2f}秒, 平均{avg_time:.2f}秒/查询")
        
        self.test_results['performance_tests'].append({
            'test': 'batch_query',
            'total_time': batch_time,
            'avg_time': avg_time,
            'query_count': len(batch_queries)
        })
    
    def test_evidence_system(self):
        """测试证据系统"""
        logger.info("\n" + "="*60)
        logger.info("第三部分：证据系统测试")
        logger.info("="*60)
        
        try:
            from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized
            collector = EvidenceCollectorOptimized()
            logger.info("✅ 证据收集器初始化成功")
        except Exception as e:
            logger.error(f"❌ 证据收集器初始化失败: {e}")
            return
        
        # 测试股票列表
        test_stocks = [
            {'ts_code': '300750.SZ', 'name': '宁德时代', 'concepts': ['储能', '锂电池']},
            {'ts_code': '002594.SZ', 'name': '比亚迪', 'concepts': ['新能源汽车', '电池']},
            {'ts_code': '600519.SH', 'name': '贵州茅台', 'concepts': ['白酒', '消费']}
        ]
        
        for stock in test_stocks:
            logger.info(f"\n测试股票: {stock['name']}({stock['ts_code']})")
            
            start = time.time()
            evidence = collector.collect_evidence(
                ts_code=stock['ts_code'],
                concepts=stock['concepts']
            )
            duration = time.time() - start
            
            # 统计证据
            evidence_count = {
                'software': len(evidence.get('software', [])),
                'interaction': len(evidence.get('interaction', [])),
                'report': len(evidence.get('report', [])),
                'announcement': len(evidence.get('announcement', []))
            }
            total_evidence = sum(evidence_count.values())
            
            # 计算得分
            scores = collector.calculate_total_score(evidence)
            
            logger.info(f"  证据收集完成，耗时: {duration:.2f}秒")
            logger.info(f"  证据数量: 软件{evidence_count['software']}, "
                       f"互动{evidence_count['interaction']}, "
                       f"财报{evidence_count['report']}, "
                       f"公告{evidence_count['announcement']}")
            logger.info(f"  总分: {scores['total']}/100")
            
            self.test_results['evidence_tests'].append({
                'stock': stock['name'],
                'ts_code': stock['ts_code'],
                'duration': duration,
                'evidence_count': evidence_count,
                'total_evidence': total_evidence,
                'score': scores['total']
            })
            
            time.sleep(1)
        
        # 显示缓存统计
        stats = collector.get_performance_stats()
        cache_stats = stats['cache_stats']
        logger.info(f"\n缓存统计:")
        logger.info(f"  命中率: {cache_stats['hit_rate']:.1%}")
        logger.info(f"  缓存大小: {cache_stats['size']}/{cache_stats['max_size']}")
    
    def test_error_handling(self):
        """测试错误处理"""
        logger.info("\n" + "="*60)
        logger.info("第四部分：错误处理测试")
        logger.info("="*60)
        
        try:
            from agents.concept.concept_agent import ConceptAgent
            agent = ConceptAgent()
        except Exception as e:
            logger.error(f"❌ 错误处理测试初始化失败: {e}")
            return
        
        error_cases = [
            {
                'id': 'error_1',
                'name': '空查询',
                'query': '概念股分析：',
                'expected_error': True
            },
            {
                'id': 'error_2',
                'name': '超长查询',
                'query': '概念股分析：' + 'test' * 200,
                'expected_error': True
            },
            {
                'id': 'error_3',
                'name': '特殊字符',
                'query': '概念股分析：@#$%^&*()',
                'expected_error': True
            },
            {
                'id': 'error_4',
                'name': '无效概念',
                'query': '概念股分析：xyz123abc不存在的概念',
                'expected_error': True
            }
        ]
        
        for case in error_cases:
            logger.info(f"\n测试: {case['name']}")
            
            start = time.time()
            result = agent.process_query(case['query'])
            duration = time.time() - start
            
            test_result = {
                'id': case['id'],
                'name': case['name'],
                'duration': duration
            }
            
            if not result.success:
                logger.info(f"✅ 正确处理错误: {result.error}")
                test_result['handled_correctly'] = True
                test_result['error_message'] = result.error
            else:
                logger.warning(f"⚠️ 预期失败但成功了")
                test_result['handled_correctly'] = False
            
            self.test_results['error_tests'].append(test_result)
    
    def test_integration(self):
        """测试系统集成"""
        logger.info("\n" + "="*60)
        logger.info("第五部分：系统集成测试")
        logger.info("="*60)
        
        # 测试优化版收集器与ConceptAgent的配合
        logger.info("\n--- 测试优化版收集器集成 ---")
        
        try:
            from agents.concept.concept_agent import ConceptAgent
            from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized
            
            agent = ConceptAgent()
            
            # 执行一个完整的查询
            query = '概念股分析：固态电池概念相关股票'
            
            start = time.time()
            result = agent.process_query(query)
            duration = time.time() - start
            
            if result.success:
                metadata = result.metadata or {}
                logger.info(f"✅ 集成测试成功")
                logger.info(f"  查询耗时: {duration:.2f}秒")
                logger.info(f"  识别概念: {metadata.get('original_concepts', [])}")
                logger.info(f"  扩展概念: {metadata.get('expanded_concepts', [])}")
                logger.info(f"  股票数量: {metadata.get('stock_count', 0)}")
                
                self.test_results['integration_tests'].append({
                    'test': 'full_integration',
                    'success': True,
                    'duration': duration,
                    'metadata': metadata
                })
            else:
                logger.error(f"❌ 集成测试失败: {result.error}")
                self.test_results['integration_tests'].append({
                    'test': 'full_integration',
                    'success': False,
                    'error': result.error
                })
                
        except Exception as e:
            logger.error(f"❌ 集成测试异常: {e}")
            self.test_results['integration_tests'].append({
                'test': 'full_integration',
                'success': False,
                'error': str(e)
            })
    
    def _run_single_test(self, agent, test_case: Dict) -> Dict:
        """运行单个测试用例"""
        logger.info(f"\n测试 {test_case['id']}: {test_case['name']}")
        logger.info(f"查询: {test_case['query']}")
        
        start = time.time()
        try:
            result = agent.process_query(test_case['query'])
            duration = time.time() - start
            
            test_result = {
                'id': test_case['id'],
                'name': test_case['name'],
                'query': test_case['query'],
                'duration': duration,
                'success': result.success
            }
            
            if result.success:
                metadata = result.metadata or {}
                test_result['metadata'] = metadata
                
                # 检查概念识别
                identified = metadata.get('original_concepts', [])
                expected = test_case.get('expected_concepts', [])
                if expected:
                    matched = len(set(identified) & set(expected))
                    match_rate = matched / len(expected) if expected else 0
                    test_result['concept_match_rate'] = match_rate
                    logger.info(f"  概念匹配率: {match_rate:.1%}")
                
                # 检查股票数量
                stock_count = metadata.get('stock_count', 0)
                min_stocks = test_case.get('min_stocks', 0)
                test_result['stock_count'] = stock_count
                test_result['meets_min_stocks'] = stock_count >= min_stocks
                
                logger.info(f"✅ 测试成功")
                logger.info(f"  识别概念: {identified}")
                logger.info(f"  股票数量: {stock_count}")
                logger.info(f"  耗时: {duration:.2f}秒")
            else:
                test_result['error'] = result.error
                logger.error(f"❌ 测试失败: {result.error}")
                
        except Exception as e:
            test_result = {
                'id': test_case['id'],
                'name': test_case['name'],
                'success': False,
                'error': str(e),
                'duration': time.time() - start
            }
            logger.error(f"❌ 测试异常: {e}")
        
        return test_result
    
    def generate_report(self):
        """生成测试报告"""
        total_time = time.time() - self.start_time
        
        logger.info("\n" + "="*80)
        logger.info("Concept Agent综合测试报告")
        logger.info("="*80)
        logger.info(f"总耗时: {total_time:.2f}秒")
        
        # 1. 基本功能测试统计
        basic_tests = self.test_results['basic_tests']
        if basic_tests:
            success = sum(1 for t in basic_tests if t.get('success', False))
            total = len(basic_tests)
            logger.info(f"\n基本功能测试: {success}/{total} 通过 ({success/total*100:.1f}%)")
            
            for test in basic_tests:
                status = "✅" if test.get('success', False) else "❌"
                logger.info(f"  {status} {test['name']} - {test.get('duration', 0):.2f}秒")
        
        # 2. 性能测试统计
        perf_tests = self.test_results['performance_tests']
        if perf_tests:
            logger.info(f"\n性能测试结果:")
            for test in perf_tests:
                if test.get('test') == 'cache_speedup':
                    logger.info(f"  缓存加速: {test.get('speedup', 0):.1f}x")
                elif test.get('test') == 'batch_query':
                    logger.info(f"  批量查询: 平均{test.get('avg_time', 0):.2f}秒/查询")
        
        # 3. 证据系统测试统计
        evidence_tests = self.test_results['evidence_tests']
        if evidence_tests:
            logger.info(f"\n证据系统测试:")
            for test in evidence_tests:
                logger.info(f"  {test['stock']}: {test['total_evidence']}条证据, "
                          f"得分{test['score']}/100, 耗时{test['duration']:.2f}秒")
        
        # 4. 错误处理测试统计
        error_tests = self.test_results['error_tests']
        if error_tests:
            handled = sum(1 for t in error_tests if t.get('handled_correctly', False))
            logger.info(f"\n错误处理测试: {handled}/{len(error_tests)} 正确处理")
        
        # 5. 集成测试统计
        integration_tests = self.test_results['integration_tests']
        if integration_tests:
            success = sum(1 for t in integration_tests if t.get('success', False))
            logger.info(f"\n集成测试: {success}/{len(integration_tests)} 通过")
        
        # 保存详细报告
        report_file = f'concept_agent_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_time': datetime.now().isoformat(),
                'total_duration': total_time,
                'results': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n详细报告已保存到: {report_file}")
        logger.info("\n" + "="*80)
        logger.info("测试完成！")


def main():
    """主函数"""
    tester = ConceptAgentComprehensiveTester()
    
    try:
        # 1. 基本功能测试
        tester.test_basic_functionality()
        
        # 2. 性能测试
        tester.test_performance()
        
        # 3. 证据系统测试
        tester.test_evidence_system()
        
        # 4. 错误处理测试
        tester.test_error_handling()
        
        # 5. 系统集成测试
        tester.test_integration()
        
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
    except Exception as e:
        logger.error(f"\n测试过程出现异常: {e}", exc_info=True)
    finally:
        # 生成报告
        tester.generate_report()


if __name__ == "__main__":
    main()