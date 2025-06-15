#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析数据库中的公告标题模式，帮助优化内容过滤规则
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from collections import Counter
import re
from datetime import datetime, timedelta


class TitleAnalyzer:
    """公告标题分析器"""
    
    def __init__(self):
        self.mysql = MySQLConnector()
        
        # 核心报告类型关键词
        self.core_keywords = {
            '年度报告': ['年度报告', '年报'],
            '季度报告': ['第一季度', '第二季度', '第三季度', '第四季度', '一季报', '二季报', '三季报', '四季报', '季度报告'],
            '半年报告': ['半年度报告', '半年报', '中期报告'],
            '业绩预告': ['业绩预告', '业绩预增', '业绩预减', '业绩预盈', '业绩预亏'],
            '业绩快报': ['业绩快报'],
            '报告摘要': ['报告摘要', '摘要']
        }
        
        # 扩展内容类型关键词
        self.extended_keywords = {
            '并购重组': ['收购', '并购', '重组', '合并', '资产重组', '重大资产'],
            '问询回复': ['问询函', '监管函', '关注函', '问询回复', '监管问询'],
            '处罚警示': ['处罚', '警示', '批评', '谴责', '违规'],
            '停复牌': ['停牌', '复牌', '暂停', '恢复'],
            '分红派息': ['分红', '派息', '利润分配', '股息', '红利'],
            '股权激励': ['股权激励', '期权', '限制性股票'],
            '重大合同': ['重大合同', '合同公告', '中标'],
            '人事变动': ['董事', '监事', '高管', '辞职', '聘任', '变更']
        }
    
    def analyze_recent_titles(self, days=30):
        """分析最近N天的公告标题"""
        print(f"\n分析最近{days}天的公告标题")
        print("=" * 80)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
        SELECT title, COUNT(*) as count
        FROM tu_anns_d
        WHERE ann_date BETWEEN '{start_date.strftime('%Y%m%d')}' AND '{end_date.strftime('%Y%m%d')}'
        GROUP BY title
        ORDER BY count DESC
        """
        
        results = self.mysql.execute_query(query)
        
        # 分类统计
        categorized = {
            '核心报告': [],
            '扩展内容': [],
            '其他': []
        }
        
        for r in results:
            title = r['title']
            count = r['count']
            
            # 检查核心类型
            matched = False
            for category, keywords in self.core_keywords.items():
                if any(kw in title for kw in keywords):
                    categorized['核心报告'].append((title, count, category))
                    matched = True
                    break
            
            # 检查扩展类型
            if not matched:
                for category, keywords in self.extended_keywords.items():
                    if any(kw in title for kw in keywords):
                        categorized['扩展内容'].append((title, count, category))
                        matched = True
                        break
            
            # 其他
            if not matched:
                categorized['其他'].append((title, count, '未分类'))
        
        # 输出统计结果
        for cat_name, items in categorized.items():
            print(f"\n{cat_name} (共{len(items)}种):")
            print("-" * 60)
            
            # 按类别统计
            cat_counter = Counter()
            for _, count, category in items:
                cat_counter[category] += count
            
            for category, total in cat_counter.most_common(10):
                print(f"  {category}: {total}条")
        
        # 显示常见的"其他"类型
        print("\n常见的其他类型公告:")
        print("-" * 60)
        for title, count, _ in sorted(categorized['其他'], key=lambda x: x[1], reverse=True)[:20]:
            print(f"  [{count:3d}] {title[:50]}...")
    
    def analyze_title_patterns(self):
        """分析标题模式"""
        print("\n分析标题模式")
        print("=" * 80)
        
        # 获取一些样本
        query = """
        SELECT DISTINCT title
        FROM tu_anns_d
        WHERE ann_date >= '20250401'
        LIMIT 1000
        """
        
        results = self.mysql.execute_query(query)
        
        # 提取常见模式
        patterns = {
            '年度报告完整': 0,
            '年度报告摘要': 0,
            '季度报告': 0,
            '更正/补充公告': 0,
            '英文版': 0,
            '问询/监管函': 0,
            '会计师事务所公告': 0,
            '券商/保荐机构公告': 0
        }
        
        for r in results:
            title = r['title']
            
            if '年度报告' in title and '摘要' not in title and '更正' not in title:
                patterns['年度报告完整'] += 1
            elif '年度报告摘要' in title:
                patterns['年度报告摘要'] += 1
            elif any(kw in title for kw in ['季度报告', '季报']):
                patterns['季度报告'] += 1
            elif any(kw in title for kw in ['更正', '补充', '修订']):
                patterns['更正/补充公告'] += 1
            elif '英文版' in title or 'English' in title:
                patterns['英文版'] += 1
            elif any(kw in title for kw in ['问询', '监管函', '关注函']):
                patterns['问询/监管函'] += 1
            elif '会计师事务所' in title:
                patterns['会计师事务所公告'] += 1
            elif any(kw in title for kw in ['证券', '保荐']):
                patterns['券商/保荐机构公告'] += 1
        
        print("\n标题模式统计:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count}")
    
    def suggest_filters(self):
        """建议的过滤规则"""
        print("\n建议的标题过滤规则")
        print("=" * 80)
        
        print("\n1. 核心报告类型（严格匹配）:")
        print("   必须包含以下关键词之一，且不包含排除词:")
        print("   - 年度报告: 包含'年度报告'或'年报'，排除'摘要'、'英文'、'更正'、'关于'")
        print("   - 季度报告: 包含'第X季度'或'X季报'，排除'摘要'、'英文'、'更正'")
        print("   - 业绩快报/预告: 包含'业绩快报'或'业绩预'")
        
        print("\n2. 扩展内容类型（宽松匹配）:")
        print("   - 重大事项: 收购、并购、重组、重大合同")
        print("   - 监管相关: 问询函回复、监管函件回复")
        print("   - 分红相关: 利润分配、分红派息")
        
        print("\n3. 建议排除的内容:")
        print("   - 会议通知、提示性公告")
        print("   - 网上说明会公告")
        print("   - 单纯的更正公告（除非是重要报告的更正）")
        print("   - 英文版报告（如果不需要）")


def main():
    analyzer = TitleAnalyzer()
    
    # 分析最近270天（约一年的交易日）
    analyzer.analyze_recent_titles(270)
    
    # 分析标题模式
    analyzer.analyze_title_patterns()
    
    # 给出建议
    analyzer.suggest_filters()
    
    # 额外分析：年报季报的详细分布
    print("\n\n年报和季报的详细分析")
    print("=" * 80)
    
    # 分析年报
    query_yearly = """
    SELECT title, COUNT(*) as count
    FROM tu_anns_d
    WHERE ann_date >= '20240101'
    AND (title LIKE '%年度报告%' OR title LIKE '%年报%')
    GROUP BY title
    ORDER BY count DESC
    LIMIT 50
    """
    
    yearly_results = analyzer.mysql.execute_query(query_yearly)
    
    print("\n年度报告类型分布（前50）:")
    for r in yearly_results:
        print(f"  [{r['count']:3d}] {r['title']}")
    
    # 分析季报
    query_quarterly = """
    SELECT title, COUNT(*) as count
    FROM tu_anns_d
    WHERE ann_date >= '20240101'
    AND (title LIKE '%季度报告%' OR title LIKE '%季报%')
    GROUP BY title
    ORDER BY count DESC
    LIMIT 50
    """
    
    quarterly_results = analyzer.mysql.execute_query(query_quarterly)
    
    print("\n\n季度报告类型分布（前50）:")
    for r in quarterly_results:
        print(f"  [{r['count']:3d}] {r['title']}")
    
    # 分析业绩相关
    query_performance = """
    SELECT title, COUNT(*) as count
    FROM tu_anns_d
    WHERE ann_date >= '20240101'
    AND (title LIKE '%业绩%' OR title LIKE '%盈利%' OR title LIKE '%亏损%')
    GROUP BY title
    ORDER BY count DESC
    LIMIT 30
    """
    
    performance_results = analyzer.mysql.execute_query(query_performance)
    
    print("\n\n业绩相关公告分布（前30）:")
    for r in performance_results:
        print(f"  [{r['count']:3d}] {r['title']}")
    
    # 询问是否要看更多
    if input("\n是否分析特定日期的公告? (y/n): ").lower() == 'y':
        date = input("输入日期 (YYYYMMDD): ")
        
        query = f"""
        SELECT ts_code, name, title
        FROM tu_anns_d
        WHERE ann_date = '{date}'
        ORDER BY ts_code
        """
        
        results = analyzer.mysql.execute_query(query)
        
        print(f"\n{date} 的公告 (共{len(results)}条):")
        print("=" * 80)
        
        for r in results[:50]:  # 只显示前50条
            print(f"{r['ts_code']} | {r['name'][:10]} | {r['title'][:60]}...")


if __name__ == "__main__":
    main()
