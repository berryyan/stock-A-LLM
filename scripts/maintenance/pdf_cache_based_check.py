"""
基于本地PDF缓存检查Milvus数据完整性
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from collections import defaultdict
import json
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger("pdf_cache_check")

class PDFCacheBasedChecker:
    """基于PDF缓存的数据检查器"""
    
    def __init__(self):
        self.mysql_conn = MySQLConnector()
        self.milvus_conn = MilvusConnector()
        self.pdf_cache_dir = Path("./data/pdfs/cache")
        self.results = {
            'cached_pdfs': [],
            'missing_in_milvus': [],
            'exists_in_milvus': [],
            'stats': {}
        }
        
        # 设置Milvus连接器的日志级别为WARNING，减少冗余输出
        import logging
        logging.getLogger('milvus_connector').setLevel(logging.WARNING)
    
    def scan_pdf_cache(self):
        """扫描本地PDF缓存目录"""
        logger.info("="*60)
        logger.info("扫描PDF缓存目录")
        logger.info(f"目录: {self.pdf_cache_dir}")
        
        if not self.pdf_cache_dir.exists():
            logger.error(f"PDF缓存目录不存在: {self.pdf_cache_dir}")
            return []
        
        pdf_files = list(self.pdf_cache_dir.glob("*.pdf"))
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 提取ann_id
        cached_ann_ids = []
        for pdf_file in pdf_files:
            # 文件名格式示例: 2025-03-19_300388_00e9225a.pdf
            # 或者: 2025-03-19_600050_3e0c439e.pdf
            filename = pdf_file.stem
            
            # 尝试不同的解析方式
            parts = filename.split('_')
            if len(parts) >= 3:
                # 格式: 日期_股票代码_ann_id
                potential_ann_id = parts[-1]  # 最后一部分可能是ann_id
                
                # 检查是否是有效的ann_id格式（通常是数字或十六进制）
                if potential_ann_id:
                    cached_ann_ids.append({
                        'filename': filename,
                        'ann_id': potential_ann_id,
                        'date': parts[0],
                        'stock_code': parts[1] if len(parts) > 1 else '',
                        'full_path': str(pdf_file)
                    })
            elif filename.replace('-', '').replace('_', '').isdigit():
                # 可能是纯数字格式
                cached_ann_ids.append({
                    'filename': filename,
                    'ann_id': filename,
                    'date': '',
                    'stock_code': '',
                    'full_path': str(pdf_file)
                })
        
        logger.info(f"解析出 {len(cached_ann_ids)} 个文件信息")
        
        # 显示一些样本
        if cached_ann_ids:
            logger.info("\n文件名样本:")
            for item in cached_ann_ids[:5]:
                logger.info(f"  {item['filename']} -> ann_id: {item['ann_id']}")
        
        self.results['cached_pdfs'] = cached_ann_ids
        
        return cached_ann_ids
    
    def check_mysql_info(self, pdf_info_list):
        """从MySQL获取这些PDF的详细信息"""
        logger.info("\n" + "="*60)
        logger.info("从MySQL获取PDF信息")
        
        ann_info = {}
        
        # 通过日期和股票代码批量查询
        logger.info("通过日期和股票代码查询...")
        
        # 按日期和股票代码分组
        by_date_stock = defaultdict(list)
        for item in pdf_info_list:
            if item['date'] and item['stock_code']:
                # 确保日期格式正确 (YYYY-MM-DD)
                key = (item['date'], item['stock_code'])
                by_date_stock[key].append(item)
        
        for (date, stock_code), items in by_date_stock.items():
            # 格式化股票代码（添加.SZ或.SH后缀）
            stock_codes = []
            if '.' not in stock_code:
                # 根据股票代码判断市场
                if stock_code.startswith('6'):
                    stock_codes = [f"{stock_code}.SH", stock_code]
                elif stock_code.startswith(('0', '3')):
                    stock_codes = [f"{stock_code}.SZ", stock_code]
                else:
                    stock_codes = [stock_code, f"{stock_code}.SZ", f"{stock_code}.SH"]
            else:
                stock_codes = [stock_code]
            
            # 构建查询 - MySQL中ann_date是date类型，直接使用YYYY-MM-DD格式
            placeholders = ','.join([f':code{i}' for i in range(len(stock_codes))])
            
            # 查询实际存在的字段
            query = f"""
            SELECT id, ts_code, ann_date, title, url, name
            FROM tu_anns_d
            WHERE ann_date = :date 
              AND ts_code IN ({placeholders})
            """
            
            params = {'date': date}  # 直接使用YYYY-MM-DD格式
            for i, code in enumerate(stock_codes):
                params[f'code{i}'] = code
            
            try:
                results = self.mysql_conn.execute_query(query, params)
                
                if not results:  # 如果没有结果，继续下一个
                    logger.debug(f"日期 {date} 股票 {stock_codes} 无数据")
                    continue
                
                # 对每个查询结果，尝试匹配PDF文件
                for row in results:
                    id_val = row['id']
                    ts_code = row['ts_code']
                    ann_date = row['ann_date']
                    title = row['title']
                    url = row['url']
                    name = row['name']
                    
                    # 从URL中提取announcement_id和announcement_time
                    # 根据document_processor.py中的extract_params_from_url方法
                    try:
                        from urllib.parse import urlparse, parse_qs
                        parsed_url = urlparse(url)
                        query_params = parse_qs(parsed_url.query)
                        
                        stock_code_from_url = query_params.get('stockCode', [None])[0]
                        announcement_id = query_params.get('announcementId', [None])[0]
                        announcement_time = query_params.get('announcementTime', [None])[0]
                        
                        if announcement_id and announcement_time and stock_code_from_url:
                            # 计算MD5哈希（与document_processor.py中的逻辑一致）
                            import hashlib
                            # 使用URL中的stock_code，而不是数据库中的ts_code
                            file_key = f"{announcement_time}_{stock_code_from_url}_{announcement_id}"
                            file_hash = hashlib.md5(file_key.encode()).hexdigest()[:8]
                            
                            # 查找匹配的PDF文件
                            for item in items:
                                if file_hash == item['ann_id']:  # ann_id字段实际上是文件名中的哈希部分
                                    # 构造PDF URL（从document_processor.py的逻辑）
                                    pdf_url = f"https://static.cninfo.com.cn/finalpage/{announcement_time}/{announcement_id}.pdf"
                                    
                                    ann_info[announcement_id] = {  # 使用announcement_id作为key
                                        'id': id_val,
                                        'ts_code': ts_code,
                                        'ann_date': str(ann_date),  # 确保是字符串格式
                                        'title': title,
                                        'name': name,
                                        'url': url,
                                        'pdf_url': pdf_url,
                                        'pdf_file': item['full_path'],
                                        'matched_by': 'hash_match',
                                        'announcement_id': announcement_id,
                                        'announcement_time': announcement_time,
                                        'stock_code_from_url': stock_code_from_url
                                    }
                                    logger.debug(f"匹配成功: {announcement_id} -> {file_hash}")
                                    break
                                else:
                                    logger.debug(f"哈希不匹配: 期望 {item['ann_id']}, 计算得到 {file_hash}")
                    except Exception as e:
                        logger.debug(f"解析URL失败: {url}, 错误: {e}")
                
            except Exception as e:
                logger.error(f"查询出错: {e}")
                logger.error(f"查询参数: date={date}, stock_codes={stock_codes}")
        
        logger.info(f"从MySQL匹配到 {len(ann_info)} 条记录 (共{len(pdf_info_list)}个PDF)")
        
        if ann_info:
            # 统计日期分布
            date_stats = defaultdict(int)
            for info in ann_info.values():
                date_stats[info['ann_date']] += 1
            
            logger.info("\nPDF缓存的日期分布:")
            for date, count in sorted(date_stats.items())[-10:]:
                logger.info(f"  {date}: {count} 个文件")
                
            # 显示一些匹配样本
            logger.info("\n匹配样本:")
            for i, (ann_id, info) in enumerate(list(ann_info.items())[:3]):
                logger.info(f"  {info['ts_code']} - {info['title'][:40]}...")
                logger.info(f"    PDF: {os.path.basename(info['pdf_file'])}")
                logger.info(f"    URL stockCode: {info['stock_code_from_url']}")
        else:
            logger.warning("\n未能匹配任何PDF文件")
            logger.info("可能的原因:")
            logger.info("1. PDF文件对应的公告不在MySQL中")
            logger.info("2. 日期格式不匹配")
            logger.info("3. 股票代码格式不匹配")
            logger.info("4. MD5计算逻辑不一致")
            
            # 显示调试信息
            if by_date_stock and pdf_info_list:
                # 选择一个样本进行详细调试
                sample_item = pdf_info_list[0]
                logger.info(f"\n调试信息 - PDF文件样本:")
                logger.info(f"  文件名: {sample_item['filename']}")
                logger.info(f"  解析的哈希: {sample_item['ann_id']}")
                logger.info(f"  日期: {sample_item['date']}")
                logger.info(f"  股票代码: {sample_item['stock_code']}")
                
                # 尝试查询这个日期的任意一条记录
                debug_query = """
                SELECT id, ts_code, ann_date, title, url
                FROM tu_anns_d
                WHERE ann_date = :date
                LIMIT 1
                """
                try:
                    debug_results = self.mysql_conn.execute_query(debug_query, {'date': sample_item['date']})
                    if debug_results:
                        debug_row = debug_results[0]
                        logger.info(f"\n数据库中该日期的样本记录:")
                        logger.info(f"  ts_code: {debug_row['ts_code']}")
                        logger.info(f"  title: {debug_row['title'][:50]}...")
                        logger.info(f"  url: {debug_row['url']}")
                        
                        # 尝试解析这个URL
                        try:
                            from urllib.parse import urlparse, parse_qs
                            parsed = urlparse(debug_row['url'])
                            params = parse_qs(parsed.query)
                            logger.info(f"  URL参数:")
                            logger.info(f"    stockCode: {params.get('stockCode', ['未找到'])[0]}")
                            logger.info(f"    announcementId: {params.get('announcementId', ['未找到'])[0]}")
                            logger.info(f"    announcementTime: {params.get('announcementTime', ['未找到'])[0]}")
                        except:
                            pass
                except Exception as e:
                    logger.error(f"调试查询失败: {e}")
        
        return ann_info, pdf_info_list
    
    def check_milvus_vectors(self, ann_info):
        """检查这些PDF是否在Milvus中有对应的向量"""
        logger.info("\n" + "="*60)
        logger.info("检查Milvus向量数据")
        
        missing_in_milvus = []
        exists_in_milvus = []
        
        total = len(ann_info)
        checked = 0
        
        for ann_id, info in ann_info.items():
            # 使用announcement_id而不是ann_id来构建doc_id
            announcement_id = info.get('announcement_id', ann_id)
            
            # 检查是否存在于Milvus（doc_id格式：announcement_id_chunk_id）
            expr = f'doc_id == "{announcement_id}_0"'
            results = self.milvus_conn.query(
                expr=expr,
                output_fields=["doc_id", "chunk_id"],
                limit=1
            )
            
            if results:
                exists_in_milvus.append(info)
            else:
                missing_in_milvus.append(info)
            
            checked += 1
            if checked % 100 == 0:
                logger.info(f"进度: {checked}/{total}")
        
        logger.info(f"\n检查完成:")
        logger.info(f"  存在于Milvus: {len(exists_in_milvus)}")
        logger.info(f"  缺失于Milvus: {len(missing_in_milvus)}")
        
        self.results['missing_in_milvus'] = missing_in_milvus
        self.results['exists_in_milvus'] = exists_in_milvus
        
        return missing_in_milvus
    
    def analyze_missing_pattern(self, missing_records):
        """分析缺失数据的模式"""
        logger.info("\n" + "="*60)
        logger.info("分析缺失模式")
        
        if not missing_records:
            logger.info("没有缺失记录")
            return
        
        # 按日期分析
        by_date = defaultdict(list)
        for record in missing_records:
            by_date[record['ann_date']].append(record)
        
        logger.info("\n缺失记录的日期分布:")
        for date, records in sorted(by_date.items()):
            logger.info(f"  {date}: {len(records)} 条")
            # 显示一些样本
            for r in records[:2]:
                logger.info(f"    - {r['ts_code']} | {r['title'][:40]}...")
        
        # 按股票分析
        by_stock = defaultdict(list)
        for record in missing_records:
            by_stock[record['ts_code']].append(record)
        
        logger.info("\n缺失最多的股票TOP10:")
        stock_counts = [(stock, len(records)) for stock, records in by_stock.items()]
        for stock, count in sorted(stock_counts, key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {stock}: {count} 条")
        
        self.results['stats'] = {
            'by_date': {date: len(records) for date, records in by_date.items()},
            'top_missing_stocks': sorted(stock_counts, key=lambda x: x[1], reverse=True)[:20]
        }
    
    def generate_recovery_script(self, missing_records):
        """生成恢复脚本"""
        logger.info("\n" + "="*60)
        logger.info("生成恢复方案")
        
        if not missing_records:
            logger.info("没有需要恢复的记录")
            return
        
        # 按日期分组
        by_date = defaultdict(list)
        for record in missing_records:
            # 使用announcement_id而不是ann_id
            announcement_id = record.get('announcement_id', record.get('ann_id', ''))
            if announcement_id:
                by_date[record['ann_date']].append(announcement_id)
        
        # 生成恢复命令
        recovery_commands = []
        
        logger.info("\n恢复命令:")
        
        # 方法1：使用新的恢复脚本（推荐）
        logger.info("方法1 - 使用专用恢复脚本（推荐）:")
        logger.info("  python -m scripts.maintenance.recovery_missing_vectors")
        logger.info("  # 这会自动读取missing_in_milvus.json并恢复所有缺失记录")
        
        # 方法2：手动指定announcement_ids
        logger.info("\n方法2 - 手动恢复特定记录:")
        for date, ann_ids in sorted(by_date.items()):
            # 分批，每批50个
            for i in range(0, len(ann_ids), 50):
                batch = ann_ids[i:i+50]
                cmd = f"python -m scripts.maintenance.recovery_missing_vectors --ann-ids {','.join(batch)}"
                recovery_commands.append(cmd)
                
                if len(recovery_commands) <= 3:  # 只显示前3个命令
                    logger.info(f"  {cmd[:100]}...")
        
        # 保存完整的恢复脚本
        with open('recovery_commands.txt', 'w', encoding='utf-8') as f:
            f.write("# 向量数据恢复脚本\n")
            f.write(f"# 生成时间: {datetime.now()}\n")
            f.write(f"# 缺失记录数: {len(missing_records)}\n\n")
            
            # 添加说明
            f.write("# 说明：这些PDF文件已经在本地缓存，只需要重新生成向量\n\n")
            
            # 方法1
            f.write("# 方法1 - 推荐：使用专用恢复脚本\n")
            f.write("python -m scripts.maintenance.recovery_missing_vectors\n\n")
            
            # 方法2
            f.write("# 方法2 - 备选：手动恢复特定记录\n")
            for cmd in recovery_commands:
                f.write(cmd + "\n")
        
        logger.info(f"\n完整恢复脚本已保存到: recovery_commands.txt")
        logger.info(f"共 {len(recovery_commands)} 个手动命令")
        
        # 显示额外信息
        logger.info("\n恢复建议:")
        logger.info("1. 这些PDF文件已在本地缓存，恢复会很快")
        logger.info("2. 建议在系统负载较低时执行恢复")
        logger.info("3. 如果某些PDF需要OCR，会记录到 data/ocr_needed_files.json")
    
    def save_results(self):
        """保存检查结果"""
        # 保存详细结果
        with open('pdf_cache_check_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 保存缺失记录列表
        if self.results['missing_in_milvus']:
            with open('missing_in_milvus.json', 'w', encoding='utf-8') as f:
                json.dump(self.results['missing_in_milvus'], f, ensure_ascii=False, indent=2)
        
        logger.info("\n检查结果已保存到:")
        logger.info("  - pdf_cache_check_results.json (完整结果)")
        logger.info("  - missing_in_milvus.json (缺失记录)")
        logger.info("  - recovery_commands.txt (恢复命令)")
    
    def run_quick_check(self, sample_size=10):
        """快速检查：只检查部分样本"""
        logger.info("\n" + "="*60)
        logger.info(f"快速检查模式：抽样 {sample_size} 个文件")
        
        # 扫描PDF
        all_pdf_info = self.scan_pdf_cache()
        if not all_pdf_info:
            return
        
        # 随机抽样
        import random
        sample_pdf_info = random.sample(all_pdf_info, min(sample_size, len(all_pdf_info)))
        
        # 获取MySQL信息
        ann_info, pdf_info_with_mysql = self.check_mysql_info(sample_pdf_info)
        
        if not ann_info:
            logger.warning("\n无法从MySQL匹配任何记录")
            logger.info("可能原因：")
            logger.info("1. ann_id格式不匹配")
            logger.info("2. 这些PDF对应的记录不在MySQL中")
            logger.info("3. 文件名解析规则需要调整")
            
            # 显示一些文件名样本供分析
            logger.info("\n文件名样本供分析:")
            for item in sample_pdf_info[:5]:
                logger.info(f"  文件: {item['filename']}")
                logger.info(f"    解析的ann_id: {item['ann_id']}")
                logger.info(f"    日期: {item['date']}")
                logger.info(f"    股票: {item['stock_code']}")
            return
        
        # 检查Milvus
        missing = self.check_milvus_vectors(ann_info)
        
        if missing:
            logger.warning(f"\n样本中发现 {len(missing)} 个缺失记录!")
            logger.warning("建议运行完整检查")
        else:
            logger.info("\n✓ 样本检查通过，数据完整性良好")
    
    def close(self):
        """关闭连接"""
        self.mysql_conn.close()
        self.milvus_conn.close()


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='基于PDF缓存检查向量数据完整性')
    parser.add_argument('--quick', action='store_true', help='快速检查模式(抽样)')
    parser.add_argument('--sample-size', type=int, default=10, help='快速检查的样本大小')
    
    args = parser.parse_args()
    
    checker = PDFCacheBasedChecker()
    
    try:
        if args.quick:
            # 快速检查
            checker.run_quick_check(args.sample_size)
        else:
            # 完整检查
            logger.info("开始完整数据检查...")
            
            # 1. 扫描PDF缓存
            cached_pdfs = checker.scan_pdf_cache()
            if not cached_pdfs:
                logger.error("没有找到PDF缓存文件")
                return
            
            # 2. 获取MySQL信息
            ann_info, pdf_info_with_mysql = checker.check_mysql_info(cached_pdfs)
            
            # 3. 检查Milvus向量
            missing_records = checker.check_milvus_vectors(ann_info)
            
            # 4. 分析缺失模式
            checker.analyze_missing_pattern(missing_records)
            
            # 5. 生成恢复脚本
            checker.generate_recovery_script(missing_records)
            
            # 6. 保存结果
            checker.save_results()
            
            # 总结
            logger.info("\n" + "="*60)
            logger.info("检查完成！")
            logger.info(f"PDF缓存总数: {len(cached_pdfs)}")
            logger.info(f"MySQL匹配数: {len(ann_info)}")
            logger.info(f"在Milvus中: {len(checker.results['exists_in_milvus'])}")
            logger.info(f"缺失: {len(missing_records)}")
            if len(ann_info) > 0:
                logger.info(f"缺失率: {len(missing_records)/len(ann_info)*100:.2f}%")
            
            if len(missing_records) > 0:
                logger.info("\n建议执行恢复脚本:")
                logger.info("  python -m scripts.maintenance.recovery_missing_vectors")
                logger.info("\n这会自动从missing_in_milvus.json读取并恢复所有缺失记录")
            
    except Exception as e:
        logger.error(f"检查过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        checker.close()


if __name__ == "__main__":
    main()