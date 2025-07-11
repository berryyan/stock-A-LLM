#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块提取调试脚本
"""
import sys
sys.path.append('.')
import logging

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

from utils.parameter_extractor import ParameterExtractor
from utils.query_templates import QueryTemplate, TemplateType

def test_sector_extraction():
    """测试板块提取"""
    extractor = ParameterExtractor()
    
    # 创建Money Flow模板
    template = QueryTemplate(
        name="资金流向分析",
        type=TemplateType.MONEY_FLOW,
        pattern="",
        route_type="MONEY_FLOW",
        required_fields=[],
        optional_fields=['stocks', 'sector', 'date', 'limit'],
        default_params={},
        example="分析贵州茅台的资金流向",
        requires_stock=False,
        requires_date=False,
        supports_exclude_st=True
    )
    
    test_queries = [
        "银行板块的主力资金",
        "分析银行板块的资金流向",
        "评估新能源板块的资金趋势",
    ]
    
    print("板块提取调试")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        params = extractor.extract_all_params(query, template)
        print(f"  提取到板块: {params.sector}")
        print(f"  板块代码: {params.sector_code}")

if __name__ == "__main__":
    test_sector_extraction()