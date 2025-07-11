#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取调试脚本
"""
import sys
sys.path.append('.')

from utils.parameter_extractor import ParameterExtractor
from utils.query_templates import QueryTemplate, TemplateType

def test_param_extraction():
    """测试参数提取"""
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
        "分析银行的资金流向",
        "分析贵州茅台的资金流向"
    ]
    
    print("参数提取调试")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        params = extractor.extract_all_params(query, template)
        
        print(f"  原始查询: {params.raw_query}")
        print(f"  股票: {params.stocks}")
        print(f"  股票名称: {params.stock_names}")
        print(f"  板块: {params.sector}")
        print(f"  板块代码: {params.sector_code}")
        print(f"  行业: {params.industry}")
        print(f"  日期: {params.date}")
        print(f"  日期范围: {params.date_range}")
        print(f"  限制: {params.limit}")
        print(f"  错误: {params.error}")

if __name__ == "__main__":
    test_param_extraction()