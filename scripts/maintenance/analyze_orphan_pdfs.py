"""
分析没有MySQL记录的PDF文件
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from database.mysql_connector import MySQLConnector
from collections import defaultdict
import json
from utils.logger import setup_logger

logger = setup_logger("orphan_pdf_analysis")

def analyze_orphan_pdfs():
    """分析没有MySQL记录的PDF文件"""
    mysql_conn = MySQLConnector()
    pdf_cache_dir = Path("./data/pdfs/cache")
    
    # 获取所有PDF文件
    pdf_files = list(pdf_cache_dir.glob("*.pdf"))
    logger.info(f"总共找到 {len(pdf_files)} 个PDF文件")
    
    # 先获取所有有MySQL记录的PDF信息
    matched_pdfs = set()
    
    # 按日期分组PDF文件
    pdf_by_date = defaultdict(list)
    for pdf_file in pdf_files:
        filename = pdf_file.stem
        parts = filename.split('_')
        if len(parts) >= 3:
            date = parts[0]
            stock_code = parts[1]
            hash_part = parts[2]
            
            pdf_by_date[date].append({
                'filename': filename,
                'stock_code': stock_code,
                'hash': hash_part,
                'full_path': str(pdf_file),
                'size': pdf_file.stat().st_size
            })
    
    # 检查每个日期的PDF
    orphan_pdfs = []
    
    for date, pdfs in pdf_by_date.items():
        # 获取该日期所有股票代码
        stock_codes_in_pdfs = set(p['stock_code'] for p in pdfs)
        
        # 查询MySQL中该日期的所有记录
        query = """
        SELECT ts_code, title, url
        FROM tu_anns_d
        WHERE ann_date = :date
        """
        
        try:
            results = mysql_conn.execute_query(query, {'date': date})
            
            # 提取MySQL中的股票代码（去掉.SZ/.SH后缀）
            mysql_stock_codes = set()
            for row in results:
                ts_code = row['ts_code']
                if '.' in ts_code:
                    mysql_stock_codes.add(ts_code.split('.')[0])
                else:
                    mysql_stock_codes.add(ts_code)
            
            # 找出在PDF中但不在MySQL中的股票
            for pdf in pdfs:
                if pdf['stock_code'] not in mysql_stock_codes:
                    orphan_pdfs.append(pdf)
                else:
                    matched_pdfs.add(pdf['filename'])
                    
        except Exception as e:
            logger.error(f"查询日期 {date} 失败: {e}")
    
    # 分析孤儿PDF
    logger.info(f"\n找到 {len(orphan_pdfs)} 个没有MySQL记录的PDF文件")
    
    if orphan_pdfs:
        # 按日期统计
        orphan_by_date = defaultdict(list)
        for pdf in orphan_pdfs:
            date = pdf['filename'].split('_')[0]
            orphan_by_date[date].append(pdf)
        
        logger.info("\n按日期分布:")
        for date in sorted(orphan_by_date.keys()):
            logger.info(f"  {date}: {len(orphan_by_date[date])} 个文件")
        
        # 按股票代码统计
        orphan_by_stock = defaultdict(list)
        for pdf in orphan_pdfs:
            orphan_by_stock[pdf['stock_code']].append(pdf)
        
        logger.info("\n按股票代码分布（前20个）:")
        stock_counts = [(stock, len(pdfs)) for stock, pdfs in orphan_by_stock.items()]
        for stock, count in sorted(stock_counts, key=lambda x: x[1], reverse=True)[:20]:
            logger.info(f"  {stock}: {count} 个文件")
        
        # 文件大小分析
        total_size = sum(pdf['size'] for pdf in orphan_pdfs)
        avg_size = total_size / len(orphan_pdfs) if orphan_pdfs else 0
        logger.info(f"\n文件大小统计:")
        logger.info(f"  总大小: {total_size / 1024 / 1024:.2f} MB")
        logger.info(f"  平均大小: {avg_size / 1024:.2f} KB")
        
        # 保存详细列表
        output_file = "orphan_pdfs.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(orphan_pdfs, f, ensure_ascii=False, indent=2)
        logger.info(f"\n详细列表已保存到: {output_file}")
        
        # 显示一些样本
        logger.info("\n样本文件:")
        for pdf in orphan_pdfs[:5]:
            logger.info(f"  {pdf['filename']} ({pdf['size'] / 1024:.1f} KB)")
    
    mysql_conn.close()

if __name__ == "__main__":
    analyze_orphan_pdfs()