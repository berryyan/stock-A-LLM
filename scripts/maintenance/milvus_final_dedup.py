"""
Milvus最终去重工具 - 基于正确的重复判断逻辑
判断标准：相同的doc_id + 相同的chunk_id = 重复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from collections import defaultdict
from datetime import datetime
import time
from tqdm import tqdm
from utils.logger import setup_logger
import json

logger = setup_logger("milvus_final_dedup")

class MilvusFinalDeduplicator:
    """Milvus最终去重工具"""
    
    def __init__(self):
        self.milvus_conn = MilvusConnector()
        self.max_query_window = 16384
        logger.info("Milvus最终去重工具初始化完成")
    
    def get_all_dates(self):
        """获取所有唯一的日期"""
        logger.info("获取所有唯一日期...")
        
        dates = set()
        sample_size = 10000
        
        # 使用ID范围获取样本
        for start_id in range(0, 1000000000, 10000000):
            expr = f"id > {start_id} and id < {start_id + 10000000}"
            results = self.milvus_conn.query(
                expr=expr,
                output_fields=["ann_date"],
                limit=sample_size
            )
            
            if not results:
                continue
                
            for r in results:
                dates.add(r['ann_date'])
            
            # 如果某个范围没有数据，尝试下一个范围
            if len(results) < 100:
                continue
        
        dates_list = sorted(list(dates))
        logger.info(f"找到 {len(dates_list)} 个唯一日期")
        return dates_list
    
    def scan_date_for_duplicates(self, date):
        """扫描特定日期的重复记录"""
        all_records = []
        last_id = 0
        batch_size = 5000
        
        # 获取该日期的所有记录
        while True:
            expr = f'ann_date == "{date}" and id > {last_id}'
            try:
                results = self.milvus_conn.query(
                    expr=expr,
                    output_fields=["id", "doc_id", "chunk_id", "ts_code", "title", "text"],
                    limit=batch_size
                )
                
                if not results:
                    break
                
                all_records.extend(results)
                last_id = max(r['id'] for r in results)
                
                if len(results) < batch_size:
                    break
                    
            except Exception as e:
                logger.error(f"查询日期 {date} 时出错: {e}")
                break
        
        # 查找重复
        # 使用(doc_id, chunk_id)作为唯一键
        seen = {}  # (doc_id, chunk_id) -> first_record
        duplicates = []
        duplicate_groups = defaultdict(list)
        
        for record in all_records:
            key = (record['doc_id'], record['chunk_id'])
            
            if key in seen:
                # 这是重复的
                duplicates.append(record)
                # 记录重复组
                if key not in duplicate_groups:
                    duplicate_groups[key] = [seen[key]]
                duplicate_groups[key].append(record)
            else:
                # 第一次见到
                seen[key] = record
        
        return all_records, duplicates, duplicate_groups
    
    def scan_all_data(self, date_filter=None, limit_dates=None):
        """扫描所有数据或指定日期的数据"""
        logger.info("开始扫描数据...")
        
        # 获取要扫描的日期
        if date_filter:
            dates_to_scan = [date_filter]
        else:
            all_dates = self.get_all_dates()
            if limit_dates and limit_dates < len(all_dates):
                dates_to_scan = all_dates[:limit_dates]
            else:
                dates_to_scan = all_dates
        
        # 初始化统计
        total_records = 0
        total_duplicates = 0
        all_duplicate_groups = {}
        
        # 扫描每个日期
        with tqdm(total=len(dates_to_scan), desc="扫描进度") as pbar:
            for date in dates_to_scan:
                records, duplicates, groups = self.scan_date_for_duplicates(date)
                
                total_records += len(records)
                total_duplicates += len(duplicates)
                
                # 合并重复组
                for key, group in groups.items():
                    if len(group) > 1:
                        all_duplicate_groups[f"{date}_{key[0]}_{key[1]}"] = group
                
                pbar.set_description(f"扫描 {date} (记录:{len(records)}, 重复:{len(duplicates)})")
                pbar.update(1)
        
        logger.info(f"\n扫描完成!")
        logger.info(f"  扫描日期数: {len(dates_to_scan)}")
        logger.info(f"  总记录数: {total_records}")
        logger.info(f"  重复记录数: {total_duplicates}")
        logger.info(f"  重复组数: {len(all_duplicate_groups)}")
        
        return total_records, total_duplicates, all_duplicate_groups
    
    def analyze_duplicates(self, duplicate_groups):
        """分析重复模式"""
        if not duplicate_groups:
            logger.info("\n没有发现重复记录")
            return
        
        logger.info("\n=== 重复数据分析 ===")
        
        # 统计
        dup_count_stats = defaultdict(int)
        stock_duplicates = defaultdict(int)
        date_duplicates = defaultdict(int)
        
        for key, records in duplicate_groups.items():
            dup_count = len(records)
            dup_count_stats[dup_count] += 1
            
            first_record = records[0]
            stock_duplicates[first_record['ts_code']] += dup_count - 1
            date_duplicates[first_record.get('ann_date', 'Unknown')] += dup_count - 1
        
        # 显示统计
        logger.info("\n重复次数分布:")
        for count in sorted(dup_count_stats.keys()):
            logger.info(f"  重复 {count} 次: {dup_count_stats[count]} 组")
        
        logger.info("\n重复最多的股票 TOP 10:")
        for stock, count in sorted(stock_duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {stock}: {count} 条重复")
        
        logger.info("\n重复最多的日期 TOP 10:")
        for date, count in sorted(date_duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {date}: {count} 条重复")
        
        # 显示样例
        logger.info("\n重复样例:")
        for i, (key, records) in enumerate(list(duplicate_groups.items())[:5]):
            logger.info(f"\n样例 {i+1}:")
            logger.info(f"  Key: {key}")
            logger.info(f"  doc_id: {records[0]['doc_id']}")
            logger.info(f"  chunk_id: {records[0]['chunk_id']}")
            logger.info(f"  重复次数: {len(records)}")
            logger.info(f"  股票: {records[0]['ts_code']}")
            logger.info(f"  标题: {records[0].get('title', 'N/A')[:50]}...")
            logger.info(f"  IDs: {[r['id'] for r in records]}")
            logger.info(f"  文本预览: {records[0]['text'][:80]}...")
            
            # 验证是否真的相同
            if len(set(r['text'] for r in records)) == 1:
                logger.info(f"  ✓ 文本内容完全相同")
            else:
                logger.warning(f"  ✗ 文本内容不同！")
    
    def save_report(self, duplicate_groups, filename=None):
        """保存重复报告"""
        if not duplicate_groups:
            logger.info("没有重复数据需要保存")
            return
        
        if not filename:
            filename = f"final_duplicate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "scan_time": datetime.now().isoformat(),
            "total_groups": len(duplicate_groups),
            "total_duplicates": sum(len(records) - 1 for records in duplicate_groups.values()),
            "groups": {}
        }
        
        # 保存每个重复组的详细信息
        for key, records in duplicate_groups.items():
            report["groups"][key] = {
                "doc_id": records[0]['doc_id'],
                "chunk_id": records[0]['chunk_id'],
                "count": len(records),
                "stock": records[0]['ts_code'],
                "title": records[0].get('title', 'N/A')[:100],
                "ids": [r['id'] for r in records],
                "text_preview": records[0]['text'][:200]
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n报告已保存到: {filename}")
    
    def delete_duplicates(self, duplicate_groups, dry_run=True):
        """删除重复记录"""
        if not duplicate_groups:
            logger.info("没有重复记录需要删除")
            return
        
        # 收集要删除的ID（保留每组中ID最小的）
        ids_to_delete = []
        
        for records in duplicate_groups.values():
            # 按ID排序，保留最小的
            sorted_records = sorted(records, key=lambda x: x['id'])
            ids_to_delete.extend([r['id'] for r in sorted_records[1:]])
        
        logger.info(f"\n准备删除 {len(ids_to_delete)} 条重复记录")
        
        if dry_run:
            logger.info("DRY RUN 模式 - 不会真正删除")
            logger.info(f"将删除的ID示例: {ids_to_delete[:10]}")
            return
        
        # 确认删除
        confirm = input("\n确认删除? (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("取消删除操作")
            return
        
        # 执行删除
        batch_size = 100
        deleted = 0
        
        with tqdm(total=len(ids_to_delete), desc="删除进度") as pbar:
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i:i+batch_size]
                
                try:
                    id_list_str = ", ".join(map(str, batch))
                    expr = f"id in [{id_list_str}]"
                    
                    if self.milvus_conn.delete_by_expr(expr):
                        deleted += len(batch)
                    
                    pbar.update(len(batch))
                    
                    if deleted % 1000 == 0:
                        self.milvus_conn.collection.flush()
                        
                except Exception as e:
                    logger.error(f"删除批次失败: {e}")
        
        # 最终flush
        self.milvus_conn.collection.flush()
        time.sleep(2)
        
        logger.info(f"\n成功删除: {deleted} 条记录")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Milvus最终去重工具')
    parser.add_argument('--date', type=str, help='只扫描特定日期')
    parser.add_argument('--limit', type=int, help='限制扫描的日期数量')
    parser.add_argument('--save-report', action='store_true', help='保存报告')
    parser.add_argument('--delete', action='store_true', help='删除重复记录')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    
    args = parser.parse_args()
    
    deduplicator = MilvusFinalDeduplicator()
    
    try:
        # 执行扫描
        total_records, total_duplicates, duplicate_groups = deduplicator.scan_all_data(
            date_filter=args.date,
            limit_dates=args.limit
        )
        
        # 分析结果
        deduplicator.analyze_duplicates(duplicate_groups)
        
        # 保存报告
        if args.save_report:
            deduplicator.save_report(duplicate_groups)
        
        # 删除重复
        if args.delete:
            deduplicator.delete_duplicates(duplicate_groups, dry_run=args.dry_run)
        
        # 总结
        logger.info("\n" + "="*60)
        if total_duplicates == 0:
            logger.info("✓ 没有发现重复记录")
        else:
            logger.info(f"✗ 发现 {total_duplicates} 条重复记录")
            if not args.delete:
                logger.info("  使用 --delete 参数来删除重复")
        
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
    except Exception as e:
        logger.error(f"处理过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        deduplicator.milvus_conn.close()


if __name__ == "__main__":
    main()