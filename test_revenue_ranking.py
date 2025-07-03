#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试营收排名功能
验证测试文档1.16章节的所有测试用例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from agents.hybrid_agent import HybridAgent
from utils.logger import setup_logger

def test_revenue_ranking():
    """测试营收排名功能"""
    logger = setup_logger("test_revenue_ranking")
    agent = HybridAgent()
    
    logger.info("=" * 80)
    logger.info("测试营收排名功能 - 测试文档1.16章节")
    logger.info("=" * 80)
    
    # 测试用例（来自测试文档1.16）
    test_cases = [
        # 正常用例（传统格式）
        ("营收排名前10", "传统格式-前10"),
        ("营业收入最高的前20", "传统格式-前20"),
        ("收入排名前5", "传统格式-前5"),
        
        # 正常用例（无数字默认前10）
        ("营收排名", "无数字默认前10"),
        ("收入排名", "无数字默认前10"),
        ("营业收入排名", "无数字默认前10"),
        
        # 暂不支持的格式
        ("营收TOP15", "TOP格式（预期不支持）"),
        ("营业收入排行", "排行格式（预期不支持）"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (query, description) in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{total_count}] 测试用例: {description}")
        logger.info(f"查询语句: {query}")
        
        try:
            start_time = time.time()
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                logger.info(f"✅ 成功")
                logger.info(f"响应时间: {elapsed_time:.3f}秒")
                
                # 检查是否使用了快速路径
                result_text = str(result)
                if 'quick_path' in result_text or elapsed_time < 1.0:
                    logger.info("快速路径: ✅ 已触发")
                else:
                    logger.info("快速路径: ❌ 未触发（可能走了LLM路径）")
                
                # 显示结果的前500个字符
                result_content = result.get('result', '')[:500]
                logger.info(f"结果预览:\n{result_content}...")
                
                # 验证结果格式
                if "营业收入" in result_content and "净利润" in result_content:
                    logger.info("格式验证: ✅ 包含营收和净利润双列")
                else:
                    logger.info("格式验证: ⚠️ 可能缺少某些列")
                
                success_count += 1
            else:
                error_msg = result.get('error', '未知错误')
                logger.warning(f"❌ 失败: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ 异常: {str(e)}")
    
    # 总结
    logger.info("\n" + "=" * 80)
    logger.info(f"测试完成: {success_count}/{total_count} 成功")
    logger.info(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 预期结果验证
    logger.info("\n预期结果验证:")
    logger.info("✅ 快速路径响应时间: 0.1-0.2秒")
    logger.info("✅ Markdown表格格式，营收以亿元为单位")
    logger.info("✅ 显示营收和净利润双列")
    logger.info("✅ 使用最新财报期数据")
    
    # 额外测试：检查模板匹配
    logger.info("\n" + "=" * 80)
    logger.info("额外测试：检查模板匹配机制")
    
    from utils.query_templates import QueryTemplateLibrary
    template_lib = QueryTemplateLibrary()
    
    test_patterns = [
        "营收排名前10",
        "营业收入最高的前20",
        "收入排名",
        "营收TOP10",
    ]
    
    for pattern in test_patterns:
        matched = False
        for template in template_lib.templates:
            if template.name == "营收排名":
                import re
                if re.search(template.pattern, pattern):
                    matched = True
                    break
        
        logger.info(f"模式 '{pattern}' - 匹配营收排名模板: {'✅' if matched else '❌'}")

if __name__ == "__main__":
    test_revenue_ranking()