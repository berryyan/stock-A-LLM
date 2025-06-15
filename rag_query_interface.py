"""
股票公告RAG智能查询界面
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import DocumentProcessor
from database.mysql_connector import MySQLConnector
import json
from datetime import datetime
from typing import List, Dict


class RAGQueryInterface:
    """RAG查询界面"""
    
    def __init__(self):
        print("初始化RAG系统...")
        self.processor = DocumentProcessor()
        self.mysql = MySQLConnector()
        print("✓ 系统初始化完成\n")
    
    def search_announcements(self, query: str, top_k: int = 5, ts_codes: List[str] = None):
        """搜索公告"""
        print(f"\n查询: '{query}'")
        print("-" * 60)
        
        try:
            results = self.processor.search_similar_documents(
                query=query,
                top_k=top_k,
                ts_codes=ts_codes
            )
            
            if results and len(results) > 0:
                # 处理结果格式
                if isinstance(results[0], list):
                    hits = results[0]
                else:
                    hits = results
                
                print(f"找到 {len(hits)} 个相关文档片段\n")
                
                # 按公司分组显示结果
                company_results = {}
                for hit in hits:
                    entity = hit.entity
                    ts_code = entity.ts_code if hasattr(entity, 'ts_code') else 'N/A'
                    
                    if ts_code not in company_results:
                        company_results[ts_code] = []
                    
                    company_results[ts_code].append({
                        'score': hit.distance,
                        'title': entity.title if hasattr(entity, 'title') else 'N/A',
                        'text': entity.text if hasattr(entity, 'text') else '',
                        'chunk_id': entity.chunk_id if hasattr(entity, 'chunk_id') else 0,
                        'ann_date': entity.ann_date if hasattr(entity, 'ann_date') else 'N/A'
                    })
                
                # 显示结果
                for ts_code, docs in company_results.items():
                    # 获取公司名称
                    company_name = self._get_company_name(ts_code)
                    print(f"\n【{ts_code} - {company_name}】")
                    
                    # 按相似度排序
                    docs.sort(key=lambda x: x['score'], reverse=True)
                    
                    for i, doc in enumerate(docs[:3]):  # 每个公司最多显示3个片段
                        print(f"\n  片段{i+1} (相似度: {doc['score']:.4f}):")
                        print(f"  文档: {doc['title']} ({doc['ann_date']})")
                        print(f"  内容: {doc['text'][:200]}...")
                
                return company_results
            else:
                print("没有找到相关文档")
                return {}
                
        except Exception as e:
            print(f"搜索错误: {e}")
            return {}
    
    def _get_company_name(self, ts_code: str) -> str:
        """获取公司名称"""
        try:
            query = f"SELECT name FROM tu_anns_d WHERE ts_code = '{ts_code}' LIMIT 1"
            result = self.mysql.execute_query(query)
            return result[0]['name'] if result else ts_code
        except:
            return ts_code
    
    def financial_analysis(self, ts_codes: List[str] = None):
        """财务数据分析查询"""
        print("\n" + "="*60)
        print("财务数据智能分析")
        print("="*60)
        
        queries = [
            "2024年营业收入和净利润情况",
            "主营业务收入构成和变化",
            "毛利率和净利率分析",
            "研发投入占营业收入比例",
            "经营活动现金流量情况"
        ]
        
        for query in queries:
            self.search_announcements(query, top_k=3, ts_codes=ts_codes)
    
    def compare_companies(self, ts_codes: List[str], metric: str):
        """对比多家公司"""
        print("\n" + "="*60)
        print(f"公司对比分析: {metric}")
        print(f"对比公司: {', '.join(ts_codes)}")
        print("="*60)
        
        self.search_announcements(metric, top_k=10, ts_codes=ts_codes)
    
    def industry_trends(self, keywords: List[str]):
        """行业趋势分析"""
        print("\n" + "="*60)
        print("行业趋势分析")
        print("="*60)
        
        for keyword in keywords:
            query = f"行业发展趋势 {keyword}"
            self.search_announcements(query, top_k=5)


def interactive_mode():
    """交互式查询模式"""
    rag = RAGQueryInterface()
    
    print("\n股票公告RAG智能查询系统")
    print("="*60)
    print("输入查询内容，或输入以下命令：")
    print("  /help     - 显示帮助")
    print("  /company  - 指定公司查询")
    print("  /finance  - 财务分析")
    print("  /compare  - 公司对比")
    print("  /quit     - 退出")
    print("="*60)
    
    current_companies = None
    
    while True:
        try:
            user_input = input("\n查询> ").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith('/'):
                # 处理命令
                command = user_input.lower()
                
                if command == '/quit':
                    print("再见！")
                    break
                
                elif command == '/help':
                    print("\n查询示例：")
                    print("  - 2024年营业收入情况")
                    print("  - 净利润同比增长")
                    print("  - 研发投入占比")
                    print("  - 主营业务构成")
                    print("  - 未来发展战略")
                
                elif command == '/company':
                    codes = input("输入股票代码（用逗号分隔）: ").strip()
                    if codes:
                        current_companies = [c.strip() for c in codes.split(',')]
                        print(f"已设定查询公司: {current_companies}")
                    else:
                        current_companies = None
                        print("已清除公司限制")
                
                elif command == '/finance':
                    rag.financial_analysis(current_companies)
                
                elif command == '/compare':
                    if not current_companies or len(current_companies) < 2:
                        print("请先使用 /company 设定至少2家公司")
                    else:
                        metric = input("对比指标（如：营业收入、净利润、毛利率）: ").strip()
                        if metric:
                            rag.compare_companies(current_companies, metric)
                
                else:
                    print(f"未知命令: {command}")
            
            else:
                # 普通查询
                rag.search_announcements(user_input, top_k=5, ts_codes=current_companies)
                
        except KeyboardInterrupt:
            print("\n\n用户中断")
            break
        except Exception as e:
            print(f"\n错误: {e}")


def demo_queries():
    """演示查询"""
    rag = RAGQueryInterface()
    
    print("\n" + "="*60)
    print("RAG系统演示查询")
    print("="*60)
    
    # 演示1：基本查询
    print("\n1. 基本财务查询")
    rag.search_announcements("2024年度营业收入和净利润", top_k=3)
    
    # 演示2：特定公司查询
    print("\n\n2. 特定公司查询")
    rag.search_announcements(
        "主营业务收入构成", 
        top_k=3, 
        ts_codes=['300607.SZ', '300290.SZ']
    )
    
    # 演示3：对比分析
    print("\n\n3. 公司对比分析")
    rag.compare_companies(
        ['300607.SZ', '300290.SZ', '300207.SZ'],
        "研发投入"
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        # 运行演示
        demo_queries()
    else:
        # 交互模式
        interactive_mode()
