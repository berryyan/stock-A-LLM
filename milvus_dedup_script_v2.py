"""
Milvus向量数据库去重脚本 - 适配修复后的连接器
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

logger = setup_logger("milvus_dedup")

class MilvusDuplicateRemover:
    """Milvus重复数据清理器"""
    
    def __init__(self):
        self.milvus_conn = MilvusConnector()
        logger.info("Milvus去重工具初始化完成")
    
    def check_collection_status(self):
        """检查集合状态"""
        stats = self.milvus_conn.get_collection_stats()
        logger.info(f"集合状态: {stats}")
        return stats
    
    def find_duplicates(self, batch_size=1000):
        """查找重复的文档"""
        logger.info("开始查找重复文档...")
        
        # 获取所有唯一的doc_id
        all_docs = []
        offset = 0
        
        # 使用新的查询方法，确保集合已加载
        while True:
            try:
                # 查询时指定 limit
                expr = "chunk_id >= 0"  # 查询所有记录
                results = self.milvus_conn.query(
                    expr=expr,
                    output_fields=["id", "doc_id", "chunk_id", "ts_code", "ann_date"],
                    limit=batch_size
                )
                
                if not results:
                    break
                
                all_docs.extend(results)
                
                if len(results) < batch_size:
                    break
                
                offset += batch_size
                logger.info(f"已扫描 {len(all_docs)} 条记录...")
                
                # 为了避免内存溢出，可以分批处理
                if len(all_docs) > 100000:
                    break
                    
            except Exception as e:
                logger.error(f"查询失败: {e}")
                break
        
        logger.info(f"共扫描 {len(all_docs)} 条记录")
        
        # 分组统计
        doc_groups = defaultdict(list)
        for doc in all_docs:
            key = f"{doc['doc_id']}_{doc['chunk_id']}"
            doc_groups[key].append(doc)
        
        # 找出重复的
        duplicates = {}
        for key, docs in doc_groups.items():
            if len(docs) > 1:
                # 按id排序，保留最小的（最早的）
                docs.sort(key=lambda x: x['id'])
                duplicates[key] = {
                    'keep': docs[0],
                    'remove': docs[1:],
                    'count': len(docs)
                }
        
        logger.info(f"发现 {len(duplicates)} 组重复文档")
        
        # 统计信息
        total_duplicates = sum(len(d['remove']) for d in duplicates.values())
        logger.info(f"需要删除 {total_duplicates} 条重复记录")
        
        return duplicates
    
    def remove_duplicates(self, duplicates, dry_run=True):
        """删除重复文档"""
        if not duplicates:
            logger.info("没有重复文档需要删除")
            return
        
        if dry_run:
            logger.info("DRY RUN 模式 - 仅显示将要删除的内容")
            
            # 显示前10个示例
            count = 0
            for key, dup_info in duplicates.items():
                if count >= 10:
                    break
                logger.info(f"\n文档: {key}")
                logger.info(f"  保留: ID={dup_info['keep']['id']}")
                logger.info(f"  删除: {[d['id'] for d in dup_info['remove']]}")
                count += 1
            
            if len(duplicates) > 10:
                logger.info(f"\n... 还有 {len(duplicates) - 10} 组重复文档")
            
            return
        
        # 实际删除
        logger.info("开始删除重复文档...")
        
        total_deleted = 0
        failed_deletes = 0
        
        # 批量删除
        batch_size = 100
        ids_to_delete = []
        
        for key, dup_info in tqdm(duplicates.items(), desc="处理重复文档"):
            for doc in dup_info['remove']:
                ids_to_delete.append(doc['id'])
                
                if len(ids_to_delete) >= batch_size:
                    # 执行批量删除
                    expr = f"id in {ids_to_delete}"
                    success = self.milvus_conn.delete_by_expr(expr)
                    
                    if success:
                        total_deleted += len(ids_to_delete)
                    else:
                        failed_deletes += len(ids_to_delete)
                    
                    ids_to_delete = []
                    time.sleep(0.1)  # 避免过于频繁
        
        # 删除剩余的
        if ids_to_delete:
            expr = f"id in {ids_to_delete}"
            success = self.milvus_conn.delete_by_expr(expr)
            
            if success:
                total_deleted += len(ids_to_delete)
            else:
                failed_deletes += len(ids_to_delete)
        
        logger.info(f"删除完成: 成功 {total_deleted} 条, 失败 {failed_deletes} 条")
    
    def analyze_duplicates(self, duplicates):
        """分析重复数据的模式"""
        if not duplicates:
            logger.info("没有重复数据可分析")
            return
        
        # 按股票代码统计
        stock_duplicates = defaultdict(int)
        # 按日期统计
        date_duplicates = defaultdict(int)
        # 按重复次数统计
        dup_count_stats = defaultdict(int)
        
        for key, dup_info in duplicates.items():
            doc = dup_info['keep']
            stock_duplicates[doc['ts_code']] += 1
            date_duplicates[doc['ann_date']] += 1
            dup_count_stats[dup_info['count']] += 1
        
        logger.info("\n=== 重复数据分析 ===")
        
        # 重复最多的股票
        logger.info("\n重复最多的股票 TOP 10:")
        for stock, count in sorted(stock_duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {stock}: {count} 个重复文档")
        
        # 重复最多的日期
        logger.info("\n重复最多的日期 TOP 10:")
        for date, count in sorted(date_duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {date}: {count} 个重复文档")
        
        # 重复次数分布
        logger.info("\n重复次数分布:")
        for dup_count, freq in sorted(dup_count_stats.items()):
            logger.info(f"  重复 {dup_count} 次: {freq} 组文档")
    
    def run(self, dry_run=True):
        """运行去重流程"""
        logger.info("="*60)
        logger.info(f"Milvus去重工具 - {'测试模式' if dry_run else '执行模式'}")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # 1. 检查集合状态
        stats = self.check_collection_status()
        if not stats.get('loaded'):
            logger.warning("集合未加载，尝试加载...")
            self.milvus_conn._ensure_collection_loaded()
        
        # 2. 查找重复
        duplicates = self.find_duplicates()
        
        # 3. 分析重复
        self.analyze_duplicates(duplicates)
        
        # 4. 删除重复（如果不是dry run）
        if duplicates:
            logger.info(f"\n准备删除 {sum(len(d['remove']) for d in duplicates.values())} 条重复记录")
            
            if not dry_run:
                confirm = input("\n确认删除? (yes/no): ")
                if confirm.lower() == 'yes':
                    self.remove_duplicates(duplicates, dry_run=False)
                else:
                    logger.info("取消删除操作")
            else:
                self.remove_duplicates(duplicates, dry_run=True)
        
        # 5. 最终统计
        logger.info("\n=== 处理完成 ===")
        final_stats = self.check_collection_status()
        logger.info(f"最终文档数: {final_stats.get('row_count', 'N/A')}")
    
    def close(self):
        """关闭连接"""
        self.milvus_conn.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Milvus向量数据库去重工具')
    parser.add_argument('--execute', action='store_true', help='实际执行删除（默认为测试模式）')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析，不删除')
    
    args = parser.parse_args()
    
    remover = MilvusDuplicateRemover()
    
    try:
        if args.analyze_only:
            # 仅分析
            duplicates = remover.find_duplicates()
            remover.analyze_duplicates(duplicates)
        else:
            # 运行完整流程
            remover.run(dry_run=not args.execute)
    finally:
        remover.close()


if __name__ == "__main__":
    main()