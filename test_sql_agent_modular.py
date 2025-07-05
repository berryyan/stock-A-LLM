#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL Agent模块化版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from utils.logger import setup_logger
import time

logger = setup_logger("test_sql_agent_modular")


def test_basic_queries():
    """测试基本查询功能"""
    # 初始化SQL Agent模块化版本
    agent = SQLAgentModular()
    
    # 基本测试用例
    test_cases = [
        # 股价查询
        "贵州茅台的最新股价",
        "万科A昨天的股价",
        
        # 市值排名
        "市值排名前5",
        
        # 涨跌幅排名
        "今天涨幅最大的10只股票",
        
        # 错误测试
        "不存在的股票ABC123的股价",
        "",  # 空查询
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_cases)}: {query}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            print(f"成功: {result.get('success', False)}")
            print(f"耗时: {elapsed_time:.2f}秒")
            print(f"快速路径: {result.get('quick_path', False)}")
            
            if result.get('success'):
                print("结果预览:")
                result_text = result.get('result', '无结果')
                # 只显示前500个字符
                if len(result_text) > 500:
                    print(result_text[:500] + "...")
                else:
                    print(result_text)
            else:
                print(f"错误: {result.get('error', '未知错误')}")
                if result.get('suggestion'):
                    print(f"建议: {result.get('suggestion')}")
            
        except Exception as e:
            print(f"异常: {str(e)}")
            logger.error(f"测试异常: {str(e)}", exc_info=True)


def test_parameter_extraction():
    """测试参数提取功能"""
    agent = SQLAgentModular()
    
    print("\n" + "="*60)
    print("测试参数提取功能")
    print("="*60)
    
    test_queries = [
        "贵州茅台和五粮液的对比",
        "ST股票的涨幅排名",
        "本月的K线数据",
        "前20名市值最大的股票",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            params = agent.param_extractor.extract_all_params(query)
            print(f"提取的股票: {params.stocks}")
            print(f"股票名称: {params.stock_names}")
            print(f"日期: {params.date}")
            print(f"日期范围: {params.date_range}")
            print(f"数量限制: {params.limit}")
            print(f"错误: {params.error}")
        except Exception as e:
            print(f"参数提取异常: {str(e)}")


def test_result_formatting():
    """测试结果格式化功能"""
    agent = SQLAgentModular()
    
    print("\n" + "="*60)
    print("测试结果格式化功能")
    print("="*60)
    
    # 测试表格格式化
    headers = ["排名", "股票代码", "股票名称", "涨跌幅(%)"]
    rows = [
        [1, "600519.SH", "贵州茅台", "2.35"],
        [2, "000858.SZ", "五粮液", "1.82"],
        [3, "000568.SZ", "泸州老窖", "1.56"],
    ]
    
    formatted = agent.result_formatter.format_table(headers, rows, title="涨幅排名前3")
    print("\n表格格式化结果:")
    print(formatted)
    
    # 测试字典格式化
    data = {
        "股票": "贵州茅台（600519.SH）",
        "最新价": "1850.00",
        "涨跌幅": "2.35%",
        "成交量": "125.36万手"
    }
    
    formatted = agent.result_formatter.format_dict_data(data)
    print("\n字典格式化结果:")
    print(formatted)


if __name__ == "__main__":
    print("开始测试SQL Agent模块化版本...")
    
    # 测试基本查询
    test_basic_queries()
    
    # 测试参数提取
    test_parameter_extraction()
    
    # 测试结果格式化
    test_result_formatting()
    
    print("\n测试完成！")