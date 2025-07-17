#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 综合测试套件
包含各种测试场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.concept.concept_agent import ConceptAgent
import logging
import time
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ConceptAgentTester:
    """Concept Agent测试器"""
    
    def __init__(self):
        """初始化测试器"""
        print("初始化Concept Agent...")
        self.agent = ConceptAgent()
        self.test_results = []
    
    def run_test(self, test_name: str, query: str, expected_type: str = None) -> Dict[str, Any]:
        """运行单个测试"""
        print(f"\n{'='*80}")
        print(f"测试: {test_name}")
        print(f"查询: {query}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            result = self.agent.process_query(query)
            elapsed_time = time.time() - start_time
            
            test_result = {
                'name': test_name,
                'query': query,
                'success': result.success if hasattr(result, 'success') else result.get('success', False),
                'elapsed_time': elapsed_time,
                'error': result.error if hasattr(result, 'error') else result.get('error')
            }
            
            if test_result['success']:
                print(f"✅ 成功 (耗时: {elapsed_time:.2f}秒)")
                # 打印部分结果
                data = result.data if hasattr(result, 'data') else result.get('data', '')
                if data:
                    lines = str(data).split('\n')
                    print("\n结果预览:")
                    for line in lines[:10]:  # 只显示前10行
                        print(line)
                    if len(lines) > 10:
                        print(f"... (还有 {len(lines)-10} 行)")
                
                # 检查元数据
                metadata = result.metadata if hasattr(result, 'metadata') else result.get('metadata', {})
                if metadata:
                    print(f"\n元数据:")
                    print(f"  - 查询类型: {metadata.get('query_type', 'N/A')}")
                    print(f"  - 股票数量: {metadata.get('stock_count', 'N/A')}")
                    print(f"  - 原始概念: {metadata.get('original_concepts', [])}")
                    print(f"  - 扩展概念: {len(metadata.get('expanded_concepts', []))}个")
            else:
                print(f"❌ 失败: {test_result['error']}")
            
            self.test_results.append(test_result)
            return test_result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            test_result = {
                'name': test_name,
                'query': query,
                'success': False,
                'elapsed_time': elapsed_time,
                'error': str(e)
            }
            print(f"❌ 异常: {str(e)}")
            self.test_results.append(test_result)
            return test_result
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print("Concept Agent 综合测试")
        print("="*80)
        
        # 1. 基础关键词测试
        self.run_test(
            "基础关键词测试",
            "概念股分析：充电宝"
        )
        
        # 2. 概念查询测试
        self.run_test(
            "概念查询测试",
            "概念股分析：固态电池概念股有哪些？"
        )
        
        # 3. 复杂查询测试
        self.run_test(
            "复杂查询测试",
            "概念股分析：新能源汽车和储能相关的概念股现在可以重点关注哪些？"
        )
        
        # 4. 新闻文本测试（短文本）
        self.run_test(
            "新闻文本测试-短",
            """概念股分析：工信部发布《新能源汽车产业发展规划》，明确提出支持固态电池、
            氢燃料电池等新型动力电池技术研发，鼓励企业加大创新投入。政策利好哪些概念股？"""
        )
        
        # 5. 新闻文本测试（长文本）
        self.run_test(
            "新闻文本测试-长",
            """概念股分析：据悉，国家发改委、工信部等多部门近日联合发布《关于推动新型储能
            高质量发展的指导意见》。文件指出，到2025年，新型储能装机规模达到3000万千瓦以上，
            到2030年，新型储能全面市场化发展。文件特别强调，要重点发展锂离子电池、钠离子电池、
            液流电池、压缩空气储能、飞轮储能等多元化技术路线。同时，支持固态电池、锂金属电池、
            钠离子电池等新一代高能量密度储能技术研发和产业化。在应用场景方面，文件提出要在
            电源侧、电网侧、用户侧等多场景推广应用，特别是在新能源汽车充换电、数据中心、
            5G基站、工业园区等领域加快部署。分析这个政策对相关概念股的影响。"""
        )
        
        # 6. 边界测试 - 空查询
        self.run_test(
            "边界测试-空查询",
            "概念股分析："
        )
        
        # 7. 边界测试 - 无效概念
        self.run_test(
            "边界测试-无效概念",
            "概念股分析：这是一个不存在的概念xyz123"
        )
        
        # 8. 多概念组合测试
        self.run_test(
            "多概念组合测试",
            "概念股分析：人工智能、大数据、云计算相关概念股"
        )
        
        # 9. 特殊字符测试
        self.run_test(
            "特殊字符测试",
            "概念股分析：5G+工业互联网"
        )
        
        # 10. 性能测试 - 热门概念
        self.run_test(
            "性能测试-热门概念",
            "概念股分析：新能源"
        )
        
        # 打印测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*80)
        print("测试总结")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        # 性能统计
        successful_times = [r['elapsed_time'] for r in self.test_results if r['success']]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            max_time = max(successful_times)
            min_time = min(successful_times)
            
            print(f"\n性能统计（成功的测试）:")
            print(f"  - 平均耗时: {avg_time:.2f}秒")
            print(f"  - 最快: {min_time:.2f}秒")
            print(f"  - 最慢: {max_time:.2f}秒")
        
        # 失败详情
        if failed_tests > 0:
            print(f"\n失败的测试:")
            for r in self.test_results:
                if not r['success']:
                    print(f"  - {r['name']}: {r['error']}")
        
        # 建议
        print(f"\n建议:")
        if failed_tests > 0:
            print("  - 检查失败的测试用例，可能需要优化错误处理")
        if successful_times and avg_time > 30:
            print("  - 平均响应时间较长，考虑优化查询性能")
        if passed_tests == total_tests:
            print("  - 所有测试通过！可以考虑添加更多边界测试")


def main():
    """主函数"""
    tester = ConceptAgentTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        if hasattr(tester.agent, '__del__'):
            tester.agent.__del__()


if __name__ == "__main__":
    main()