#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 简化测试
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_simple_query():
    """测试简单查询"""
    logger.info("=== Concept Agent 简化测试 ===")
    
    # 初始化Agent
    agent = ConceptAgent()
    
    # 简单测试
    query = "储能概念股"
    logger.info(f"测试查询: {query}")
    
    try:
        result = agent.process_query(query)
        
        # 检查结果
        if result.get('success'):
            logger.info("✅ 查询成功")
            
            # 显示metadata
            metadata = result.get('metadata', {})
            logger.info(f"查询类型: {metadata.get('query_type')}")
            logger.info(f"原始概念: {metadata.get('original_concepts')}")
            logger.info(f"扩展概念: {metadata.get('expanded_concepts')}")
            logger.info(f"股票数量: {metadata.get('stock_count')}")
            
            # 显示部分结果
            if result.get('data'):
                data_str = str(result['data'])
                logger.info(f"结果预览: {data_str[:300]}...")
        else:
            logger.error(f"❌ 查询失败: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ 执行异常: {e}", exc_info=True)
    
    logger.info("\n=== 测试完成 ===")


def main():
    """主函数"""
    test_simple_query()


if __name__ == "__main__":
    main()