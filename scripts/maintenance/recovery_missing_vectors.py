"""
恢复缺失向量的专用脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from rag.document_processor import DocumentProcessor
from utils.logger import setup_logger
import json
from pathlib import Path

logger = setup_logger("vector_recovery")

class VectorRecovery:
    def __init__(self):
        self.mysql_conn = MySQLConnector()
        self.milvus_conn = MilvusConnector()
        self.processor = DocumentProcessor()
        
    def recover_by_announcement_ids(self, announcement_ids):
        """根据announcement_id列表恢复向量"""
        logger.info(f"准备恢复 {len(announcement_ids)} 个公告的向量")
        
        success_count = 0
        failed_count = 0
        
        for ann_id in announcement_ids:
            logger.info(f"\n处理 announcement_id: {ann_id}")
            
            # 查询MySQL获取公告信息
            query = """
            SELECT ts_code, name, title, url, ann_date
            FROM tu_anns_d
            WHERE url LIKE :pattern
            """
            
            results = self.mysql_conn.execute_query(
                query, 
                {"pattern": f"%announcementId={ann_id}%"}
            )
            
            if not results:
                logger.error(f"未找到 announcement_id={ann_id} 的记录")
                failed_count += 1
                continue
                
            # 应该只有一条记录
            row = results[0]
            announcement = {
                'ts_code': row['ts_code'],
                'name': row['name'],
                'title': row['title'],
                'url': row['url'],
                'ann_date': str(row['ann_date'])
            }
            
            logger.info(f"找到公告: {announcement['ts_code']} - {announcement['title'][:50]}...")
            
            try:
                # 处理公告
                docs = self.processor.process_announcement(announcement)
                
                if docs:
                    # 存储到Milvus
                    if self.processor.store_documents_to_milvus(docs):
                        logger.info(f"✓ 成功恢复 {len(docs)} 个文档块")
                        success_count += 1
                    else:
                        logger.error(f"✗ 存储到Milvus失败")
                        failed_count += 1
                else:
                    logger.error(f"✗ 文档处理失败")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"✗ 处理失败: {e}")
                failed_count += 1
        
        logger.info(f"\n恢复完成: 成功 {success_count}, 失败 {failed_count}")
        return success_count, failed_count
    
    def recover_from_json(self, json_file="missing_in_milvus.json"):
        """从JSON文件恢复缺失的向量"""
        if not Path(json_file).exists():
            logger.error(f"文件不存在: {json_file}")
            return
            
        with open(json_file, 'r', encoding='utf-8') as f:
            missing_records = json.load(f)
            
        logger.info(f"从 {json_file} 加载了 {len(missing_records)} 条缺失记录")
        
        # 提取announcement_id
        announcement_ids = []
        for record in missing_records:
            ann_id = record.get('announcement_id')
            if ann_id:
                announcement_ids.append(ann_id)
            else:
                logger.warning(f"记录缺少announcement_id: {record}")
        
        if announcement_ids:
            return self.recover_by_announcement_ids(announcement_ids)
        else:
            logger.error("没有找到有效的announcement_id")
            return 0, 0
    
    def close(self):
        self.mysql_conn.close()
        self.milvus_conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='恢复缺失的向量数据')
    parser.add_argument('--ann-ids', type=str, help='逗号分隔的announcement_id列表')
    parser.add_argument('--from-json', action='store_true', help='从missing_in_milvus.json恢复')
    parser.add_argument('--json-file', type=str, default='missing_in_milvus.json', help='JSON文件路径')
    
    args = parser.parse_args()
    
    recovery = VectorRecovery()
    
    try:
        if args.from_json:
            # 从JSON文件恢复
            recovery.recover_from_json(args.json_file)
        elif args.ann_ids:
            # 从命令行参数恢复
            ann_ids = args.ann_ids.split(',')
            recovery.recover_by_announcement_ids(ann_ids)
        else:
            # 默认从JSON文件恢复
            logger.info("使用默认方式：从missing_in_milvus.json恢复")
            recovery.recover_from_json()
            
    except Exception as e:
        logger.error(f"恢复过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        recovery.close()


if __name__ == "__main__":
    main()