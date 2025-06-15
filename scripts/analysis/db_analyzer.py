#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tushare数据库全面分析脚本
用于检查数据库表结构、数据质量和完整性
生成详细的分析报告，为股票分析系统开发提供数据基础
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect, text
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'tushare_db_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TushareDBAnalyzer:
    """Tushare数据库分析器"""
    
    def __init__(self, host='10.0.0.77', port=3306, database='Tushare', 
                 user='readonly_user', password='Tushare2024'):
        """初始化数据库连接"""
        self.connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        try:
            self.engine = create_engine(self.connection_string)
            self.inspector = inspect(self.engine)
            logger.info(f"成功连接到数据库: {database}@{host}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
            
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        tables = self.inspector.get_table_names()
        tu_tables = [t for t in tables if t.startswith('tu_')]
        logger.info(f"找到 {len(tu_tables)} 个 tu_ 开头的表")
        return sorted(tu_tables)
        
    def analyze_table_structure(self, table_name: str) -> Dict:
        """分析表结构"""
        try:
            # 获取列信息
            columns = self.inspector.get_columns(table_name)
            
            # 获取主键
            pk = self.inspector.get_pk_constraint(table_name)
            
            # 获取索引
            indexes = self.inspector.get_indexes(table_name)
            
            # 获取外键
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            # 获取表注释和列注释
            table_comment = self._get_table_comment(table_name)
            columns_with_comments = self._get_columns_with_comments(table_name, columns)
            
            return {
                'table_name': table_name,
                'table_comment': table_comment,
                'columns': columns_with_comments,
                'primary_key': pk,
                'indexes': indexes,
                'foreign_keys': foreign_keys,
                'column_count': len(columns)
            }
        except Exception as e:
            logger.error(f"分析表 {table_name} 结构时出错: {e}")
            return None
            
    def analyze_table_data(self, table_name: str) -> Dict:
        """分析表数据"""
        try:
            # 获取记录数
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = pd.read_sql(count_query, self.engine)
            record_count = int(result['count'].iloc[0])
            
            # 获取数据时间范围
            date_columns = self._get_date_columns(table_name)
            date_ranges = {}
            
            for date_col in date_columns:
                try:
                    range_query = f"""
                    SELECT 
                        MIN({date_col}) as min_date,
                        MAX({date_col}) as max_date
                    FROM {table_name}
                    WHERE {date_col} IS NOT NULL
                    """
                    range_result = pd.read_sql(range_query, self.engine)
                    if not range_result.empty:
                        date_ranges[date_col] = {
                            'min': str(range_result['min_date'].iloc[0]),
                            'max': str(range_result['max_date'].iloc[0])
                        }
                except:
                    continue
                    
            # 获取样本数据
            sample_query = f"SELECT * FROM {table_name} LIMIT 5"
            sample_data = pd.read_sql(sample_query, self.engine)
            
            # 特殊表的额外分析
            extra_info = {}
            if table_name == 'tu_stock_basic':
                extra_info = self._analyze_stock_basic()
            elif table_name == 'tu_daily_basic':
                extra_info = self._analyze_daily_basic()
            elif table_name in ['tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator']:
                extra_info = self._analyze_financial_table(table_name)
                
            return {
                'record_count': record_count,
                'date_ranges': date_ranges,
                'sample_columns': list(sample_data.columns),
                'extra_info': extra_info
            }
            
        except Exception as e:
            logger.error(f"分析表 {table_name} 数据时出错: {e}")
            return {'record_count': 0, 'error': str(e)}
            
    def _get_table_comment(self, table_name: str) -> str:
        """获取表的中文注释"""
        try:
            query = """
            SELECT TABLE_COMMENT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = :table_name
            """
            result = pd.read_sql(query, self.engine, params={'table_name': table_name})
            if not result.empty:
                return result['TABLE_COMMENT'].iloc[0] or ''
            return ''
        except Exception as e:
            logger.error(f"获取表 {table_name} 注释时出错: {e}")
            return ''
            
    def _get_columns_with_comments(self, table_name: str, columns: List[Dict]) -> List[Dict]:
        """获取带有中文注释的列信息"""
        try:
            # 查询列的注释信息
            query = """
            SELECT 
                COLUMN_NAME,
                COLUMN_COMMENT,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
            """
            
            comments_df = pd.read_sql(query, self.engine, params={'table_name': table_name})
            
            # 将注释信息合并到列信息中
            columns_with_comments = []
            for col in columns:
                col_name = col['name']
                col_info = col.copy()
                
                # 查找对应的注释
                comment_row = comments_df[comments_df['COLUMN_NAME'] == col_name]
                if not comment_row.empty:
                    col_info['comment'] = comment_row['COLUMN_COMMENT'].iloc[0] or ''
                    col_info['column_type'] = comment_row['COLUMN_TYPE'].iloc[0]
                    col_info['is_nullable'] = comment_row['IS_NULLABLE'].iloc[0]
                    col_info['column_key'] = comment_row['COLUMN_KEY'].iloc[0]
                else:
                    col_info['comment'] = ''
                    
                columns_with_comments.append(col_info)
                
            return columns_with_comments
            
        except Exception as e:
            logger.error(f"获取表 {table_name} 列注释时出错: {e}")
            # 如果出错，返回原始列信息
            return columns
            
    def _get_date_columns(self, table_name: str) -> List[str]:
        """获取日期类型的列"""
        columns = self.inspector.get_columns(table_name)
        date_columns = []
        
        for col in columns:
            col_name = col['name'].lower()
            # 通过列名判断日期列
            if any(keyword in col_name for keyword in ['date', 'time', 'day']):
                date_columns.append(col['name'])
            # 通过类型判断
            elif str(col['type']).upper() in ['DATE', 'DATETIME', 'TIMESTAMP']:
                date_columns.append(col['name'])
                
        return date_columns
        
    def _analyze_stock_basic(self) -> Dict:
        """分析股票基本信息表"""
        try:
            query = """
            SELECT 
                list_status,
                COUNT(*) as count,
                COUNT(DISTINCT industry) as industry_count
            FROM tu_stock_basic
            GROUP BY list_status
            """
            result = pd.read_sql(query, self.engine)
            
            # 获取行业分布
            industry_query = """
            SELECT 
                industry,
                COUNT(*) as count
            FROM tu_stock_basic
            WHERE list_status = 'L'
            GROUP BY industry
            ORDER BY count DESC
            LIMIT 10
            """
            industry_result = pd.read_sql(industry_query, self.engine)
            
            return {
                'status_distribution': result.to_dict('records'),
                'top_industries': industry_result.to_dict('records')
            }
        except:
            return {}
            
    def _analyze_daily_basic(self) -> Dict:
        """分析每日指标表"""
        try:
            # 获取最新交易日
            latest_query = """
            SELECT 
                trade_date,
                COUNT(*) as stock_count,
                AVG(pe) as avg_pe,
                AVG(pb) as avg_pb,
                SUM(total_mv) / 10000 as total_market_cap_billion
            FROM tu_daily_basic
            WHERE trade_date = (SELECT MAX(trade_date) FROM tu_daily_basic)
            GROUP BY trade_date
            """
            result = pd.read_sql(latest_query, self.engine)
            
            return {
                'latest_trade_date': str(result['trade_date'].iloc[0]) if not result.empty else None,
                'stock_count': int(result['stock_count'].iloc[0]) if not result.empty else 0,
                'market_stats': {
                    'avg_pe': float(result['avg_pe'].iloc[0]) if not result.empty else None,
                    'avg_pb': float(result['avg_pb'].iloc[0]) if not result.empty else None,
                    'total_market_cap_billion': float(result['total_market_cap_billion'].iloc[0]) if not result.empty else None
                }
            }
        except:
            return {}
            
    def _analyze_financial_table(self, table_name: str) -> Dict:
        """分析财务报表"""
        try:
            # 获取最新报告期
            query = f"""
            SELECT 
                end_date,
                COUNT(DISTINCT ts_code) as company_count
            FROM {table_name}
            GROUP BY end_date
            ORDER BY end_date DESC
            LIMIT 5
            """
            result = pd.read_sql(query, self.engine)
            
            return {
                'recent_periods': result.to_dict('records')
            }
        except:
            return {}
            
    def check_data_completeness(self) -> Dict:
        """检查数据完整性"""
        completeness = {
            'daily_data': self._check_daily_completeness(),
            'financial_data': self._check_financial_completeness(),
            'basic_data': self._check_basic_completeness()
        }
        return completeness
        
    def _check_daily_completeness(self) -> Dict:
        """检查日线数据完整性"""
        try:
            # 检查最近30天的数据完整性
            query = """
            SELECT 
                d.trade_date,
                COUNT(DISTINCT d.ts_code) as daily_count,
                COUNT(DISTINCT b.ts_code) as basic_count
            FROM tu_daily_detail d
            LEFT JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
            WHERE d.trade_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY d.trade_date
            ORDER BY d.trade_date DESC
            """
            result = pd.read_sql(query, self.engine)
            
            return {
                'recent_30days': result.to_dict('records'),
                'avg_daily_stocks': int(result['daily_count'].mean()) if not result.empty else 0,
                'avg_basic_stocks': int(result['basic_count'].mean()) if not result.empty else 0
            }
        except:
            return {}
            
    def _check_financial_completeness(self) -> Dict:
        """检查财务数据完整性"""
        try:
            # 检查最新季度的财务数据
            query = """
            SELECT 
                table_name,
                end_date,
                company_count
            FROM (
                SELECT 'income' as table_name, end_date, COUNT(DISTINCT ts_code) as company_count
                FROM tu_income
                WHERE end_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY end_date
                
                UNION ALL
                
                SELECT 'balancesheet' as table_name, end_date, COUNT(DISTINCT ts_code) as company_count
                FROM tu_balancesheet
                WHERE end_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY end_date
                
                UNION ALL
                
                SELECT 'cashflow' as table_name, end_date, COUNT(DISTINCT ts_code) as company_count
                FROM tu_cashflow
                WHERE end_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY end_date
            ) t
            ORDER BY end_date DESC, table_name
            """
            result = pd.read_sql(query, self.engine)
            
            return {
                'recent_financial_data': result.to_dict('records') if not result.empty else []
            }
        except:
            return {}
            
    def _check_basic_completeness(self) -> Dict:
        """检查基础数据完整性"""
        try:
            # 检查股票基本信息
            stock_query = """
            SELECT 
                COUNT(*) as total_stocks,
                SUM(CASE WHEN list_status = 'L' THEN 1 ELSE 0 END) as listed_stocks,
                SUM(CASE WHEN list_status = 'D' THEN 1 ELSE 0 END) as delisted_stocks,
                SUM(CASE WHEN list_status = 'P' THEN 1 ELSE 0 END) as paused_stocks
            FROM tu_stock_basic
            """
            stock_result = pd.read_sql(stock_query, self.engine)
            
            return {
                'stock_statistics': stock_result.to_dict('records')[0] if not stock_result.empty else {}
            }
        except:
            return {}
            
    def generate_field_dictionary(self) -> pd.DataFrame:
        """生成所有表的字段字典"""
        logger.info("生成字段字典...")
        
        field_dict = []
        tables = self.get_all_tables()
        
        for table in tables:
            structure = self.analyze_table_structure(table)
            if structure and 'columns' in structure:
                table_comment = structure.get('table_comment', '')
                
                for col in structure['columns']:
                    field_dict.append({
                        '表名': table,
                        '表注释': table_comment,
                        '字段名': col['name'],
                        '字段类型': col.get('column_type', str(col.get('type', ''))),
                        '中文说明': col.get('comment', ''),
                        '是否为空': col.get('is_nullable', 'YES'),
                        '键类型': col.get('column_key', ''),
                        '默认值': col.get('default', '')
                    })
                    
        return pd.DataFrame(field_dict)
        
    def analyze_comments_coverage(self) -> Dict:
        """分析中文注释覆盖率"""
        logger.info("分析中文注释覆盖率...")
        
        tables = self.get_all_tables()
        coverage_stats = {
            'total_tables': len(tables),
            'tables_with_comment': 0,
            'total_fields': 0,
            'fields_with_comment': 0,
            'tables_coverage': {},
            'missing_comments': []
        }
        
        for table in tables:
            structure = self.analyze_table_structure(table)
            if structure:
                # 检查表注释
                if structure.get('table_comment'):
                    coverage_stats['tables_with_comment'] += 1
                    
                # 检查字段注释
                if 'columns' in structure:
                    table_fields = len(structure['columns'])
                    fields_with_comment = sum(1 for col in structure['columns'] 
                                            if col.get('comment'))
                    
                    coverage_stats['total_fields'] += table_fields
                    coverage_stats['fields_with_comment'] += fields_with_comment
                    
                    # 计算单表覆盖率
                    coverage_rate = (fields_with_comment / table_fields * 100) if table_fields > 0 else 0
                    coverage_stats['tables_coverage'][table] = {
                        'total_fields': table_fields,
                        'commented_fields': fields_with_comment,
                        'coverage_rate': round(coverage_rate, 2)
                    }
                    
                    # 记录缺少注释的重要字段
                    for col in structure['columns']:
                        if not col.get('comment') and self._is_important_field(col['name']):
                            coverage_stats['missing_comments'].append({
                                'table': table,
                                'field': col['name'],
                                'type': col.get('column_type', str(col.get('type', '')))
                            })
                            
        # 计算总体覆盖率
        coverage_stats['table_comment_coverage'] = round(
            coverage_stats['tables_with_comment'] / coverage_stats['total_tables'] * 100, 2
        ) if coverage_stats['total_tables'] > 0 else 0
        
        coverage_stats['field_comment_coverage'] = round(
            coverage_stats['fields_with_comment'] / coverage_stats['total_fields'] * 100, 2
        ) if coverage_stats['total_fields'] > 0 else 0
        
        return coverage_stats
        
    def _is_important_field(self, field_name: str) -> bool:
        """判断是否为重要字段（需要注释）"""
        # 排除明显的字段
        obvious_fields = ['id', 'create_time', 'update_time', 'ts_code', 'trade_date']
        if field_name.lower() in obvious_fields:
            return False
            
        # 重要的业务字段
        important_keywords = [
            'amount', 'price', 'rate', 'ratio', 'profit', 'revenue', 
            'cost', 'margin', 'pe', 'pb', 'roe', 'eps', 'indicator'
        ]
        
        return any(keyword in field_name.lower() for keyword in important_keywords)
        
    def generate_summary_report(self) -> Dict:
        """生成汇总报告"""
        logger.info("开始生成数据库分析报告...")
        
        # 获取所有表
        tables = self.get_all_tables()
        
        # 分析每个表
        table_analysis = {}
        for table in tables:
            logger.info(f"分析表: {table}")
            structure = self.analyze_table_structure(table)
            data = self.analyze_table_data(table)
            
            table_analysis[table] = {
                'structure': structure,
                'data': data
            }
            
        # 检查数据完整性
        completeness = self.check_data_completeness()
        
        # 分析注释覆盖率
        comment_coverage = self.analyze_comments_coverage()
        
        # 生成字段字典
        field_dictionary = self.generate_field_dictionary()
        
        # 生成摘要
        summary = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database': 'Tushare',
            'total_tables': len(tables),
            'tables': table_analysis,
            'completeness_check': completeness,
            'comment_coverage': comment_coverage,
            'field_dictionary_summary': {
                'total_fields': len(field_dictionary),
                'fields_with_comments': len(field_dictionary[field_dictionary['中文说明'] != ''])
            },
            'recommendations': self._generate_recommendations(table_analysis, completeness, comment_coverage)
        }
        
        # 保存字段字典
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 尝试保存为Excel
        try:
            import openpyxl
            field_dict_file = f'tushare_field_dictionary_{timestamp}.xlsx'
            field_dictionary.to_excel(field_dict_file, index=False, sheet_name='字段字典')
            logger.info(f"字段字典已保存: {field_dict_file}")
        except ImportError:
            # 如果没有openpyxl，保存为CSV
            field_dict_file = f'tushare_field_dictionary_{timestamp}.csv'
            field_dictionary.to_csv(field_dict_file, index=False, encoding='utf-8-sig')
            logger.info(f"字段字典已保存为CSV: {field_dict_file}")
        
        return summary
        
    def _generate_recommendations(self, table_analysis: Dict, completeness: Dict, comment_coverage: Dict = None) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 检查是否有缺失的核心表
        core_tables = [
            'tu_stock_basic', 'tu_daily_detail', 'tu_daily_basic',
            'tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator'
        ]
        
        existing_tables = list(table_analysis.keys())
        missing_tables = [t for t in core_tables if t not in existing_tables]
        
        if missing_tables:
            recommendations.append(f"缺失核心数据表: {', '.join(missing_tables)}")
            
        # 检查数据更新情况
        for table, info in table_analysis.items():
            if 'data' in info and 'date_ranges' in info['data']:
                for date_col, date_range in info['data']['date_ranges'].items():
                    if date_range and 'max' in date_range:
                        try:
                            max_date = pd.to_datetime(date_range['max'])
                            days_old = (datetime.now() - max_date).days
                            
                            if 'daily' in table and days_old > 1:
                                recommendations.append(f"{table} 的数据已经 {days_old} 天未更新")
                            elif 'financial' in table or 'income' in table or 'balance' in table:
                                if days_old > 90:
                                    recommendations.append(f"{table} 的财务数据可能需要更新 (最新: {date_range['max']})")
                        except:
                            continue
                            
        # 检查注释覆盖率
        if comment_coverage:
            if comment_coverage['field_comment_coverage'] < 50:
                recommendations.append(
                    f"字段注释覆盖率较低 ({comment_coverage['field_comment_coverage']}%)，"
                    f"建议完善重要字段的中文说明"
                )
                
            # 列出注释缺失最严重的表
            worst_tables = sorted(
                comment_coverage['tables_coverage'].items(),
                key=lambda x: x[1]['coverage_rate']
            )[:5]
            
            for table, stats in worst_tables:
                if stats['coverage_rate'] < 30:
                    recommendations.append(
                        f"{table} 表的字段注释覆盖率仅 {stats['coverage_rate']}%"
                    )
                    
        return recommendations
        
    def export_report(self, report: Dict, format: str = 'all'):
        """导出报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format in ['json', 'all']:
            # 导出JSON格式
            json_filename = f'tushare_db_analysis_{timestamp}.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"JSON报告已保存: {json_filename}")
            
        if format in ['markdown', 'all']:
            # 导出Markdown格式
            md_filename = f'tushare_db_analysis_{timestamp}.md'
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(self._generate_markdown_report(report))
            logger.info(f"Markdown报告已保存: {md_filename}")
            
        if format in ['excel', 'all']:
            # 检查是否安装了openpyxl
            try:
                import openpyxl
                # 导出Excel格式
                excel_filename = f'tushare_db_analysis_{timestamp}.xlsx'
                self._export_to_excel(report, excel_filename)
                logger.info(f"Excel报告已保存: {excel_filename}")
            except ImportError:
                logger.warning("未安装openpyxl模块，跳过Excel导出。可通过 'pip install openpyxl' 安装")
                
        if format in ['csv', 'all']:
            # 导出CSV格式（不需要openpyxl）
            csv_filename = f'tushare_db_analysis_{timestamp}_overview.csv'
            self._export_to_csv(report, csv_filename)
            logger.info(f"CSV报告已保存: {csv_filename}")
            
    def _export_to_csv(self, report: Dict, filename: str):
        """导出CSV格式报告（作为Excel的替代方案）"""
        # 导出表概览
        overview_data = []
        for table_name, info in report['tables'].items():
            table_comment = info['structure'].get('table_comment', '') if info['structure'] else ''
            overview_data.append({
                '表名': table_name,
                '表说明': table_comment,
                '记录数': info['data'].get('record_count', 0),
                '列数': info['structure']['column_count'] if info['structure'] else 0
            })
        
        overview_df = pd.DataFrame(overview_data)
        overview_df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        # 导出注释覆盖率
        if 'comment_coverage' in report:
            coverage_filename = filename.replace('_overview.csv', '_coverage.csv')
            coverage_data = []
            for table, stats in report['comment_coverage']['tables_coverage'].items():
                coverage_data.append({
                    '表名': table,
                    '总字段数': stats['total_fields'],
                    '已注释字段': stats['commented_fields'],
                    '覆盖率(%)': stats['coverage_rate']
                })
            
            coverage_df = pd.DataFrame(coverage_data)
            coverage_df.to_csv(coverage_filename, index=False, encoding='utf-8-sig')
            
    def _generate_markdown_report(self, report: Dict) -> str:
        """生成Markdown格式报告"""
        md_lines = []
        
        # 标题
        md_lines.append("# Tushare数据库分析报告")
        md_lines.append(f"\n生成时间: {report['analysis_time']}")
        md_lines.append(f"\n数据库: {report['database']}")
        md_lines.append(f"\n总表数: {report['total_tables']}")
        
        # 表概览
        md_lines.append("\n## 数据表概览")
        md_lines.append("\n| 表名 | 表说明 | 记录数 | 列数 | 数据范围 |")
        md_lines.append("|------|--------|--------|------|----------|")
        
        for table_name, info in report['tables'].items():
            table_comment = info['structure'].get('table_comment', '') if info['structure'] else ''
            record_count = info['data'].get('record_count', 0)
            column_count = info['structure']['column_count'] if info['structure'] else 0
            
            # 获取日期范围
            date_range = "N/A"
            if 'date_ranges' in info['data']:
                ranges = info['data']['date_ranges']
                if ranges:
                    first_range = list(ranges.values())[0]
                    if 'min' in first_range and 'max' in first_range:
                        date_range = f"{first_range['min']} ~ {first_range['max']}"
                        
            md_lines.append(f"| {table_name} | {table_comment} | {record_count:,} | {column_count} | {date_range} |")
            
        # 注释覆盖率统计
        if 'comment_coverage' in report:
            coverage = report['comment_coverage']
            md_lines.append("\n## 中文注释覆盖率")
            md_lines.append(f"- 表注释覆盖率: {coverage['table_comment_coverage']}%")
            md_lines.append(f"- 字段注释覆盖率: {coverage['field_comment_coverage']}%")
            md_lines.append(f"- 总字段数: {coverage['total_fields']}")
            md_lines.append(f"- 已注释字段数: {coverage['fields_with_comment']}")
            
            # 注释覆盖率最低的表
            md_lines.append("\n### 注释覆盖率最低的表")
            worst_tables = sorted(
                coverage['tables_coverage'].items(),
                key=lambda x: x[1]['coverage_rate']
            )[:10]
            
            if worst_tables:
                md_lines.append("\n| 表名 | 总字段数 | 已注释 | 覆盖率 |")
                md_lines.append("|------|----------|--------|--------|")
                for table, stats in worst_tables:
                    md_lines.append(
                        f"| {table} | {stats['total_fields']} | "
                        f"{stats['commented_fields']} | {stats['coverage_rate']}% |"
                    )
                    
        # 数据完整性检查
        md_lines.append("\n## 数据完整性检查")
        
        if 'daily_data' in report['completeness_check']:
            daily = report['completeness_check']['daily_data']
            md_lines.append(f"\n### 日线数据")
            md_lines.append(f"- 平均每日股票数: {daily.get('avg_daily_stocks', 0):,}")
            md_lines.append(f"- 平均每日基础数据: {daily.get('avg_basic_stocks', 0):,}")
            
        # 重要表的详细信息
        md_lines.append("\n## 重要表详细信息")
        
        important_tables = ['tu_stock_basic', 'tu_daily_basic', 'tu_income', 'tu_fina_indicator']
        for table_name in important_tables:
            if table_name in report['tables']:
                info = report['tables'][table_name]
                if info['structure']:
                    md_lines.append(f"\n### {table_name}")
                    if info['structure'].get('table_comment'):
                        md_lines.append(f"**表说明**: {info['structure']['table_comment']}")
                    
                    # 显示前10个字段
                    md_lines.append("\n**主要字段**:")
                    md_lines.append("\n| 字段名 | 类型 | 说明 |")
                    md_lines.append("|--------|------|------|")
                    
                    for col in info['structure']['columns'][:10]:
                        field_name = col['name']
                        field_type = col.get('column_type', str(col.get('type', '')))
                        comment = col.get('comment', '')
                        md_lines.append(f"| {field_name} | {field_type} | {comment} |")
                        
                    if len(info['structure']['columns']) > 10:
                        md_lines.append(f"\n*... 还有 {len(info['structure']['columns']) - 10} 个字段*")
                        
        # 建议
        md_lines.append("\n## 改进建议")
        for i, rec in enumerate(report.get('recommendations', []), 1):
            md_lines.append(f"{i}. {rec}")
            
        return "\n".join(md_lines)
        
    def _export_to_excel(self, report: Dict, filename: str):
        """导出Excel格式报告"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 概览sheet
            overview_data = []
            for table_name, info in report['tables'].items():
                overview_data.append({
                    '表名': table_name,
                    '记录数': info['data'].get('record_count', 0),
                    '列数': info['structure']['column_count'] if info['structure'] else 0
                })
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='表概览', index=False)
            
            # 数据完整性sheet
            if 'completeness_check' in report and 'daily_data' in report['completeness_check']:
                if 'recent_30days' in report['completeness_check']['daily_data']:
                    daily_df = pd.DataFrame(report['completeness_check']['daily_data']['recent_30days'])
                    daily_df.to_excel(writer, sheet_name='日线数据完整性', index=False)


def main():
    """主函数"""
    # 创建分析器
    analyzer = TushareDBAnalyzer()
    
    # 生成报告
    report = analyzer.generate_summary_report()
    
    # 导出报告
    analyzer.export_report(report, format='all')
    
    # 打印摘要
    print("\n" + "="*60)
    print("Tushare数据库分析完成")
    print("="*60)
    print(f"分析时间: {report['analysis_time']}")
    print(f"数据表总数: {report['total_tables']}")
    
    # 打印主要表的统计
    print("\n主要数据表统计:")
    for table_name in ['tu_stock_basic', 'tu_daily_detail', 'tu_daily_basic', 
                       'tu_income', 'tu_balancesheet', 'tu_cashflow']:
        if table_name in report['tables']:
            info = report['tables'][table_name]
            table_comment = info['structure'].get('table_comment', '') if info['structure'] else ''
            record_count = info['data'].get('record_count', 0)
            print(f"- {table_name}: {record_count:,} 条记录")
            if table_comment:
                print(f"  说明: {table_comment}")
                
    # 打印注释覆盖率
    if 'comment_coverage' in report:
        coverage = report['comment_coverage']
        print(f"\n中文注释覆盖率:")
        print(f"- 表注释: {coverage['table_comment_coverage']}%")
        print(f"- 字段注释: {coverage['field_comment_coverage']}%")
        print(f"- 总字段数: {coverage['total_fields']}")
        print(f"- 已注释字段: {coverage['fields_with_comment']}")
            
    # 打印建议
    if report.get('recommendations'):
        print("\n改进建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")
            
    print("\n生成的文件:")
    print("1. 详细分析报告 (JSON/Markdown/Excel)")
    print("2. 字段字典 (Excel) - 包含所有表的字段中文说明")
    print("\n请查看生成的文件获取完整信息")
    

if __name__ == "__main__":
    main()
