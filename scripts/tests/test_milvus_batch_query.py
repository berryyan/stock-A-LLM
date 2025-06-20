"""
测试Milvus分批查询功能
用于验证V5.3版本的分批查询是否正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
import time
from datetime import datetime

def test_batch_query():
    """测试分批查询功能"""
    print("=" * 80)
    print("Milvus分批查询测试")
    print("=" * 80)
    
    # 连接Milvus
    milvus = MilvusConnector()
    
    # 1. 获取集合统计信息
    stats = milvus.get_collection_stats()
    print(f"\n集合统计信息:")
    print(f"  总文档数: {stats['row_count']}")
    
    # 2. 测试不同批量大小的查询
    batch_sizes = [1000, 5000, 10000]
    
    for batch_size in batch_sizes:
        print(f"\n测试批量大小: {batch_size}")
        
        processed_ids = set()
        offset = 0
        batch_count = 0
        start_time = time.time()
        
        while True:
            try:
                # 查询一批数据
                batch_start = time.time()
                results = milvus.collection.query(
                    expr="chunk_id == 0",
                    output_fields=["doc_id", "ann_date"],
                    limit=batch_size,
                    offset=offset
                )
                batch_time = time.time() - batch_start
                
                if not results:
                    break
                    
                batch_count += 1
                
                # 提取公告ID
                batch_ids = 0
                for r in results:
                    doc_id = r.get('doc_id', '')
                    if '_' in doc_id:
                        ann_id = doc_id.split('_')[0]
                        if ann_id not in processed_ids:
                            processed_ids.add(ann_id)
                            batch_ids += 1
                
                print(f"  批次 {batch_count}: 查询 {len(results)} 条，"
                      f"新增 {batch_ids} 个ID，总计 {len(processed_ids)} 个 "
                      f"(耗时 {batch_time:.2f}秒)")
                
                # 如果返回数量少于batch_size，说明已经是最后一批
                if len(results) < batch_size:
                    break
                    
                offset += batch_size
                
                # 只测试前5批
                if batch_count >= 5:
                    print("  ... (仅显示前5批)")
                    break
                    
            except Exception as e:
                print(f"  错误: {e}")
                break
        
        total_time = time.time() - start_time
        print(f"  总耗时: {total_time:.2f}秒")
    
    # 3. 测试日期范围查询
    print("\n\n测试日期范围查询:")
    date_ranges = [
        ("20250401", "20250430"),
        ("20250315", "20250415"),
        ("20250422", "20250422")
    ]
    
    for start_date, end_date in date_ranges:
        print(f"\n日期范围: {start_date} - {end_date}")
        
        try:
            expr = f"chunk_id == 0 and ann_date >= '{start_date}' and ann_date <= '{end_date}'"
            
            # 先获取总数
            count_results = milvus.collection.query(
                expr=expr,
                output_fields=["doc_id"],
                limit=1
            )
            
            # 查询一批数据
            results = milvus.collection.query(
                expr=expr,
                output_fields=["doc_id", "ann_date"],
                limit=100
            )
            
            # 统计日期分布
            date_dist = {}
            for r in results[:10]:  # 只显示前10条
                ann_date = r.get('ann_date', '')
                doc_id = r.get('doc_id', '')
                print(f"  {doc_id} - {ann_date}")
                
                if ann_date:
                    date_dist[ann_date] = date_dist.get(ann_date, 0) + 1
            
            print(f"  查询到 {len(results)} 条记录")
            
        except Exception as e:
            print(f"  错误: {e}")
    
    # 4. 测试offset超出范围
    print("\n\n测试offset边界情况:")
    try:
        # 测试一个很大的offset
        results = milvus.collection.query(
            expr="chunk_id == 0",
            output_fields=["doc_id"],
            limit=10,
            offset=1000000  # 一个很大的offset
        )
        print(f"  大offset查询结果: {len(results)} 条")
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

def test_query_performance():
    """测试查询性能"""
    print("\n\n性能测试:")
    milvus = MilvusConnector()
    
    # 测试不同查询条件的性能
    test_cases = [
        ("无条件查询", "chunk_id == 0"),
        ("日期范围查询", "chunk_id == 0 and ann_date >= '20250401' and ann_date <= '20250430'"),
        ("特定日期查询", "chunk_id == 0 and ann_date == '20250422'")
    ]
    
    for name, expr in test_cases:
        print(f"\n{name}:")
        print(f"  表达式: {expr}")
        
        # 执行10次查询，计算平均时间
        times = []
        for i in range(3):
            start = time.time()
            results = milvus.collection.query(
                expr=expr,
                output_fields=["doc_id"],
                limit=1000
            )
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  第{i+1}次: {elapsed:.3f}秒 ({len(results)}条)")
        
        avg_time = sum(times) / len(times)
        print(f"  平均耗时: {avg_time:.3f}秒")

if __name__ == "__main__":
    try:
        test_batch_query()
        test_query_performance()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()
