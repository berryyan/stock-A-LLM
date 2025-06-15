"""
安全批处理脚本 - 处理公告并监控错误
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import DocumentProcessor
from database.mysql_connector import MySQLConnector
import time
import json
from datetime import datetime
from pathlib import Path


class SafeBatchProcessor:
    """安全的批处理器"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.mysql = MySQLConnector()
        self.log_file = Path("data/processing_log.json")
        self.error_log = Path("data/error_log.json")
        
        # 加载历史记录
        self.processed_ids = self.load_processed_ids()
        self.errors = self.load_errors()
    
    def load_processed_ids(self):
        """加载已处理的公告ID"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
        return set()
    
    def load_errors(self):
        """加载错误记录"""
        if self.error_log.exists():
            with open(self.error_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_state(self):
        """保存状态"""
        # 保存已处理ID
        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_ids': list(self.processed_ids),
                'last_update': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # 保存错误日志
        with open(self.error_log, 'w', encoding='utf-8') as f:
            json.dump(self.errors, f, ensure_ascii=False, indent=2)
    
    def process_with_safety(self, 
                          start_date='20250422',
                          end_date='20250422',
                          title_keywords=['年度报告'],
                          max_items=10,
                          sleep_range=(15, 25)):
        """
        安全地批处理公告
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            title_keywords: 标题关键词
            max_items: 最大处理数量
            sleep_range: 休眠时间范围
        """
        print(f"\n开始安全批处理")
        print(f"日期: {start_date} - {end_date}")
        print(f"关键词: {title_keywords}")
        print(f"最大处理数: {max_items}")
        print(f"休眠时间: {sleep_range[0]}-{sleep_range[1]}秒")
        print(f"已处理: {len(self.processed_ids)} 个公告")
        
        # 查询公告
        query = f"""
        SELECT ts_code, name, title, url, ann_date
        FROM tu_anns_d
        WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        announcements = self.mysql.execute_query(query)
        
        # 过滤
        filtered = []
        for ann in announcements:
            # 检查是否已处理
            ann_id = self._get_announcement_id(ann['url'])
            if ann_id in self.processed_ids:
                continue
            
            # 检查关键词
            if any(keyword in ann['title'] for keyword in title_keywords):
                filtered.append(ann)
        
        print(f"待处理: {len(filtered)} 个公告")
        
        if len(filtered) == 0:
            print("没有新的公告需要处理")
            return
        
        # 限制处理数量
        to_process = filtered[:max_items]
        print(f"本次处理: {len(to_process)} 个公告")
        
        # 处理统计
        success_count = 0
        pdf_fail_count = 0
        milvus_fail_count = 0
        
        for i, ann in enumerate(to_process):
            print(f"\n[{i+1}/{len(to_process)}] 处理: {ann['ts_code']} - {ann['title'][:50]}...")
            
            try:
                # 处理公告
                result = self._process_single_announcement(ann)
                
                if result['success']:
                    success_count += 1
                    # 记录成功
                    ann_id = self._get_announcement_id(ann['url'])
                    self.processed_ids.add(ann_id)
                    print(f"  ✓ 成功")
                else:
                    # 记录错误
                    if 'PDF下载失败' in result['error']:
                        pdf_fail_count += 1
                    elif 'Milvus' in result['error']:
                        milvus_fail_count += 1
                    
                    self.errors.append({
                        'timestamp': datetime.now().isoformat(),
                        'announcement': ann,
                        'error': result['error']
                    })
                    print(f"  ✗ 失败: {result['error']}")
                
                # 保存状态
                if (i + 1) % 5 == 0:  # 每5个保存一次
                    self.save_state()
                
                # 休眠
                if i < len(to_process) - 1:
                    sleep_time = time.uniform(*sleep_range)
                    print(f"  休眠 {sleep_time:.1f} 秒...")
                    time.sleep(sleep_time)
                    
            except KeyboardInterrupt:
                print("\n\n用户中断!")
                break
            except Exception as e:
                print(f"  ✗ 未预期错误: {e}")
                self.errors.append({
                    'timestamp': datetime.now().isoformat(),
                    'announcement': ann,
                    'error': str(e)
                })
        
        # 最终保存
        self.save_state()
        
        # 打印统计
        print("\n" + "=" * 60)
        print("处理完成统计:")
        print(f"  成功: {success_count}")
        print(f"  PDF下载失败: {pdf_fail_count}")
        print(f"  Milvus存储失败: {milvus_fail_count}")
        print(f"  其他失败: {len(to_process) - success_count - pdf_fail_count - milvus_fail_count}")
        print(f"  总计已处理: {len(self.processed_ids)}")
        
        # 如果有错误，显示最近的几个
        if self.errors:
            print(f"\n最近的错误 (共{len(self.errors)}个):")
            for err in self.errors[-3:]:
                ann = err['announcement']
                print(f"  - {ann['ts_code']} {ann['title'][:30]}...")
                print(f"    错误: {err['error']}")
    
    def _get_announcement_id(self, url):
        """从URL提取公告ID"""
        try:
            _, ann_id, _ = self.processor.extract_params_from_url(url)
            return ann_id
        except:
            return url  # 如果解析失败，使用URL作为ID
    
    def _process_single_announcement(self, announcement):
        """处理单个公告并返回结果"""
        try:
            docs = self.processor.process_announcement(announcement)
            if docs:
                # 尝试存储到Milvus
                try:
                    success = self.processor.store_documents_to_milvus(docs)
                    if success:
                        return {'success': True}
                    else:
                        return {'success': False, 'error': 'Milvus存储失败'}
                except Exception as e:
                    return {'success': False, 'error': f'Milvus错误: {str(e)}'}
            else:
                return {'success': False, 'error': 'PDF处理失败'}
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'PDF下载失败' in error_msg:
                return {'success': False, 'error': 'PDF下载失败(404)'}
            else:
                return {'success': False, 'error': error_msg}
    
    def show_status(self):
        """显示当前状态"""
        print("\n当前处理状态:")
        print(f"  已处理公告数: {len(self.processed_ids)}")
        print(f"  错误记录数: {len(self.errors)}")
        
        if self.errors:
            # 统计错误类型
            error_types = {}
            for err in self.errors:
                error_type = err['error'].split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print("\n错误类型统计:")
            for err_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {err_type}: {count}")


def main():
    """主函数"""
    processor = SafeBatchProcessor()
    
    # 显示当前状态
    processor.show_status()
    
    # 用户确认
    print("\n准备开始处理...")
    input("按Enter继续，Ctrl+C取消...")
    
    # 开始处理
    processor.process_with_safety(
        start_date='20250422',
        end_date='20250422',
        title_keywords=['年度报告'],
        max_items=5,  # 先处理5个
        sleep_range=(20, 30)  # 安全的休眠时间
    )


if __name__ == "__main__":
    main()
