#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速模板匹配测试脚本
直接测试模板匹配功能，不调用实际的SQL查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import match_query_template, query_templates
from utils.date_intelligence import date_intelligence
from utils.logger import setup_logger

logger = setup_logger("test_quick_templates")

def test_template_matching():
    """测试模板匹配功能"""
    
    test_cases = [
        # 股价查询测试
        ('贵州茅台最新股价', '股价查询'),
        ('贵州茅台20250627的股价', '股价查询'),
        ('平安银行2025-06-27的股价', '股价查询'),
        ('中国平安2025年06月27日的股价', '股价查询'),
        ('格力电器昨天的股价', '股价查询'),
        
        # K线查询测试
        ('贵州茅台最近30天K线', 'K线查询'),
        ('平安银行从2025-06-01到2025-06-27的K线', 'K线查询'),
        ('中国平安过去5天的走势', 'K线查询'),
        
        # 成交量查询测试
        ('贵州茅台最新成交量', '成交量查询'),
        ('平安银行昨天的成交量', '成交量查询'),
        ('中国平安20250627的成交额', '成交量查询'),
        
        # 利润查询测试
        ('贵州茅台的净利润', '利润查询'),
        ('平安银行的营业收入', '利润查询'),
        
        # 估值指标查询测试
        ('中国平安最新PE', '估值指标查询'),
        ('贵州茅台昨天的市盈率', '估值指标查询'),
        ('平安银行20250627的市净率', '估值指标查询'),
        
        # 排名查询测试
        ('今天涨幅前10', '涨跌幅排名'),
        ('20250627涨幅前10', '涨跌幅排名'),
        ('昨天跌幅最大的20只股票', '涨跌幅排名'),
        ('上个交易日总市值排名前10', '总市值排名'),
        ('昨天流通市值前10', '流通市值排名'),
        
        # 主力净流入排行测试
        ('今日主力净流入排行前10', '主力净流入排行'),
        ('昨天主力净流入前20', '主力净流入排行'),
        ('20250627主力净流入排名', '主力净流入排行'),
        
        # 资金流向分析
        ('茅台的资金流向如何', '资金流向分析'),
        ('贵州茅台的超大单资金流入情况', '超大单分析'),
        
        # 财务健康度
        ('分析贵州茅台的财务健康度', '财务健康度分析'),
        
        # 杜邦分析
        ('平安银行的杜邦分析', '杜邦分析'),
        
        # 现金流分析
        ('万科的现金流质量', '现金流质量分析'),
    ]
    
    logger.info("="*60)
    logger.info("开始测试模板匹配功能")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for query, expected_template in test_cases:
        result = match_query_template(query)
        
        if result:
            template, params = result
            if template.name == expected_template:
                logger.info(f"✓ 通过: {query}")
                logger.info(f"  匹配模板: {template.name}")
                logger.info(f"  路由类型: {template.route_type}")
                logger.info(f"  提取参数: {params}")
                passed += 1
            else:
                logger.error(f"✗ 失败: {query}")
                logger.error(f"  期望模板: {expected_template}")
                logger.error(f"  实际模板: {template.name}")
                failed += 1
        else:
            logger.error(f"✗ 失败: {query}")
            logger.error(f"  期望模板: {expected_template}")
            logger.error(f"  实际结果: 未匹配到任何模板")
            failed += 1
        
        logger.info("")
    
    logger.info("="*60)
    logger.info(f"测试完成: 通过 {passed}, 失败 {failed}")
    logger.info(f"成功率: {passed/(passed+failed)*100:.1f}%")
    logger.info("="*60)


def test_date_intelligence_integration():
    """测试日期智能解析集成"""
    
    test_queries = [
        '贵州茅台最新股价',
        '贵州茅台昨天的股价',
        '平安银行前天的股价',
        '中国平安5天前的股价',
        '格力电器上个交易日的股价',
        '万科A最近30天的走势',
        '贵州茅台前5天的K线',
        '平安银行去年同期的股价',
        '今天涨幅前10',
        '昨天跌幅最大的股票',
        '上个月主力净流入排行',
    ]
    
    logger.info("\n" + "="*60)
    logger.info("开始测试日期智能解析集成")
    logger.info("="*60)
    
    for query in test_queries:
        logger.info(f"\n原始查询: {query}")
        
        # 测试日期解析
        result = date_intelligence.preprocess_question(query)
        modified_question = result[0]
        parse_info = result[1]
        
        if modified_question != query:
            logger.info(f"解析后: {modified_question}")
            logger.info(f"解析成功: {parse_info['success']}")
            logger.info(f"表达式数量: {parse_info['expressions_count']}")
        else:
            logger.info("未发现需要解析的日期表达")
        
        # 测试模板匹配
        template_result = match_query_template(modified_question)
        if template_result:
            template, params = template_result
            logger.info(f"匹配模板: {template.name}")
            logger.info(f"路由类型: {template.route_type}")


def test_date_extraction():
    """测试日期提取功能"""
    import re
    
    test_cases = [
        ('贵州茅台20250627的股价', '20250627'),
        ('平安银行2025-06-27的股价', '20250627'),
        ('中国平安2025年06月27日的股价', '20250627'),
        ('20250627涨幅前10', '20250627'),
        ('2025-06-27跌幅最大的股票', '20250627'),
    ]
    
    logger.info("\n" + "="*60)
    logger.info("开始测试日期提取功能")
    logger.info("="*60)
    
    # 日期提取正则表达式
    date_patterns = [
        (r'(\d{8})', lambda m: m.group(1)),
        (r'(\d{4})-(\d{2})-(\d{2})', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}"),
        (r'(\d{4})年(\d{2})月(\d{2})日', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}"),
    ]
    
    for query, expected_date in test_cases:
        logger.info(f"\n查询: {query}")
        logger.info(f"期望日期: {expected_date}")
        
        extracted_date = None
        for pattern, formatter in date_patterns:
            match = re.search(pattern, query)
            if match:
                extracted_date = formatter(match)
                break
        
        if extracted_date == expected_date:
            logger.info(f"✓ 提取成功: {extracted_date}")
        else:
            logger.error(f"✗ 提取失败: {extracted_date}")


def main():
    """主函数"""
    logger.info("开始快速模板功能测试")
    logger.info("="*60)
    
    # 运行各项测试
    test_template_matching()
    test_date_intelligence_integration()
    test_date_extraction()
    
    logger.info("\n所有测试完成！")


if __name__ == "__main__":
    main()