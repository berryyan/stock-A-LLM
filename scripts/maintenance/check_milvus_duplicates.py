"""
Milvus重复数据诊断脚本
快速检查和分析重复情况
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from collections import defaultdict
from utils.logger import setup_logger

logger = setup_logger("milvus_duplicate_check")

def check_specific_duplicates():
    """检查特定的重复情况"""
    milvus_conn = MilvusConnector()
    
    try:
        # 1. 检查集合状态
        stats = milvus_conn.get_collection_stats()
        logger.info(f"集合状态: {stats}")
        
        # 2. 检查特定日期的重复
        logger.info("\n检查2025-04-22的重复情况...")
        
        # 查询这个日期的所有记录
        expr = 'ann_date == "2025-04-22"'
        results = milvus_conn.query(
            expr=expr,
            output_fields=["id", "doc_id", "chunk_id", "ts_code", "title"],
            limit=2000  # 获取更多记录
        )
        
        logger.info(f"2025-04-22 共有 {len(results)} 条记录")
        
        # 分组统计
        doc_chunk_groups = defaultdict(list)
        for doc in results:
            key = f"{doc['doc_id']}_{doc['chunk_id']}"
            doc_chunk_groups[key].append(doc)
        
        # 找出重复的
        duplicate_count = 0
        duplicate_records = 0
        
        logger.info("\n重复详情（前5个）:")
        shown = 0
        for key, docs in doc_chunk_groups.items():
            if len(docs) > 1:
                duplicate_count += 1
                duplicate_records += len(docs) - 1
                
                if shown < 5:
                    logger.info(f"\nKey: {key}")
                    logger.info(f"  重复次数: {len(docs)}")
                    logger.info(f"  股票代码: {docs[0]['ts_code']}")
                    logger.info(f"  标题: {docs[0]['title'][:50]}...")
                    logger.info(f"  IDs: {[d['id'] for d in docs]}")
                    shown += 1
        
        logger.info(f"\n2025-04-22 总结:")
        logger.info(f"  重复的doc_chunk组合: {duplicate_count}")
        logger.info(f"  需要删除的重复记录: {duplicate_records}")
        
        # 3. 检查特定股票的重复
        logger.info("\n检查002915.SZ的重复情况...")
        
        expr = 'ts_code == "002915.SZ"'
        results = milvus_conn.query(
            expr=expr,
            output_fields=["id", "doc_id", "chunk_id", "ann_date", "title"],
            limit=1000
        )
        
        logger.info(f"002915.SZ 共有 {len(results)} 条记录")
        
        # 按doc_id和chunk_id分组
        doc_chunk_groups = defaultdict(list)
        for doc in results:
            key = f"{doc['doc_id']}_{doc['chunk_id']}"
            doc_chunk_groups[key].append(doc)
        
        # 统计重复
        duplicate_count = 0
        for key, docs in doc_chunk_groups.items():
            if len(docs) > 1:
                duplicate_count += 1
        
        logger.info(f"002915.SZ 有 {duplicate_count} 个重复的doc_chunk组合")
        
        # 4. 随机抽样检查
        logger.info("\n随机抽样检查...")
        
        # 获取一些随机ID
        sample_results = milvus_conn.query(
            expr="id > 100000 and id < 200000",
            output_fields=["id", "doc_id", "chunk_id"],
            limit=1000
        )
        
        # 检查这些记录是否有重复
        doc_chunk_set = set()
        duplicates_in_sample = 0
        
        for doc in sample_results:
            key = f"{doc['doc_id']}_{doc['chunk_id']}"
            if key in doc_chunk_set:
                duplicates_in_sample += 1
            else:
                doc_chunk_set.add(key)
        
        logger.info(f"在1000条随机样本中发现 {duplicates_in_sample} 条重复")
        
        # 5. 检查ID范围
        logger.info("\n检查ID范围...")
        
        # 获取一批高ID的记录（模拟最新记录）
        # 先获取一个大概的最大ID
        sample_high = milvus_conn.query(
            expr="id > 700000",
            output_fields=["id"],
            limit=10
        )
        
        if sample_high:
            max_id_approx = max(doc['id'] for doc in sample_high)
            logger.info(f"找到的高ID示例: {max_id_approx}")
            
            # 获取接近最大ID的记录
            expr = f"id > {max_id_approx - 10000}"
            latest_results = milvus_conn.query(
                expr=expr,
                output_fields=["id", "doc_id", "chunk_id", "ann_date"],
                limit=1000
            )
            
            if latest_results:
                id_range = [doc['id'] for doc in latest_results]
                logger.info(f"获取到的ID范围: {min(id_range)} - {max(id_range)}")
                
                # 检查重复
                doc_chunk_groups = defaultdict(list)
                for doc in latest_results:
                    key = f"{doc['doc_id']}_{doc['chunk_id']}"
                    doc_chunk_groups[key].append(doc)
                
                duplicates_in_latest = sum(1 for docs in doc_chunk_groups.values() if len(docs) > 1)
                logger.info(f"这批记录中有 {duplicates_in_latest} 组重复")
        
    finally:
        milvus_conn.close()


def test_deletion():
    """测试删除单条记录"""
    milvus_conn = MilvusConnector()
    
    try:
        # 找一个重复的记录
        expr = 'ann_date == "2025-04-22"'
        results = milvus_conn.query(
            expr=expr,
            output_fields=["id", "doc_id", "chunk_id"],
            limit=10
        )
        
        if results:
            # 尝试删除第一条
            test_id = results[0]['id']
            logger.info(f"\n测试删除ID: {test_id}")
            
            # 删除前计数
            before_count = len(results)
            logger.info(f"删除前记录数: {before_count}")
            
            # 执行删除
            expr = f"id == {test_id}"
            success = milvus_conn.delete_by_expr(expr)
            logger.info(f"删除操作结果: {success}")
            
            # Flush
            milvus_conn.collection.flush()
            
            # 等待
            import time
            time.sleep(2)
            
            # 重新查询
            expr = 'ann_date == "2025-04-22"'
            results_after = milvus_conn.query(
                expr=expr,
                output_fields=["id", "doc_id", "chunk_id"],
                limit=10
            )
            
            after_count = len(results_after)
            logger.info(f"删除后记录数: {after_count}")
            logger.info(f"实际删除数: {before_count - after_count}")
            
            # 检查特定ID是否还存在
            check_expr = f"id == {test_id}"
            check_results = milvus_conn.query(
                expr=check_expr,
                output_fields=["id"],
                limit=1
            )
            
            if check_results:
                logger.warning(f"ID {test_id} 仍然存在！")
            else:
                logger.info(f"ID {test_id} 已成功删除")
                
    finally:
        milvus_conn.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Milvus重复数据诊断')
    parser.add_argument('--test-delete', action='store_true', help='测试删除功能')
    
    args = parser.parse_args()
    
    if args.test_delete:
        test_deletion()
    else:
        check_specific_duplicates()


if __name__ == "__main__":
    main()