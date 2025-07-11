#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试光伏设备板块查询问题"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_sector_validator import extract_sector
from utils.parameter_extractor import ParameterExtractor
from agents.money_flow_agent import MoneyFlowAgent
import logging
import re

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)

def debug_photovoltaic_query():
    """调试光伏设备板块查询"""
    query = "评估光伏设备板块的资金趋势"
    print(f"调试查询: {query}")
    print("="*60)
    
    # 1. 测试板块提取
    print("\n1. 板块提取测试:")
    sector_result = extract_sector(query)
    if sector_result:
        sector_name, sector_code = sector_result
        print(f"   提取到板块: {sector_name} ({sector_code})")
    else:
        print("   未能提取到板块")
    
    # 2. 测试参数提取
    print("\n2. 参数提取测试:")
    extractor = ParameterExtractor()
    params = extractor.extract_all_params(query)
    print(f"   板块: {params.sector}")
    print(f"   板块代码: {params.sector_code}")
    print(f"   错误: {params.error}")
    
    # 3. 测试Money Flow Agent处理
    print("\n3. Money Flow Agent处理:")
    try:
        agent = MoneyFlowAgent()
        result = agent.query(query)
        print(f"   成功: {result.get('success', False)}")
        if not result.get('success'):
            print(f"   错误: {result.get('error', '未知错误')}")
        else:
            print(f"   结果预览: {result.get('result', '')[:200]}...")
    except Exception as e:
        print(f"   处理异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. 测试板块名称映射
    print("\n4. 测试板块名称映射:")
    from utils.sector_name_mapper import map_sector_name
    mapped = map_sector_name("光伏设备")
    print(f"   '光伏设备' 映射结果: {mapped}")
    
    # 5. 测试板块代码查询
    print("\n5. 测试板块代码查询:")
    from utils.sector_code_mapper import SectorCodeMapper
    mapper = SectorCodeMapper()
    code = mapper.get_sector_code("光伏设备")
    print(f"   '光伏设备' 板块代码: {code}")

if __name__ == "__main__":
    debug_photovoltaic_query()