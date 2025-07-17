#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试概念股数据结构
"""

import logging
import sys
import json

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_data_collector import ConceptDataCollector
from utils.concept.money_flow_collector import MoneyFlowCollector
from utils.concept.technical_collector import TechnicalCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def debug_concept_stocks():
    """调试概念股数据"""
    logger.info("=== 调试概念股数据结构 ===")
    
    # 初始化采集器
    concept_collector = ConceptDataCollector()
    
    # 获取储能概念股
    concept_stocks = concept_collector.get_concept_stocks(["储能"])
    
    logger.info(f"共找到 {len(concept_stocks)} 只储能概念股")
    
    # 查看前3只股票的数据结构
    for i, stock in enumerate(concept_stocks[:3]):
        logger.info(f"\n股票 {i+1}:")
        logger.info(json.dumps(stock, ensure_ascii=False, indent=2))
    
    return concept_stocks


def debug_money_flow():
    """调试资金流向数据"""
    logger.info("\n=== 调试资金流向数据 ===")
    
    money_collector = MoneyFlowCollector()
    
    # 测试单只股票
    test_code = "000021.SZ"
    money_data = money_collector.get_stock_money_flow(test_code)
    
    logger.info(f"{test_code} 资金流向数据:")
    logger.info(json.dumps(money_data, ensure_ascii=False, indent=2))
    
    return money_data


def debug_technical():
    """调试技术指标数据"""
    logger.info("\n=== 调试技术指标数据 ===")
    
    tech_collector = TechnicalCollector()
    
    # 测试几只股票
    test_codes = ["000021.SZ", "000027.SZ", "000030.SZ"]
    tech_data = tech_collector.get_latest_technical_indicators(test_codes)
    
    for code, data in tech_data.items():
        logger.info(f"\n{code} 技术指标:")
        logger.info(json.dumps(data, ensure_ascii=False, indent=2))
    
    return tech_data


def check_data_fields():
    """检查数据字段是否完整"""
    logger.info("\n=== 检查数据完整性 ===")
    
    # 获取少量概念股
    concept_collector = ConceptDataCollector()
    concept_stocks = concept_collector.get_concept_stocks(["储能"])[:3]
    
    # 检查概念股数据字段
    logger.info("\n概念股数据字段检查:")
    expected_fields = [
        'ts_code', 'name', 'concepts', 'data_source', 
        'first_limit_date', 'financial_report_mention',
        'interaction_mention', 'announcement_mention', 'sector_rank_pct'
    ]
    
    for stock in concept_stocks:
        logger.info(f"\n{stock['name']} ({stock['ts_code']}):")
        for field in expected_fields:
            if field in stock:
                logger.info(f"  ✓ {field}: {stock[field]}")
            else:
                logger.warning(f"  ✗ {field}: 缺失")


def main():
    """主函数"""
    try:
        # 1. 调试概念股数据
        concept_stocks = debug_concept_stocks()
        
        # 2. 调试资金流向数据
        money_data = debug_money_flow()
        
        # 3. 调试技术指标数据
        tech_data = debug_technical()
        
        # 4. 检查数据完整性
        check_data_fields()
        
        logger.info("\n=== 调试完成 ===")
        
    except Exception as e:
        logger.error(f"调试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()