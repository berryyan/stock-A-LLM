"""
测试SQL Agent中文数字支持功能

测试用例包括：
1. 基本中文数字："前十"、"前二十"
2. 混合表达："TOP二十"、"前一百名"
3. 实际查询："涨幅前十的股票"、"市值排名前二十"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = setup_logger("test_chinese_number")

def test_chinese_number_queries():
    """测试中文数字查询"""
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试用例
    test_queries = [
        # 基本中文数字测试
        ("涨幅前十", "涨幅排名前10（中文数字）"),
        ("涨幅前二十", "涨幅排名前20（中文数字）"),
        ("跌幅前五", "跌幅排名前5（中文数字）"),
        
        # TOP格式测试
        ("TOP十的股票", "TOP10（中文数字）"),
        ("TOP二十涨幅", "TOP20涨幅（中文数字）"),
        
        # 市值排名测试
        ("市值排名前十", "市值排名前10（中文数字）"),
        ("总市值前二十", "总市值前20（中文数字）"),
        ("流通市值前十五", "流通市值前15（中文数字）"),
        
        # 成交额/成交量测试
        ("成交额前十", "成交额前10（中文数字）"),
        ("成交量前二十", "成交量前20（中文数字）"),
        
        # 财务指标测试
        ("PE最高前十", "PE最高前10（中文数字）"),
        ("净利润排名前二十", "净利润排名前20（中文数字）"),
        ("ROE最高前十五", "ROE最高前15（中文数字）"),
        
        # 资金流向测试
        ("主力净流入前十", "主力净流入前10（中文数字）"),
        ("主力净流出前二十", "主力净流出前20（中文数字）"),
        
        # 混合测试（对比阿拉伯数字）
        ("涨幅前10", "涨幅排名前10（阿拉伯数字）"),
        ("市值排名前30", "市值排名前30（阿拉伯数字）"),
    ]
    
    # 测试结果统计
    results = {
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    print("\n" + "="*80)
    print("SQL Agent 中文数字支持测试")
    print("="*80 + "\n")
    
    for query, description in test_queries:
        print(f"\n测试: {description}")
        print(f"查询: {query}")
        print("-" * 50)
        
        try:
            # 执行查询
            result = sql_agent.query(query)
            
            if result['success']:
                # 检查是否使用了快速路径
                if result.get('quick_path'):
                    print("✓ 成功 - 使用快速路径")
                    
                    # 尝试从结果中提取实际返回的记录数
                    result_text = result.get('result', '')
                    if '共' in result_text and '条记录' in result_text:
                        import re
                        count_match = re.search(r'共(\d+)条记录', result_text)
                        if count_match:
                            actual_count = int(count_match.group(1))
                            print(f"  实际返回记录数: {actual_count}")
                else:
                    print("✓ 成功 - 使用LLM路径")
                
                # 显示部分结果
                result_lines = result['result'].split('\n')[:5]
                for line in result_lines:
                    if line.strip():
                        print(f"  {line}")
                
                results["success"] += 1
            else:
                print(f"✗ 失败: {result.get('error', '未知错误')}")
                results["failed"] += 1
                results["errors"].append({
                    "query": query,
                    "error": result.get('error')
                })
                
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            results["failed"] += 1
            results["errors"].append({
                "query": query,
                "error": str(e)
            })
    
    # 打印测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"成功: {results['success']}")
    print(f"失败: {results['failed']}")
    print(f"总计: {results['success'] + results['failed']}")
    print(f"成功率: {results['success'] / (results['success'] + results['failed']) * 100:.1f}%")
    
    if results["errors"]:
        print("\n失败详情:")
        for error in results["errors"]:
            print(f"- {error['query']}: {error['error']}")
    
    return results

if __name__ == "__main__":
    test_chinese_number_queries()