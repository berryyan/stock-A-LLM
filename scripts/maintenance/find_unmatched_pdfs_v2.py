"""
准确找出未匹配的PDF文件
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from database.mysql_connector import MySQLConnector
from collections import defaultdict
import hashlib
import json
from utils.logger import setup_logger

logger = setup_logger("find_unmatched_pdfs")

def find_unmatched_pdfs():
    """找出所有未匹配的PDF文件"""
    mysql_conn = MySQLConnector()
    pdf_cache_dir = Path("./data/pdfs/cache")
    
    # 获取所有PDF文件
    pdf_files = list(pdf_cache_dir.glob("*.pdf"))
    logger.info(f"总共找到 {len(pdf_files)} 个PDF文件")
    
    # 解析所有PDF文件信息
    all_pdfs = []
    for pdf_file in pdf_files:
        filename = pdf_file.stem
        parts = filename.split('_')
        if len(parts) >= 3:
            all_pdfs.append({
                'filename': filename,
                'date': parts[0],
                'stock_code': parts[1],
                'hash': parts[2],
                'full_path': str(pdf_file),
                'size': pdf_file.stat().st_size
            })
    
    # 获取所有日期
    all_dates = list(set(pdf['date'] for pdf in all_pdfs))
    logger.info(f"涉及 {len(all_dates)} 个不同日期")
    
    # 从MySQL获取所有这些日期的记录
    all_mysql_records = []
    for date in all_dates:
        query = """
        SELECT id, ts_code, ann_date, title, url
        FROM tu_anns_d
        WHERE ann_date = :date
        """
        try:
            results = mysql_conn.execute_query(query, {'date': date})
            all_mysql_records.extend(results)
        except Exception as e:
            logger.error(f"查询日期 {date} 失败: {e}")
    
    logger.info(f"从MySQL获取了 {len(all_mysql_records)} 条记录")
    
    # 为每条MySQL记录计算哈希
    mysql_hashes = set()
    mysql_hash_to_record = {}
    
    for record in all_mysql_records:
        url = record['url']
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            stock_code = query_params.get('stockCode', [None])[0]
            announcement_id = query_params.get('announcementId', [None])[0]
            announcement_time = query_params.get('announcementTime', [None])[0]
            
            if announcement_id and announcement_time and stock_code:
                # 计算哈希（与document_processor.py逻辑一致）
                file_key = f"{announcement_time}_{stock_code}_{announcement_id}"
                file_hash = hashlib.md5(file_key.encode()).hexdigest()[:8]
                
                mysql_hashes.add(file_hash)
                mysql_hash_to_record[file_hash] = {
                    'ts_code': record['ts_code'],
                    'title': record['title'],
                    'ann_date': str(record['ann_date']),
                    'url': url,
                    'announcement_id': announcement_id
                }
        except Exception as e:
            logger.debug(f"解析URL失败: {e}")
    
    logger.info(f"计算了 {len(mysql_hashes)} 个MySQL记录的哈希")
    
    # 找出未匹配的PDF
    unmatched_pdfs = []
    matched_count = 0
    
    for pdf in all_pdfs:
        if pdf['hash'] in mysql_hashes:
            matched_count += 1
        else:
            unmatched_pdfs.append(pdf)
    
    logger.info(f"\n匹配结果:")
    logger.info(f"  已匹配: {matched_count}")
    logger.info(f"  未匹配: {len(unmatched_pdfs)}")
    
    if unmatched_pdfs:
        # 分析未匹配的PDF
        logger.info("\n未匹配PDF分析:")
        
        # 按日期统计
        by_date = defaultdict(list)
        for pdf in unmatched_pdfs:
            by_date[pdf['date']].append(pdf)
        
        logger.info("\n按日期分布:")
        for date in sorted(by_date.keys()):
            logger.info(f"  {date}: {len(by_date[date])} 个文件")
            
        # 按股票代码统计
        by_stock = defaultdict(list)
        for pdf in unmatched_pdfs:
            by_stock[pdf['stock_code']].append(pdf)
        
        logger.info("\n按股票代码分布（前20个）:")
        stock_counts = [(stock, len(pdfs)) for stock, pdfs in by_stock.items()]
        for stock, count in sorted(stock_counts, key=lambda x: x[1], reverse=True)[:20]:
            logger.info(f"  {stock}: {count} 个文件")
        
        # 显示一些样本
        logger.info("\n未匹配PDF样本:")
        for pdf in unmatched_pdfs[:10]:
            logger.info(f"  {pdf['filename']} ({pdf['size'] / 1024:.1f} KB)")
        
        # 保存详细列表
        output_file = "unmatched_pdfs_detail.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_pdfs': len(pdf_files),
                    'matched': matched_count,
                    'unmatched': len(unmatched_pdfs)
                },
                'unmatched_pdfs': unmatched_pdfs
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n详细信息已保存到: {output_file}")
    
    mysql_conn.close()

if __name__ == "__main__":
    find_unmatched_pdfs()