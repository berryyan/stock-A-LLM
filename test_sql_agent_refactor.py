"""
测试SQL Agent重构功能

验证Phase 1.3重构后的功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = setup_logger("test_refactor")

def test_refactored_sql_agent():
    """测试重构后的SQL Agent"""
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试用例 - 覆盖各种查询类型
    test_queries = [
        # 1. 股价查询（需要股票代码和日期）
        ("贵州茅台最新股价", "股价查询"),
        ("中国平安昨天的股价", "股价查询"),
        
        # 2. 涨跌幅排名（支持中文数字）
        ("涨幅前十", "涨跌幅排名"),
        ("跌幅前五", "涨跌幅排名"),
        
        # 3. 市值排名
        ("市值排名前二十", "市值排名"),
        ("流通市值TOP十", "流通市值排名"),
        
        # 4. 成交额/成交量排名
        ("成交额前十", "成交额排名"),
        ("成交量前二十", "成交量排名"),
        
        # 5. PE/PB排名（测试方向判断）
        ("PE最高前十", "PE排名"),
        ("PB最低前五", "PB排名"),
        
        # 6. 个股主力资金
        ("贵州茅台的主力资金", "个股主力资金"),
        
        # 7. 板块主力资金
        ("银行板块的主力资金", "板块主力资金"),
        
        # 8. 财务查询
        ("贵州茅台的利润", "利润查询"),
        
        # 9. 错误处理测试
        ("不存在的股票的股价", "错误处理"),
        ("", "空查询"),
    ]
    
    # 测试结果统计
    results = {
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    print("\n" + "="*80)
    print("SQL Agent 重构功能测试")
    print("="*80 + "\n")
    
    for query, test_type in test_queries:
        print(f"\n测试类型: {test_type}")
        print(f"查询: {query}")
        print("-" * 50)
        
        try:
            # 执行查询
            result = sql_agent.query(query)
            
            if result['success']:
                print("✓ 成功")
                
                # 检查是否使用了快速路径
                if result.get('quick_path'):
                    print(f"  使用快速路径 - 模板: {result.get('template', 'N/A')}")
                    if result.get('execution_time'):
                        print(f"  执行时间: {result['execution_time']}")
                else:
                    print("  使用LLM路径")
                
                # 检查错误类型
                if result.get('error_type'):
                    print(f"  错误类型: {result['error_type']}")
                
                # 显示部分结果
                result_content = result.get('result', '')
                if result_content:
                    result_lines = str(result_content).split('\n')[:3]
                    for line in result_lines:
                        if line.strip():
                            print(f"  {line}")
                
                results["success"] += 1
            else:
                error_msg = result.get('error', '未知错误')
                error_type = result.get('error_type', 'UNKNOWN')
                print(f"✗ 失败: {error_msg}")
                print(f"  错误类型: {error_type}")
                
                # 对于某些预期的错误（如空查询），也算成功
                if test_type in ["错误处理", "空查询"] and not result['success']:
                    print("  (预期的错误处理)")
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "query": query,
                        "error": error_msg,
                        "type": error_type
                    })
                
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            results["failed"] += 1
            results["errors"].append({
                "query": query,
                "error": str(e),
                "type": "EXCEPTION"
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
            print(f"- {error['query']}: {error['error']} (类型: {error['type']})")
    
    # 测试特定功能
    print("\n" + "="*80)
    print("特定功能测试")
    print("="*80)
    
    # 测试中文数字支持
    print("\n1. 中文数字支持测试:")
    for query in ["涨幅前十", "涨幅前二十", "涨幅前五十"]:
        result = sql_agent.query(query)
        if result['success'] and result.get('result'):
            result_content = result['result']
            if '条记录' in result_content:
                import re
                count_match = re.search(r'共(\d+)条记录', result_content)
                if count_match:
                    actual_count = int(count_match.group(1))
                    print(f"  '{query}' -> 返回{actual_count}条记录")
            else:
                # 尝试从结果中找到行数
                lines = result_content.strip().split('\n')
                # 查找表格行
                table_lines = [line for line in lines if line.strip().startswith('|') and not line.strip().startswith('|--')]
                if table_lines:
                    # 减去表头行
                    data_rows = len(table_lines) - 1
                    if data_rows > 0:
                        print(f"  '{query}' -> 返回{data_rows}条记录")
    
    return results

if __name__ == "__main__":
    test_refactored_sql_agent()