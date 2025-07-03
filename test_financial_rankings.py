#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有财务排名功能
包括：PE排名、PB排名、净利润排名、营收排名、ROE排名
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from agents.hybrid_agent import HybridAgent
from utils.logger import setup_logger

def test_financial_rankings():
    """测试所有财务排名功能"""
    logger = setup_logger("test_financial_rankings")
    agent = HybridAgent()
    
    # 测试用例列表
    test_cases = [
        # PE排名
        ("PE排名前10", "PE排名"),
        ("市盈率最高的前5", "PE排名"),
        ("PE排名", "PE排名（默认前10）"),
        
        # PB排名
        ("PB排名前10", "PB排名"),
        ("市净率最低的前10", "PB排名"),
        ("PB排名", "PB排名（默认前10）"),
        
        # 净利润排名
        ("净利润排名前10", "净利润排名"),
        ("利润最高的前20", "净利润排名"),
        ("盈利排名", "净利润排名（默认前10）"),
        
        # 营收排名
        ("营收排名前10", "营收排名"),
        ("营业收入最高的前20", "营收排名"),
        ("收入排名", "营收排名（默认前10）"),
        
        # ROE排名
        ("ROE排名前10", "ROE排名"),
        ("净资产收益率最高的前15", "ROE排名"),
        ("ROE排名", "ROE排名（默认前10）"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for query, description in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"测试: {description}")
        logger.info(f"查询: {query}")
        
        try:
            start_time = time.time()
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                # 检查是否走了快速路径
                if 'quick_path' in str(result):
                    logger.info(f"✅ 成功 - 快速路径响应时间: {elapsed_time:.2f}秒")
                else:
                    logger.info(f"✅ 成功 - 普通路径响应时间: {elapsed_time:.2f}秒")
                
                # 打印结果的前500个字符
                result_text = result.get('result', '')[:500]
                logger.info(f"结果预览:\n{result_text}...")
                
                success_count += 1
            else:
                logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"❌ 异常: {str(e)}")
    
    # 总结
    logger.info(f"\n{'='*60}")
    logger.info(f"测试完成: {success_count}/{total_count} 成功")
    logger.info(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 测试特殊情况
    logger.info(f"\n{'='*60}")
    logger.info("测试特殊情况...")
    
    special_cases = [
        ("营收TOP10", "TOP格式（预期失败）"),
        ("营收排行榜", "排行榜格式（预期失败）"),
        ("亏损最多的前10", "亏损排名"),
    ]
    
    for query, description in special_cases:
        logger.info(f"\n测试: {description}")
        logger.info(f"查询: {query}")
        
        try:
            result = agent.query(query)
            if result.get('success'):
                logger.info(f"✅ 成功处理")
            else:
                logger.info(f"⚠️ 预期的失败: {result.get('error', '')}")
        except Exception as e:
            logger.info(f"⚠️ 预期的异常: {str(e)}")

if __name__ == "__main__":
    test_financial_rankings()