#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源深度调查
查询三个数据源的原始数据库内容，找到合适的测试用例
"""

import logging
import sys
from collections import Counter

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from database.mysql_connector import MySQLConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def investigate_ths_concepts(mysql: MySQLConnector):
    """调查同花顺概念"""
    logger.info("\n=== 同花顺概念调查 ===")
    
    # 查询所有概念
    query = """
    SELECT DISTINCT name, ts_code
    FROM tu_ths_index
    WHERE exchange = 'A' AND type = 'N'
    ORDER BY name
    """
    
    concepts = mysql.execute_query(query)
    logger.info(f"同花顺概念总数: {len(concepts)}")
    
    # 显示部分概念
    logger.info("\n前20个概念:")
    for i, concept in enumerate(concepts[:20], 1):
        logger.info(f"{i}. {concept['name']} ({concept['ts_code']})")
    
    # 查找包含特定关键词的概念
    keywords = ['储能', '新能源', '电池', '光伏', '风电', '汽车', '银行', '医药']
    logger.info("\n关键词匹配:")
    for keyword in keywords:
        matched = [c['name'] for c in concepts if keyword in c['name']]
        if matched:
            logger.info(f"'{keyword}': {len(matched)}个 - {', '.join(matched[:5])}")
    
    return [(c['name'], c['ts_code']) for c in concepts]


def investigate_dc_concepts(mysql: MySQLConnector):
    """调查东财板块"""
    logger.info("\n=== 东财板块调查 ===")
    
    # 查询所有板块
    query = """
    SELECT DISTINCT name, leading_code
    FROM tu_dc_index
    WHERE 1=1
    ORDER BY name
    """
    
    concepts = mysql.execute_query(query)
    logger.info(f"东财板块总数: {len(concepts)}")
    
    # 显示部分板块
    logger.info("\n前20个板块:")
    for i, concept in enumerate(concepts[:20], 1):
        logger.info(f"{i}. {concept['name']} ({concept['leading_code']})")
    
    # 查找包含特定关键词的板块
    keywords = ['储能', '新能源', '电池', '光伏', '风电', '汽车', '银行', '医药']
    logger.info("\n关键词匹配:")
    for keyword in keywords:
        matched = [c['name'] for c in concepts if keyword in c['name']]
        if matched:
            logger.info(f"'{keyword}': {len(matched)}个 - {', '.join(matched[:5])}")
    
    return [(c['name'], c['leading_code']) for c in concepts]


def investigate_kpl_concepts(mysql: MySQLConnector):
    """调查开盘啦题材"""
    logger.info("\n=== 开盘啦题材调查 ===")
    
    # 查询所有题材
    query = """
    SELECT DISTINCT name, ts_code
    FROM tu_kpl_concept_cons
    WHERE 1=1
    ORDER BY name
    """
    
    concepts = mysql.execute_query(query)
    logger.info(f"开盘啦题材总数: {len(concepts)}")
    
    # 显示部分题材
    logger.info("\n前20个题材:")
    for i, concept in enumerate(concepts[:20], 1):
        logger.info(f"{i}. {concept['name']} ({concept['ts_code']})")
    
    # 查找包含特定关键词的题材
    keywords = ['储能', '新能源', '电池', '光伏', '风电', '汽车', '银行', '医药']
    logger.info("\n关键词匹配:")
    for keyword in keywords:
        matched = [c['name'] for c in concepts if keyword in c['name']]
        if matched:
            logger.info(f"'{keyword}': {len(matched)}个 - {', '.join(matched[:5])}")
    
    # 检查成分股表是否有数据
    check_query = """
    SELECT COUNT(*) as count
    FROM tu_kpl_concept_cons
    LIMIT 1
    """
    result = mysql.execute_query(check_query)
    if result:
        logger.info(f"\n开盘啦成分股表记录数: {result[0]['count']}")
    
    return [(c['name'], c['ts_code']) for c in concepts]


def find_common_concepts(ths_concepts, dc_concepts, kpl_concepts):
    """找到通用概念"""
    logger.info("\n=== 查找通用概念 ===")
    
    # 提取概念名称
    ths_names = set(name for name, _ in ths_concepts)
    dc_names = set(name for name, _ in dc_concepts)
    kpl_names = set(name for name, _ in kpl_concepts)
    
    # 找交集
    common_all = ths_names & dc_names & kpl_names
    common_ths_dc = (ths_names & dc_names) - common_all
    common_ths_kpl = (ths_names & kpl_names) - common_all
    common_dc_kpl = (dc_names & kpl_names) - common_all
    
    logger.info(f"三个数据源都有: {len(common_all)}个")
    if common_all:
        logger.info(f"示例: {list(common_all)[:5]}")
    
    logger.info(f"\n同花顺+东财共有: {len(common_ths_dc)}个")
    if common_ths_dc:
        logger.info(f"示例: {list(common_ths_dc)[:5]}")
    
    logger.info(f"\n同花顺+开盘啦共有: {len(common_ths_kpl)}个")
    if common_ths_kpl:
        logger.info(f"示例: {list(common_ths_kpl)[:5]}")
    
    logger.info(f"\n东财+开盘啦共有: {len(common_dc_kpl)}个")
    if common_dc_kpl:
        logger.info(f"示例: {list(common_dc_kpl)[:5]}")
    
    # 找独有概念
    unique_ths = ths_names - dc_names - kpl_names
    unique_dc = dc_names - ths_names - kpl_names
    unique_kpl = kpl_names - ths_names - dc_names
    
    logger.info(f"\n同花顺独有: {len(unique_ths)}个")
    if unique_ths:
        logger.info(f"示例: {list(unique_ths)[:5]}")
    
    logger.info(f"\n东财独有: {len(unique_dc)}个")
    if unique_dc:
        logger.info(f"示例: {list(unique_dc)[:5]}")
    
    logger.info(f"\n开盘啦独有: {len(unique_kpl)}个")
    if unique_kpl:
        logger.info(f"示例: {list(unique_kpl)[:5]}")
    
    return {
        'common_all': list(common_all),
        'common_ths_dc': list(common_ths_dc),
        'common_ths_kpl': list(common_ths_kpl),
        'common_dc_kpl': list(common_dc_kpl),
        'unique_ths': list(unique_ths)[:10],
        'unique_dc': list(unique_dc)[:10],
        'unique_kpl': list(unique_kpl)[:10]
    }


def analyze_naming_patterns():
    """分析命名模式差异"""
    logger.info("\n=== 命名模式分析 ===")
    
    patterns = {
        '同花顺': [
            '储能概念', '新能源汽车', '光伏概念', '风电', '锂电池',
            '充电桩', '特高压', '智能电网', 'BIPV概念', '钠电池'
        ],
        '东财': [
            '储能', '新能源车', '光伏设备', '风电设备', '锂电池概念',
            '充电桩', '特高压', '智能电网', '光伏建筑一体化', '钠离子电池'
        ],
        '开盘啦': [
            '储能', '新能源汽车', '光伏', '风电', '锂电池',
            '充电桩', '特高压', '智能电网', 'BIPV', '钠电池'
        ]
    }
    
    logger.info("命名差异示例:")
    concepts = ['储能', '新能源汽车', '光伏', 'BIPV', '钠电池']
    for concept in concepts:
        logger.info(f"\n{concept}相关:")
        logger.info(f"  同花顺: {[p for p in patterns['同花顺'] if concept in p]}")
        logger.info(f"  东财: {[p for p in patterns['东财'] if concept in p]}")
        logger.info(f"  开盘啦: {[p for p in patterns['开盘啦'] if concept in p]}")


def suggest_test_cases(common_concepts):
    """建议测试用例"""
    logger.info("\n=== 建议的测试用例 ===")
    
    # 通用测试用例
    logger.info("\n1. 通用测试用例（优先选择）:")
    if common_concepts['common_all']:
        for concept in common_concepts['common_all'][:5]:
            logger.info(f"   - {concept}")
    else:
        logger.info("   暂无三个数据源都有的概念")
    
    # 两两共有测试用例
    logger.info("\n2. 两两共有测试用例:")
    if common_concepts['common_ths_dc']:
        logger.info(f"   同花顺+东财: {common_concepts['common_ths_dc'][0]}")
    if common_concepts['common_ths_kpl']:
        logger.info(f"   同花顺+开盘啦: {common_concepts['common_ths_kpl'][0]}")
    if common_concepts['common_dc_kpl']:
        logger.info(f"   东财+开盘啦: {common_concepts['common_dc_kpl'][0]}")
    
    # 独有测试用例
    logger.info("\n3. 独有测试用例:")
    if common_concepts['unique_ths']:
        logger.info(f"   同花顺独有: {common_concepts['unique_ths'][0]}")
    if common_concepts['unique_dc']:
        logger.info(f"   东财独有: {common_concepts['unique_dc'][0]}")
    if common_concepts['unique_kpl']:
        logger.info(f"   开盘啦独有: {common_concepts['unique_kpl'][0]}")


def main():
    """主函数"""
    mysql = MySQLConnector()
    
    try:
        # 调查各数据源
        ths_concepts = investigate_ths_concepts(mysql)
        dc_concepts = investigate_dc_concepts(mysql)
        kpl_concepts = investigate_kpl_concepts(mysql)
        
        # 分析共同点和差异
        common_concepts = find_common_concepts(ths_concepts, dc_concepts, kpl_concepts)
        
        # 分析命名模式
        analyze_naming_patterns()
        
        # 建议测试用例
        suggest_test_cases(common_concepts)
        
        # 保存结果
        import json
        with open('data_source_investigation_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'ths_count': len(ths_concepts),
                'dc_count': len(dc_concepts),
                'kpl_count': len(kpl_concepts),
                'common_concepts': common_concepts,
                'timestamp': '2025-07-18'
            }, f, ensure_ascii=False, indent=2)
        
        logger.info("\n调查结果已保存到: data_source_investigation_results.json")
        
    except Exception as e:
        logger.error(f"调查失败: {e}", exc_info=True)
    finally:
        mysql.close()


if __name__ == "__main__":
    main()