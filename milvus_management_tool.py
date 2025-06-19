"""
Milvus数据管理工具 - 完整版 v2.0
修复了删除功能中的chunks处理问题
整合了所有数据完整性维护功能：
- 查找和删除孤立主文档（没有chunks的主文档）
- 查找和删除孤立chunks（没有主文档的chunks）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from database.mysql_connector import MySQLConnector
from pathlib import Path
import json
from datetime import datetime
import time
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class MilvusManagementTool:
    def __init__(self):
        self.milvus = MilvusConnector()
        self.mysql = MySQLConnector()
        
    def normalize_date(self, date_input: str) -> Tuple[str, str]:
        """
        标准化日期格式
        输入：YYYYMMDD, YYYY-MM-DD, YYYY/MM/DD 等
        返回：(YYYYMMDD格式, YYYY-MM-DD格式)
        """
        # 清理输入
        date_input = date_input.strip()
        
        # 移除所有分隔符得到纯数字
        clean_date = date_input.replace('-', '').replace('/', '').replace('.', '').replace(' ', '')
        
        # 验证是否为8位数字
        if len(clean_date) != 8 or not clean_date.isdigit():
            raise ValueError(f"无效的日期格式: {date_input}")
            
        # 生成两种格式
        yyyymmdd = clean_date
        yyyy_mm_dd = f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:8]}"
        
        return yyyymmdd, yyyy_mm_dd
        
    def search_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict]:
        """按关键词搜索 - 改进版，支持更灵活的匹配"""
        print(f"\n搜索包含 '{keyword}' 的记录...")
        
        try:
            # 对于年度报告类关键词，特殊处理
            if "年度报告" in keyword or "年报" in keyword:
                # 提取年份
                year = None
                for y in range(2020, 2030):
                    if str(y) in keyword:
                        year = str(y)
                        break
                        
                if year:
                    # 搜索包含年份和报告关键词的记录
                    expr = f'(title like "%{year}%年度报告%" or title like "%{year}%年报%") and chunk_id == 0'
                else:
                    # 搜索所有年度报告
                    expr = f'(title like "%年度报告%" or title like "%年报%") and chunk_id == 0'
            else:
                # 普通关键词搜索
                expr = f'title like "%{keyword}%" and chunk_id == 0'
                
            results = self.milvus.collection.query(
                expr=expr,
                output_fields=["doc_id", "ts_code", "title", "ann_date", "chunk_id"],
                limit=limit
            )
            
            print(f"找到 {len(results)} 个主文档")
            return results
            
        except Exception as e:
            print(f"搜索出错: {e}")
            return []
            
    def search_by_date(self, date: str, limit: int = 16384) -> List[Dict]:
        """按日期搜索 - 智能处理日期格式"""
        print(f"\n搜索日期 {date} 的记录...")
        
        try:
            # 标准化日期
            yyyymmdd, yyyy_mm_dd = self.normalize_date(date)
            
            # 根据数据库实际格式（YYYY-MM-DD）进行搜索
            results = self.milvus.collection.query(
                expr=f'ann_date == "{yyyy_mm_dd}" and chunk_id == 0',
                output_fields=["doc_id", "ts_code", "title", "ann_date"],
                limit=limit
            )
            
            print(f"找到 {len(results)} 条记录")
            return results
            
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return []
        except Exception as e:
            print(f"搜索出错: {e}")
            return []
            
    def search_by_date_range(self, start_date: str, end_date: str, limit: int = 16384) -> List[Dict]:
        """按日期范围搜索"""
        print(f"\n搜索日期范围 {start_date} 至 {end_date} 的记录...")
        
        try:
            # 标准化日期
            _, start_yyyy_mm_dd = self.normalize_date(start_date)
            _, end_yyyy_mm_dd = self.normalize_date(end_date)
            
            # 构建查询表达式
            expr = f'ann_date >= "{start_yyyy_mm_dd}" and ann_date <= "{end_yyyy_mm_dd}" and chunk_id == 0'
            
            results = self.milvus.collection.query(
                expr=expr,
                output_fields=["doc_id", "ts_code", "title", "ann_date"],
                limit=limit
            )
            
            print(f"找到 {len(results)} 条记录")
            return results
            
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return []
        except Exception as e:
            print(f"搜索出错: {e}")
            return []
            
    def search_by_stock(self, ts_code: str, limit: int = 1000) -> List[Dict]:
        """按股票代码搜索"""
        print(f"\n搜索股票 {ts_code} 的记录...")
        
        try:
            results = self.milvus.collection.query(
                expr=f'ts_code == "{ts_code}" and chunk_id == 0',
                output_fields=["doc_id", "title", "ann_date"],
                limit=limit
            )
            
            print(f"找到 {len(results)} 条记录")
            return results
            
        except Exception as e:
            print(f"搜索出错: {e}")
            return []
            
    def delete_by_doc_ids(self, doc_ids: List[str], include_chunks: bool = True) -> int:
        """通过doc_id列表删除，包括相关的chunks"""
        if not doc_ids:
            print("没有要删除的记录")
            return 0
            
        # 如果需要包含chunks，先收集所有相关的doc_id
        if include_chunks:
            all_doc_ids = set()
            print("正在查找相关的chunks...")
            
            for doc_id in doc_ids:
                # 获取基础announcement_id
                if '_' in doc_id:
                    # doc_id格式: announcement_id_chunk_id
                    announcement_id = doc_id.split('_')[0]  # 修复：只取第一部分
                else:
                    announcement_id = doc_id
                    
                # 查找所有相关的文档和chunks
                try:
                    # 使用announcement_id查找所有相关记录
                    chunk_results = self.milvus.collection.query(
                        expr=f'doc_id like "{announcement_id}_%"',  # 修复：查找announcement_id_*
                        output_fields=["doc_id"],
                        limit=1000
                    )
                    
                    # 添加所有找到的doc_id
                    for chunk in chunk_results:
                        all_doc_ids.add(chunk['doc_id'])
                        
                    # 如果没找到任何chunks，至少保留原始doc_id
                    if not chunk_results:
                        all_doc_ids.add(doc_id)
                        
                except Exception as e:
                    print(f"查找chunks时出错: {e}")
                    all_doc_ids.add(doc_id)
                    
            doc_ids = list(all_doc_ids)
            print(f"找到 {len(doc_ids)} 条相关记录（包括chunks）")
            
        print(f"\n准备删除 {len(doc_ids)} 条记录")
        
        # 分批删除
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(doc_ids), batch_size):
            batch = doc_ids[i:i+batch_size]
            
            # 构建删除表达式
            doc_id_list = ', '.join([f'"{doc_id}"' for doc_id in batch])
            expr = f'doc_id in [{doc_id_list}]'
            
            try:
                self.milvus.collection.delete(expr)
                deleted_count += len(batch)
                print(f"  批次 {i//batch_size + 1}: 删除 {len(batch)} 条")
                
                # flush确保生效
                self.milvus.collection.flush()
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  删除失败: {e}")
                
        print(f"总共删除了 {deleted_count} 条记录")
        return deleted_count
        
    def delete_by_keyword(self, keyword: str) -> int:
        """按关键词删除，包括所有相关chunks"""
        # 先搜索
        results = self.search_by_keyword(keyword, limit=16384)
        
        if not results:
            print("没有找到匹配的记录")
            return 0
            
        # 收集主文档的doc_id
        main_doc_ids = [r['doc_id'] for r in results]
        
        # 显示示例
        print("\n将删除的记录示例:")
        for i, r in enumerate(results[:5]):
            print(f"  {i+1}. {r['ts_code']} - {r['title'][:50]}... - {r['ann_date']}")
        if len(results) > 5:
            print(f"  ... 还有 {len(results)-5} 条")
        
        # 确认删除
        response = input(f"\n确认删除这些记录及其相关chunks? (yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
            
        return self.delete_by_doc_ids(main_doc_ids, include_chunks=True)
        
    def delete_by_date(self, date: str) -> int:
        """按日期删除"""
        results = self.search_by_date(date, limit=16384)
        
        if not results:
            print("没有找到匹配的记录")
            return 0
            
        # 显示将删除的记录摘要
        print(f"\n将删除 {date} 的以下记录:")
        
        # 按股票代码分组统计
        stock_counts = defaultdict(int)
        for r in results:
            stock_counts[r['ts_code']] += 1
            
        # 显示前10个股票
        for i, (stock, count) in enumerate(sorted(stock_counts.items())[:10]):
            print(f"  {stock}: {count} 条")
        if len(stock_counts) > 10:
            print(f"  ... 还有 {len(stock_counts)-10} 只股票")
            
        # 收集doc_id
        doc_ids = [r['doc_id'] for r in results]
        
        # 确认删除
        response = input(f"\n确认删除 {date} 的 {len(doc_ids)} 条记录及其相关chunks? (yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
            
        return self.delete_by_doc_ids(doc_ids, include_chunks=True)
        
    def get_statistics(self):
        """获取详细统计信息"""
        print("\n=== Milvus统计信息 ===")
        
        stats = self.milvus.get_collection_stats()
        print(f"总记录数: {stats['row_count']:,} (包含所有chunks)")
        
        # 统计主文档数
        try:
            # 获取所有主文档
            main_docs_count = 0
            batch_size = 1000
            offset = 0
            
            print("\n正在统计主文档数...")
            while True:
                results = self.milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id"],
                    offset=offset,
                    limit=batch_size
                )
                
                if not results:
                    break
                    
                main_docs_count += len(results)
                offset += batch_size
                
                if len(results) < batch_size:
                    break
                    
            print(f"主文档数: {main_docs_count:,}")
            
            # 计算平均chunks数
            if main_docs_count > 0:
                avg_chunks = stats['row_count'] / main_docs_count
                print(f"平均每个文档的chunks数: {avg_chunks:.1f}")
                
        except Exception as e:
            print(f"统计主文档时出错: {e}")
            
        # 获取日期范围
        print("\n获取日期范围...")
        try:
            # 获取一些样本来确定日期范围
            sample_size = 1000
            sample = self.milvus.collection.query(
                expr="chunk_id == 0",
                output_fields=["ann_date"],
                limit=sample_size
            )
            
            if sample:
                dates = [r.get('ann_date', '') for r in sample if r.get('ann_date')]
                if dates:
                    dates.sort()
                    earliest = dates[0]
                    latest = dates[-1]
                    
                    # 转换日期格式显示
                    try:
                        earliest_display = earliest.replace('-', '')
                        latest_display = latest.replace('-', '')
                        print(f"日期范围: {earliest_display} 至 {latest_display}")
                        print(f"日期格式: {dates[0]} (YYYY-MM-DD)")
                    except:
                        print(f"日期范围: {earliest} 至 {latest}")
                        
        except Exception as e:
            print(f"获取日期范围时出错: {e}")
        
        # 统计文档类型
        print("\n正在统计文档类型...")
        doc_types = self._analyze_document_types()
        
        print("\n文档类型分布:")
        total_typed = 0
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {doc_type}: {count:,} 个")
                total_typed += count
                
        # 按年份统计
        print("\n按年份统计...")
        year_stats = self._analyze_by_year()
        if year_stats:
            print("\n年份分布:")
            for year, count in sorted(year_stats.items(), reverse=True)[:10]:
                if count > 0:
                    print(f"  {year}年: {count:,} 个")
                    
        # 最近几天的统计
        print("\n最近7天的公告统计:")
        recent_stats = self._analyze_recent_days(7)
        for date, count in recent_stats:
            print(f"  {date}: {count:,} 个")
                
    def _analyze_document_types(self) -> Dict[str, int]:
        """分析文档类型分布"""
        doc_types = defaultdict(int)
        
        # 定义搜索模式
        search_patterns = [
            ('年度报告', ['年度报告', '年报']),
            ('季度报告', ['第一季度报告', '第三季度报告', '一季报', '三季报']),
            ('半年度报告', ['半年度报告', '半年报', '中期报告']),
            ('业绩预告', ['业绩预告']),
            ('业绩快报', ['业绩快报']),
            ('权益分派', ['权益分派', '利润分配', '分红']),
            ('股东大会', ['股东大会']),
            ('董事会决议', ['董事会决议']),
            ('公告', ['公告']),
        ]
        
        # 使用set来避免重复计数
        counted_docs = set()
        
        for doc_type, keywords in search_patterns:
            type_count = 0
            for kw in keywords:
                try:
                    results = self.milvus.collection.query(
                        expr=f'title like "%{kw}%" and chunk_id == 0',
                        output_fields=["doc_id", "title"],
                        limit=16384
                    )
                    
                    for r in results:
                        doc_id = r.get('doc_id', '')
                        if doc_id not in counted_docs:
                            # 检查是否真的匹配（避免子串匹配问题）
                            title = r.get('title', '')
                            if kw in title:
                                # 对于年度报告，排除摘要
                                if doc_type == '年度报告' and '摘要' in title:
                                    continue
                                type_count += 1
                                counted_docs.add(doc_id)
                                
                except Exception as e:
                    print(f"  搜索 '{kw}' 时出错: {e}")
                    
            doc_types[doc_type] = type_count
            
        return doc_types
        
    def _analyze_by_year(self) -> Dict[str, int]:
        """按年份分析文档分布"""
        year_stats = defaultdict(int)
        
        try:
            # 搜索包含年份的标题
            for year in range(2020, 2026):
                results = self.milvus.collection.query(
                    expr=f'title like "%{year}%" and chunk_id == 0',
                    output_fields=["doc_id"],
                    limit=16384
                )
                year_stats[str(year)] = len(results)
                
        except Exception as e:
            print(f"  按年份统计时出错: {e}")
            
        return year_stats
        
    def _analyze_recent_days(self, days: int) -> List[Tuple[str, int]]:
        """分析最近几天的数据"""
        from datetime import datetime, timedelta
        
        results = []
        today = datetime.now()
        
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            try:
                day_results = self.milvus.collection.query(
                    expr=f'ann_date == "{date_str}" and chunk_id == 0',
                    output_fields=["doc_id"],
                    limit=16384
                )
                results.append((date_str, len(day_results)))
            except:
                results.append((date_str, 0))
                
        return results
            
    def export_processed_records(self):
        """导出已处理记录到文件"""
        print("\n=== 导出已处理记录 ===")
        
        output_file = Path("data/processed_announcements.json")
        
        processed_ids = set()
        batch_size = 1000
        total_fetched = 0
        
        print("正在导出...")
        try:
            # 分批获取所有主文档
            offset = 0
            while True:
                results = self.milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id"],
                    offset=offset,
                    limit=batch_size
                )
                
                if not results:
                    break
                    
                for r in results:
                    doc_id = r.get('doc_id', '')
                    if '_' in doc_id:
                        ann_id = doc_id.split('_')[0]
                        processed_ids.add(ann_id)
                        
                total_fetched += len(results)
                offset += batch_size
                print(f"\r已处理: {len(processed_ids)} 个 (已扫描 {total_fetched} 条记录)", end='')
                
                # 如果结果少于批次大小，说明已经到最后了
                if len(results) < batch_size:
                    break
                    
        except Exception as e:
            print(f"\n查询出错: {e}")
            print(f"但已成功获取 {len(processed_ids)} 个ID")
                
        print(f"\n共导出 {len(processed_ids)} 个公告ID")
        
        # 保存到文件
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_ids': list(processed_ids),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(processed_ids),
                'source': 'milvus_export'
            }, f, ensure_ascii=False, indent=2)
            
        print(f"已保存到: {output_file}")
        
    def check_duplicates(self):
        """检查重复记录 - 改进版"""
        print("\n=== 检查重复记录 ===")
        
        # 批量获取所有主文档
        print("正在检查重复记录...")
        ann_id_counts = defaultdict(list)
        
        batch_size = 1000
        offset = 0
        total_checked = 0
        
        try:
            while True:
                results = self.milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id", "title", "ts_code", "ann_date"],
                    offset=offset,
                    limit=batch_size
                )
                
                if not results:
                    break
                    
                for r in results:
                    doc_id = r.get('doc_id', '')
                    if '_' in doc_id:
                        ann_id = doc_id.split('_')[0]
                        ann_id_counts[ann_id].append({
                            'doc_id': doc_id,
                            'title': r.get('title', ''),
                            'ts_code': r.get('ts_code', ''),
                            'ann_date': r.get('ann_date', '')
                        })
                        
                total_checked += len(results)
                offset += batch_size
                print(f"\r已检查 {total_checked} 条记录...", end='')
                
                if len(results) < batch_size:
                    break
                    
        except Exception as e:
            print(f"\n检查时出错: {e}")
            
        print(f"\n总共检查了 {total_checked} 条记录")
        
        # 找出重复的
        duplicates = {k: v for k, v in ann_id_counts.items() if len(v) > 1}
        
        if duplicates:
            print(f"\n发现 {len(duplicates)} 个重复的公告ID:")
            
            # 显示前10个重复记录的详细信息
            for i, (ann_id, records) in enumerate(list(duplicates.items())[:10]):
                print(f"\n{i+1}. 公告ID: {ann_id} (重复 {len(records)} 次)")
                
                # 按股票代码和日期分组
                by_stock = defaultdict(list)
                for rec in records:
                    key = f"{rec['ts_code']} - {rec['ann_date']}"
                    by_stock[key].append(rec)
                    
                for key, recs in by_stock.items():
                    print(f"   {key}:")
                    for rec in recs[:2]:  # 最多显示2条
                        print(f"     - {rec['title'][:50]}...")
                        
            if len(duplicates) > 10:
                print(f"\n... 还有 {len(duplicates)-10} 个重复记录")
                
            # 询问是否导出详细的重复记录
            response = input("\n是否导出详细的重复记录到文件? (y/n): ")
            if response.lower() == 'y':
                self._export_duplicates(duplicates)
        else:
            print("\n未发现重复记录")
            
    def _export_duplicates(self, duplicates: Dict):
        """导出重复记录详情"""
        output_file = Path("data/duplicate_records.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'duplicates': duplicates,
                'total_count': len(duplicates),
                'exported_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        print(f"重复记录已导出到: {output_file}")
            
    def find_orphan_main_docs(self):
        """查找孤立的主文档（只有主文档，没有任何chunks的记录）"""
        print("\n=== 查找孤立的主文档 ===")
        print("正在分析数据...")
        
        orphan_main_docs = []
        batch_size = 500
        offset = 0
        total_checked = 0
        
        print("\n检查主文档是否有对应的chunks...")
        
        try:
            while True:
                # 获取主文档
                main_docs = self.milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id", "ts_code", "title", "ann_date"],
                    offset=offset,
                    limit=batch_size
                )
                
                if not main_docs:
                    break
                    
                # 检查每个主文档是否有chunks
                for doc in main_docs:
                    doc_id = doc.get('doc_id', '')
                    if '_' in doc_id:
                        announcement_id = doc_id.split('_')[0]
                        
                        # 查找是否有chunk_id > 0的记录
                        chunk_check = self.milvus.collection.query(
                            expr=f'doc_id like "{announcement_id}_%" and chunk_id > 0',
                            output_fields=["doc_id"],
                            limit=1
                        )
                        
                        # 如果没有找到任何chunks，这是一个孤立的主文档
                        if not chunk_check:
                            orphan_main_docs.append({
                                'doc_id': doc_id,
                                'announcement_id': announcement_id,
                                'ts_code': doc.get('ts_code', ''),
                                'title': doc.get('title', ''),
                                'ann_date': doc.get('ann_date', '')
                            })
                            
                total_checked += len(main_docs)
                offset += batch_size
                
                print(f"\r已检查 {total_checked} 个主文档，找到 {len(orphan_main_docs)} 个孤立主文档", end='')
                
                # 限制最大offset避免超过16384
                if offset >= 15000 or len(main_docs) < batch_size:
                    break
                    
        except Exception as e:
            print(f"\n检查时出错: {e}")
            
        print(f"\n\n分析结果:")
        print(f"  - 检查了 {total_checked} 个主文档")
        print(f"  - 找到 {len(orphan_main_docs)} 个孤立主文档")
        
        if orphan_main_docs:
            # 统计分析
            by_stock = defaultdict(int)
            by_date = defaultdict(int)
            
            for doc in orphan_main_docs:
                by_stock[doc['ts_code']] += 1
                by_date[doc['ann_date']] += 1
                
            print("\n按股票代码统计 (前20):")
            for stock, count in sorted(by_stock.items(), key=lambda x: x[1], reverse=True)[:20]:
                print(f"  {stock}: {count} 个孤立主文档")
                
            if len(by_stock) > 20:
                print(f"  ... 还有 {len(by_stock)-20} 只股票")
                
            print("\n按日期统计 (前10):")
            for date, count in sorted(by_date.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {date}: {count} 个孤立主文档")
                
            # 显示示例
            print("\n孤立主文档示例 (前5个):")
            for i, doc in enumerate(orphan_main_docs[:5]):
                print(f"\n{i+1}. 公告ID: {doc['announcement_id']}")
                print(f"   股票代码: {doc['ts_code']}")
                print(f"   标题: {doc['title'][:60]}...")
                print(f"   日期: {doc['ann_date']}")
                print(f"   说明: 该文档没有任何文本chunks，可能是空文档或处理失败")
                
        return orphan_main_docs
        
    def delete_orphan_main_docs(self, orphan_docs=None):
        """删除孤立的主文档"""
        if orphan_docs is None:
            # 先查找
            orphan_docs = self.find_orphan_main_docs()
            
        if not orphan_docs:
            print("\n没有找到孤立的主文档")
            return 0
            
        print(f"\n准备删除 {len(orphan_docs)} 个孤立的主文档")
        
        # 显示摘要
        doc_ids = [doc['doc_id'] for doc in orphan_docs]
        
        # 确认删除
        response = input("\n这些主文档没有任何文本内容，确认删除? (yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
            
        # 执行删除（不需要查找chunks，因为这些文档本身就没有chunks）
        return self.delete_by_doc_ids(doc_ids, include_chunks=False)
        
    def find_orphan_chunks(self):
        """查找孤立的chunks（主文档已删除但chunks还在）"""
        print("\n=== 查找孤立的chunks ===")
        print("正在分析数据...")
        
        # 1. 获取所有主文档的announcement_id
        main_doc_ids = set()
        batch_size = 1000
        offset = 0
        max_offset = 16000  # 避免超过16384限制
        
        print("\n1. 收集主文档ID...")
        while offset < max_offset:
            try:
                results = self.milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id"],
                    offset=offset,
                    limit=batch_size
                )
                
                if not results:
                    break
                    
                for r in results:
                    doc_id = r.get('doc_id', '')
                    if '_' in doc_id:
                        announcement_id = doc_id.split('_')[0]
                        main_doc_ids.add(announcement_id)
                            
                offset += len(results)
                print(f"\r  已处理 {len(main_doc_ids)} 个主文档", end='')
                
                if len(results) < batch_size:
                    break
                    
            except Exception as e:
                print(f"\n  获取主文档时出错: {e}")
                break
                
        print(f"\n  找到 {len(main_doc_ids)} 个主文档")
        
        # 2. 查找孤立的chunks
        orphan_chunks = []
        orphan_announcement_ids = set()
        
        print("\n2. 检查chunks...")
        print("  由于查询限制，将分多次查询...")
        
        # 分批查询不同chunk_id范围
        total_chunks_checked = 0
        
        for chunk_id_start in range(1, 500, 50):  # 假设chunk_id不会超过500
            chunk_id_end = chunk_id_start + 49
            
            try:
                expr = f"chunk_id >= {chunk_id_start} and chunk_id <= {chunk_id_end}"
                results = self.milvus.collection.query(
                    expr=expr,
                    output_fields=["doc_id", "chunk_id", "ts_code", "title", "ann_date"],
                    limit=16000
                )
                
                if not results:
                    continue
                    
                total_chunks_checked += len(results)
                
                for r in results:
                    doc_id = r.get('doc_id', '')
                    if '_' in doc_id:
                        announcement_id = doc_id.split('_')[0]
                        
                        # 检查是否有对应的主文档
                        if announcement_id not in main_doc_ids:
                            orphan_chunks.append({
                                'doc_id': doc_id,
                                'announcement_id': announcement_id,
                                'chunk_id': r.get('chunk_id'),
                                'ts_code': r.get('ts_code', ''),
                                'title': r.get('title', ''),
                                'ann_date': r.get('ann_date', '')
                            })
                            orphan_announcement_ids.add(announcement_id)
                            
                print(f"\r  已检查 {total_chunks_checked} 个chunks，找到 {len(orphan_chunks)} 个孤立chunks", end='')
                        
            except Exception as e:
                print(f"\n  检查chunks时出错: {e}")
                continue
                
        print(f"\n\n分析结果:")
        print(f"  - 检查了 {total_chunks_checked} 个chunks")
        print(f"  - 找到 {len(orphan_chunks)} 个孤立chunks")
        print(f"  - 这些chunks属于 {len(orphan_announcement_ids)} 个已删除的文档")
        
        # 3. 统计和显示
        if orphan_chunks:
            # 按announcement_id分组
            orphan_by_announcement = defaultdict(list)
            for chunk in orphan_chunks:
                orphan_by_announcement[chunk['announcement_id']].append(chunk)
                
            # 按股票代码统计
            by_stock = defaultdict(int)
            by_date = defaultdict(int)
            
            for ann_id, chunks in orphan_by_announcement.items():
                if chunks:
                    stock = chunks[0]['ts_code']
                    date = chunks[0]['ann_date']
                    by_stock[stock] += len(chunks)
                    by_date[date] += len(chunks)
                    
            print("\n按股票代码统计 (前20):")
            for stock, count in sorted(by_stock.items(), key=lambda x: x[1], reverse=True)[:20]:
                print(f"  {stock}: {count} 个孤立chunks")
                
            if len(by_stock) > 20:
                print(f"  ... 还有 {len(by_stock)-20} 只股票")
                
            print("\n按日期统计 (前10):")
            for date, count in sorted(by_date.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {date}: {count} 个孤立chunks")
                
            # 显示具体示例
            print("\n文档示例 (前5个):")
            for i, (ann_id, chunks) in enumerate(list(orphan_by_announcement.items())[:5]):
                print(f"\n{i+1}. 公告ID: {ann_id}")
                print(f"   股票代码: {chunks[0]['ts_code']}")
                print(f"   标题: {chunks[0]['title'][:60]}...")
                print(f"   日期: {chunks[0]['ann_date']}")
                print(f"   孤立chunks数: {len(chunks)}")
                chunk_ids = [c['chunk_id'] for c in chunks]
                print(f"   chunk_id范围: {min(chunk_ids)}-{max(chunk_ids)}")
                
        return orphan_chunks
        
    def delete_orphan_chunks(self, orphan_chunks=None):
        """删除孤立的chunks"""
        if orphan_chunks is None:
            # 先查找
            orphan_chunks = self.find_orphan_chunks()
            
        if not orphan_chunks:
            print("\n没有找到孤立的chunks")
            return 0
            
        # 按announcement_id分组统计
        orphan_by_announcement = defaultdict(list)
        for chunk in orphan_chunks:
            orphan_by_announcement[chunk['announcement_id']].append(chunk)
            
        print(f"\n准备删除:")
        print(f"  - {len(orphan_chunks)} 个孤立chunks")
        print(f"  - 来自 {len(orphan_by_announcement)} 个已删除的文档")
        
        # 确认删除
        response = input("\n确认删除这些孤立的chunks? (yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
            
        # 收集所有要删除的doc_id
        doc_ids_to_delete = [chunk['doc_id'] for chunk in orphan_chunks]
        
        # 使用现有的批量删除方法
        return self.delete_by_doc_ids(doc_ids_to_delete, include_chunks=False)
        
    def check_data_integrity(self):
        """综合检查数据完整性"""
        print("\n=== 数据完整性检查 ===")
        
        # 1. 检查孤立主文档
        print("\n1. 检查孤立主文档...")
        orphan_main_docs = []
        main_checked = 0
        
        try:
            results = self.milvus.collection.query(
                expr="chunk_id == 0",
                output_fields=["doc_id"],
                limit=1000
            )
            
            for doc in results[:100]:  # 采样检查前100个
                main_checked += 1
                doc_id = doc.get('doc_id', '')
                if '_' in doc_id:
                    announcement_id = doc_id.split('_')[0]
                    
                    # 检查是否有chunks
                    chunk_check = self.milvus.collection.query(
                        expr=f'doc_id like "{announcement_id}_%" and chunk_id > 0',
                        output_fields=["doc_id"],
                        limit=1
                    )
                    
                    if not chunk_check:
                        orphan_main_docs.append(doc_id)
                        
            print(f"  采样检查了 {main_checked} 个主文档")
            print(f"  发现 {len(orphan_main_docs)} 个可能的孤立主文档")
            
        except Exception as e:
            print(f"  检查出错: {e}")
            
        # 2. 检查孤立chunks
        print("\n2. 检查孤立chunks...")
        orphan_chunks_count = 0
        
        try:
            # 采样检查chunk_id=100的记录
            sample_chunks = self.milvus.collection.query(
                expr="chunk_id == 100",
                output_fields=["doc_id"],
                limit=100
            )
            
            for chunk in sample_chunks:
                doc_id = chunk.get('doc_id', '')
                if '_' in doc_id:
                    ann_id = doc_id.split('_')[0]
                    # 检查主文档
                    main_check = self.milvus.collection.query(
                        expr=f'doc_id == "{ann_id}_0"',
                        output_fields=["doc_id"],
                        limit=1
                    )
                    if not main_check:
                        orphan_chunks_count += 1
                        
            print(f"  采样检查了chunk_id=100的记录")
            print(f"  发现 {orphan_chunks_count} 个可能的孤立chunks")
            
        except Exception as e:
            print(f"  检查出错: {e}")
            
        # 3. 总结
        print("\n数据完整性总结:")
        if orphan_main_docs or orphan_chunks_count > 0:
            print("  ⚠️ 发现数据完整性问题")
            if orphan_main_docs:
                print(f"     - 可能有孤立主文档需要清理")
            if orphan_chunks_count > 0:
                print(f"     - 可能有孤立chunks需要清理")
            print("\n  建议运行相应的清理功能")
        else:
            print("  ✓ 数据完整性良好")

def main():
    tool = MilvusManagementTool()
    
    while True:
        print("\n" + "=" * 80)
        print("Milvus数据管理工具 v2.0 (完整数据维护版)".center(80))
        print("=" * 80)
        
        print("\n=== 基础功能 ===")
        print("1. 查看统计信息")
        print("2. 按关键词搜索")
        print("3. 按日期搜索")
        print("4. 按股票代码搜索")
        
        print("\n=== 数据管理 ===")
        print("5. 按关键词删除")
        print("6. 按日期删除")
        print("7. 导出已处理记录")
        print("8. 检查重复记录")
        
        print("\n=== 数据完整性维护 ===")
        print("9. 查找孤立主文档（没有chunks的主文档）")
        print("10. 删除孤立主文档")
        print("11. 查找孤立chunks（没有主文档的chunks）")
        print("12. 删除孤立chunks")
        print("13. 综合数据完整性检查")
        
        print("\n0. 退出")
        
        choice = input("\n请选择: ")
        
        if choice == '1':
            tool.get_statistics()
            
        elif choice == '2':
            keyword = input("输入搜索关键词: ")
            results = tool.search_by_keyword(keyword, limit=1000)
            # 显示前10条
            for i, r in enumerate(results[:10]):
                print(f"{i+1}. {r['ts_code']} - {r['title'][:60]}... - {r['ann_date']}")
            if len(results) > 10:
                print(f"... 还有 {len(results)-10} 条")
                
        elif choice == '3':
            print("\n日期搜索选项:")
            print("1. 单日搜索")
            print("2. 日期范围搜索")
            
            sub_choice = input("选择 (1-2): ")
            
            if sub_choice == '1':
                date = input("输入日期 (支持格式: YYYYMMDD, YYYY-MM-DD, YYYY/MM/DD): ")
                results = tool.search_by_date(date)
                for i, r in enumerate(results[:10]):
                    print(f"{i+1}. {r['ts_code']} - {r['title'][:60]}...")
                if len(results) > 10:
                    print(f"... 还有 {len(results)-10} 条")
                    
            elif sub_choice == '2':
                start = input("开始日期: ")
                end = input("结束日期: ")
                results = tool.search_by_date_range(start, end)
                for i, r in enumerate(results[:10]):
                    print(f"{i+1}. {r['ts_code']} - {r['title'][:60]}... - {r['ann_date']}")
                if len(results) > 10:
                    print(f"... 还有 {len(results)-10} 条")
                
        elif choice == '4':
            ts_code = input("输入股票代码: ")
            results = tool.search_by_stock(ts_code)
            for i, r in enumerate(results[:10]):
                print(f"{i+1}. {r['title'][:60]}... - {r['ann_date']}")
            if len(results) > 10:
                print(f"... 还有 {len(results)-10} 条")
                
        elif choice == '5':
            keyword = input("输入要删除的关键词: ")
            tool.delete_by_keyword(keyword)
            
        elif choice == '6':
            date = input("输入要删除的日期 (支持多种格式): ")
            tool.delete_by_date(date)
            
        elif choice == '7':
            tool.export_processed_records()
            
        elif choice == '8':
            tool.check_duplicates()
            
        elif choice == '9':
            tool.find_orphan_main_docs()
            
        elif choice == '10':
            tool.delete_orphan_main_docs()
            
        elif choice == '11':
            tool.find_orphan_chunks()
            
        elif choice == '12':
            tool.delete_orphan_chunks()
            
        elif choice == '13':
            tool.check_data_integrity()
            
        elif choice == '0':
            print("\n再见！")
            break
            
        input("\n按回车继续...")

if __name__ == "__main__":
    main()