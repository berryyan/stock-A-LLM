#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Analysis Agent - 深度财务分析代理
基于四表联合查询的专业财务分析系统
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import time
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from database.mysql_connector import MySQLConnector
from config.settings import settings
from utils.logger import setup_logger
from utils.stock_code_mapper import convert_to_ts_code


@dataclass
class FinancialData:
    """财务数据结构"""
    ts_code: str
    end_date: str
    report_type: str
    
    # 利润表数据
    total_revenue: float
    n_income_attr_p: float  # 净利润(不含少数股东)
    operate_profit: float
    
    # 资产负债表数据
    total_assets: float
    total_liab: float
    total_hldr_eqy_inc_min_int: float  # 股东权益合计
    
    # 现金流量表数据
    n_cashflow_act: float  # 经营活动现金流
    n_cashflow_inv_act: float  # 投资活动现金流
    n_cash_flows_fnc_act: float  # 筹资活动现金流
    
    # 财务指标数据
    roe: float
    roa: float
    debt_to_assets: float
    current_ratio: float


class FinancialAnalysisAgent:
    """财务分析代理 - 专业财务分析和诊断"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        self.logger = setup_logger("financial_agent")
        
        # 初始化数据库连接
        self.mysql = MySQLConnector()
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=0.3,  # 财务分析需要更准确的结果
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 创建财务分析提示词模板
        self.analysis_chain = self._create_analysis_chain()
        
        # 财务查询模式匹配
        self.query_patterns = {
            'financial_health': ['财务健康', '财务状况', '经营状况', '财务评级', '健康度'],
            'profitability': ['盈利能力', '赚钱能力', 'ROE', 'ROA', '净利率', '毛利率'],
            'solvency': ['偿债能力', '负债率', '流动比率', '资产负债率', '偿债'],
            'growth': ['成长性', '增长率', '营收增长', '利润增长', '发展速度'],
            'cash_flow': ['现金流', '现金流量', '经营现金流', '现金质量'],
            'dupont': ['杜邦分析', 'ROE分解', '杜邦', '盈利能力分解'],
            'comparison': ['对比', '比较', '同行', '行业对比', '历史对比']
        }
        
        self.logger.info("Financial Analysis Agent初始化完成")
    
    def _create_analysis_chain(self):
        """创建财务分析链"""
        analysis_prompt = PromptTemplate(
            input_variables=["stock_info", "analysis_type", "financial_data", "metrics", "insights"],
            template="""你是一位资深的财务分析师，请基于提供的财务数据进行专业分析。

股票信息：{stock_info}
分析类型：{analysis_type}

财务数据：
{financial_data}

计算指标：
{metrics}

关键发现：
{insights}

请提供：
1. **核心结论** (3-5个要点)
2. **详细分析** (各项指标的含义和表现)
3. **风险提示** (需要关注的问题)
4. **投资建议** (基于分析结果的建议)

注意：
- 在分析开头标明股票名称和代码，方便阅读和分享
- 分析要客观专业，避免过度乐观或悲观
- 重要数据和结论用**加粗**标注
- 涉及风险的地方要明确提示
- 建议要具体可行

财务分析报告："""
        )
        
        return analysis_prompt | self.llm | StrOutputParser()
    
    def query(self, question: str, ts_code: str = None) -> Dict[str, Any]:
        """
        主查询接口 - 路由财务分析请求
        
        Args:
            question: 用户问题
            ts_code: 股票代码（可选，可从问题中提取）
            
        Returns:
            分析结果
        """
        start_time = time.time()
        
        try:
            # 输入验证
            if not question or not question.strip():
                return {
                    'success': False,
                    'error': '查询内容不能为空',
                    'type': 'financial_query'
                }
            
            self.logger.info(f"财务分析查询: {question}")
            
            # 解析查询意图和股票代码
            intent, extracted_ts_code = self._parse_query_intent(question)
            final_ts_code = ts_code or extracted_ts_code
            
            # 处理特殊错误码
            if final_ts_code == 'INVALID_FORMAT':
                return {
                    'success': False,
                    'error': '证券代码格式不正确，后缀应为.SZ/.SH/.BJ',
                    'type': 'financial_query'
                }
            elif final_ts_code == 'INVALID_LENGTH':
                return {
                    'success': False,
                    'error': '股票代码格式不正确，请输入6位数字',
                    'type': 'financial_query'
                }
            elif not final_ts_code:
                self.logger.warning(f"无法从查询中提取股票代码: {question}")
                return {
                    'success': False,
                    'error': '无法识别输入内容。请输入：1) 6位股票代码（如002047）2) 证券代码（如600519.SH）3) 股票名称（如贵州茅台）',
                    'type': 'financial_query'
                }
            
            # 根据意图路由到相应的分析功能
            if intent == 'financial_health':
                result = self.analyze_financial_health(final_ts_code)
            elif intent == 'dupont':
                result = self.dupont_analysis(final_ts_code)
            elif intent == 'cash_flow':
                result = self.cash_flow_quality_analysis(final_ts_code)
            elif intent == 'comparison':
                result = self.multi_period_comparison(final_ts_code)
            else:
                # 默认进行综合财务分析
                result = self.comprehensive_analysis(final_ts_code)
            
            result['processing_time'] = time.time() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"财务分析查询失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'financial_query',
                'processing_time': time.time() - start_time
            }
    
    def _parse_query_intent(self, question: str) -> Tuple[str, Optional[str]]:
        """解析查询意图和股票代码"""
        import re
        
        # 1. 首先尝试提取完整的ts_code格式 (如 600519.SH)
        ts_code_pattern = r'(\d{6}\.(SZ|SH|BJ))'
        ts_code_match = re.search(ts_code_pattern, question)
        if ts_code_match:
            extracted_ts_code = ts_code_match.group(0)  # 直接使用完整匹配
            self.logger.info(f"从查询中提取到ts_code: {extracted_ts_code}")
            # 验证ts_code格式
            if not self._validate_ts_code(extracted_ts_code):
                self.logger.warning(f"证券代码格式不正确: {extracted_ts_code}")
                # 先确定intent再返回
                intent = 'comprehensive'
                for pattern_type, patterns in self.query_patterns.items():
                    if any(pattern in question for pattern in patterns):
                        intent = pattern_type
                        break
                return intent, 'INVALID_FORMAT'
        else:
            extracted_ts_code = None
        
        # 2. 如果没有找到完整格式，尝试提取纯数字股票代码
        if not extracted_ts_code:
            # 更严格的数字提取，避免提取到其他数字
            number_pattern = r'(?:^|[\s\u4e00-\u9fa5])(\d+)(?:[\s\u4e00-\u9fa5]|$)'
            numbers = re.findall(number_pattern, question)
            for number in numbers:
                if len(number) == 6:  # 只接受6位数字
                    # 使用股票代码映射器转换
                    extracted_ts_code = convert_to_ts_code(number)
                    if extracted_ts_code:
                        self.logger.info(f"从查询中提取到股票代码 {number}，转换为: {extracted_ts_code}")
                        break
                elif len(number) != 6 and len(number) >= 3:  # 可能是错误的股票代码
                    self.logger.warning(f"股票代码长度不正确: {number} (应为6位)")
                    # 先确定intent再返回
                    intent = 'comprehensive'
                    for pattern_type, patterns in self.query_patterns.items():
                        if any(pattern in question for pattern in patterns):
                            intent = pattern_type
                            break
                    return intent, 'INVALID_LENGTH'
        
        # 3. 如果还没有找到，尝试通过股票名称查找
        if not extracted_ts_code:
            # 使用更智能的名称提取逻辑
            extracted_ts_code = self._extract_stock_by_name(question)
            
        # 4. 验证提取到的ts_code格式
        if extracted_ts_code and not self._validate_ts_code(extracted_ts_code):
            self.logger.warning(f"证券代码格式不正确: {extracted_ts_code}")
            # 先确定intent再返回
            intent = 'comprehensive'
            for pattern_type, patterns in self.query_patterns.items():
                if any(pattern in question for pattern in patterns):
                    intent = pattern_type
                    break
            return intent, 'INVALID_FORMAT'
        
        # 匹配查询意图
        intent = 'comprehensive'  # 默认意图
        for pattern_type, patterns in self.query_patterns.items():
            if any(pattern in question for pattern in patterns):
                intent = pattern_type
                break
        
        return intent, extracted_ts_code
    
    def _validate_ts_code(self, ts_code: str) -> bool:
        """验证证券代码格式是否正确"""
        import re
        # 验证格式：6位数字.SZ/SH/BJ
        pattern = r'^\d{6}\.(SZ|SH|BJ)$'
        return bool(re.match(pattern, ts_code))
    
    def _get_stock_name(self, ts_code: str) -> str:
        """根据ts_code获取股票名称"""
        try:
            # 使用stock_code_mapper的缓存机制
            from utils.stock_code_mapper import get_stock_mapper
            mapper = get_stock_mapper()
            return mapper.get_stock_name(ts_code)
            
        except Exception as e:
            self.logger.warning(f"获取股票名称失败: {e}")
            return ts_code
    
    def _extract_stock_by_name(self, question: str) -> Optional[str]:
        """通过股票名称查找TS代码"""
        try:
            # 常见的股票名称模式
            # 1. 先尝试提取可能的公司名称（2-6个中文字符）
            import re
            name_patterns = [
                r'([一-龥]{2,6}(?:股份|集团|银行|科技|电子|医药|能源|地产|证券|保险|汽车|新材料|新能源))',
                r'([一-龥]{2,6}[A-Z]?(?=的|财务|分析|怎么样|如何))',  # 如 "万科A的财务"
                r'分析([一-龥]{2,6})的',  # 如 "分析茅台的"
                r'([一-龥]{2,4})(?:股价|财务|业绩|年报|公告)'  # 如 "茅台股价"
            ]
            
            potential_names = []
            for pattern in name_patterns:
                matches = re.findall(pattern, question)
                potential_names.extend(matches)
            
            # 去重并尝试转换
            seen = set()
            for name in potential_names:
                if name not in seen:
                    seen.add(name)
                    ts_code = convert_to_ts_code(name)
                    if ts_code:
                        self.logger.info(f"从查询中提取到股票名称 '{name}'，转换为: {ts_code}")
                        return ts_code
            
            # 如果没有找到，尝试整个问题作为输入
            # 去除一些常见的查询词
            clean_question = question
            for word in ['分析', '查询', '的', '财务', '健康度', '状况', '怎么样', '如何']:
                clean_question = clean_question.replace(word, ' ')
            
            # 提取剩余的主要词汇
            words = [w.strip() for w in clean_question.split() if len(w.strip()) >= 2]
            for word in words:
                # 跳过纯数字，因为已经在前面处理过了
                if word.isdigit():
                    continue
                ts_code = convert_to_ts_code(word)
                if ts_code:
                    self.logger.info(f"从查询词 '{word}' 转换为: {ts_code}")
                    return ts_code
            
            # 如果尝试了但没找到，记录尝试的名称
            if words:
                self.logger.warning(f"未找到股票名称匹配: {', '.join(words)}")
            
            return None
        except Exception as e:
            self.logger.warning(f"股票名称提取失败: {e}")
            return None
    
    def get_financial_data(self, ts_code: str, periods: int = 4) -> List[FinancialData]:
        """获取财务数据 - 四表联合查询"""
        try:
            query = """
            SELECT 
                i.ts_code, i.end_date, i.report_type,
                -- 利润表关键字段
                COALESCE(i.total_revenue, 0) as total_revenue,
                COALESCE(i.n_income_attr_p, 0) as n_income_attr_p,
                COALESCE(i.operate_profit, 0) as operate_profit,
                -- 资产负债表关键字段  
                COALESCE(b.total_assets, 0) as total_assets,
                COALESCE(b.total_liab, 0) as total_liab,
                COALESCE(b.total_hldr_eqy_inc_min_int, 0) as total_hldr_eqy_inc_min_int,
                -- 现金流量表关键字段
                COALESCE(c.n_cashflow_act, 0) as n_cashflow_act,
                COALESCE(c.n_cashflow_inv_act, 0) as n_cashflow_inv_act,
                COALESCE(c.n_cash_flows_fnc_act, 0) as n_cash_flows_fnc_act,
                -- 财务指标关键字段
                COALESCE(f.roe, 0) as roe,
                COALESCE(f.roa, 0) as roa,
                COALESCE(f.debt_to_assets, 0) as debt_to_assets,
                COALESCE(f.current_ratio, 0) as current_ratio
            FROM tu_income i
            LEFT JOIN tu_balancesheet b ON i.ts_code = b.ts_code AND i.end_date = b.end_date
            LEFT JOIN tu_cashflow c ON i.ts_code = c.ts_code AND i.end_date = c.end_date  
            LEFT JOIN tu_fina_indicator f ON i.ts_code = f.ts_code AND i.end_date = f.end_date
            WHERE i.ts_code = :ts_code AND i.report_type = '1'
            ORDER BY i.end_date DESC
            LIMIT :periods
            """
            
            results = self.mysql.execute_query(query, {'ts_code': ts_code, 'periods': periods})
            
            financial_data = []
            for row in results:
                data = FinancialData(
                    ts_code=row['ts_code'],
                    end_date=row['end_date'],
                    report_type=row['report_type'],
                    total_revenue=float(row['total_revenue'] or 0),
                    n_income_attr_p=float(row['n_income_attr_p'] or 0),
                    operate_profit=float(row['operate_profit'] or 0),
                    total_assets=float(row['total_assets'] or 0),
                    total_liab=float(row['total_liab'] or 0),
                    total_hldr_eqy_inc_min_int=float(row['total_hldr_eqy_inc_min_int'] or 0),
                    n_cashflow_act=float(row['n_cashflow_act'] or 0),
                    n_cashflow_inv_act=float(row['n_cashflow_inv_act'] or 0),
                    n_cash_flows_fnc_act=float(row['n_cash_flows_fnc_act'] or 0),
                    roe=float(row['roe'] or 0),
                    roa=float(row['roa'] or 0),
                    debt_to_assets=float(row['debt_to_assets'] or 0),
                    current_ratio=float(row['current_ratio'] or 0)
                )
                financial_data.append(data)
            
            return financial_data
            
        except Exception as e:
            self.logger.error(f"获取财务数据失败: {e}")
            return []
    
    def analyze_financial_health(self, ts_code: str) -> Dict[str, Any]:
        """财务健康度分析"""
        try:
            self.logger.info(f"开始分析 {ts_code} 的财务健康度")
            
            # 获取财务数据
            self.logger.info(f"正在获取 {ts_code} 的财务数据...")
            financial_data = self.get_financial_data(ts_code, periods=4)
            
            if not financial_data:
                self.logger.warning(f"未找到股票 {ts_code} 的财务数据")
                return {
                    'success': False,
                    'error': f'未找到股票 {ts_code} 的财务数据。请确认股票代码是否正确。'
                }
            
            self.logger.info(f"成功获取 {len(financial_data)} 期财务数据")
            latest_data = financial_data[0]
            
            # 增加额外的数据完整性检查
            if latest_data is None:
                return {
                    'success': False,
                    'error': f'股票 {ts_code} 的财务数据无效'
                }
            
            # 计算财务健康度评分
            self.logger.info(f"正在计算财务健康度评分...")
            health_score = self._calculate_health_score(latest_data)
            self.logger.info(f"财务健康度评分: {health_score['total_score']} ({health_score['rating']})")
            
            # 生成分析报告
            analysis_data = {
                'ts_code': ts_code,
                'period': latest_data.end_date,
                'health_score': health_score,
                'financial_metrics': self._format_financial_metrics(latest_data)
            }
            
            # 使用LLM生成详细分析
            self.logger.info(f"正在生成LLM分析报告...")
            stock_name = self._get_stock_name(ts_code)
            analysis_report = self.analysis_chain.invoke({
                'stock_info': f"{stock_name} ({ts_code})",
                'analysis_type': '财务健康度分析',
                'financial_data': self._format_financial_data_for_llm(latest_data),
                'metrics': self._format_health_metrics(health_score),
                'insights': self._generate_health_insights(health_score, latest_data)
            })
            
            self.logger.info(f"财务健康度分析完成: {ts_code}")
            
            return {
                'success': True,
                'ts_code': ts_code,
                'analysis_type': 'financial_health',
                'period': latest_data.end_date,
                'health_score': health_score,
                'financial_data': analysis_data,
                'analysis_report': analysis_report,
                'type': 'financial_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"财务健康度分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'financial_analysis'
            }
    
    def _calculate_health_score(self, data: FinancialData) -> Dict[str, Any]:
        """计算财务健康度评分"""
        
        # 盈利能力评分 (30%)
        profitability_score = self._score_profitability(data)
        
        # 偿债能力评分 (25%)
        solvency_score = self._score_solvency(data)
        
        # 运营能力评分 (25%)
        operation_score = self._score_operation(data)
        
        # 成长能力评分 (20%)
        growth_score = self._score_growth(data)
        
        # 加权总分
        total_score = (
            profitability_score * 0.3 +
            solvency_score * 0.25 + 
            operation_score * 0.25 +
            growth_score * 0.2
        )
        
        return {
            'total_score': round(total_score, 2),
            'rating': self._get_rating(total_score),
            'dimension_scores': {
                'profitability': round(profitability_score, 2),
                'solvency': round(solvency_score, 2),
                'operation': round(operation_score, 2),
                'growth': round(growth_score, 2)
            }
        }
    
    def _score_profitability(self, data: FinancialData) -> float:
        """盈利能力评分"""
        score = 0
        
        # ROE评分 (40%)
        if data.roe >= 20:
            score += 40
        elif data.roe >= 15:
            score += 35
        elif data.roe >= 10:
            score += 25
        elif data.roe >= 5:
            score += 15
        else:
            score += 5
        
        # 净利率评分 (35%)
        if data.total_revenue > 0:
            net_margin = (data.n_income_attr_p / data.total_revenue) * 100
            if net_margin >= 20:
                score += 35
            elif net_margin >= 15:
                score += 30
            elif net_margin >= 10:
                score += 20
            elif net_margin >= 5:
                score += 10
            else:
                score += 0
        
        # 营业利润率评分 (25%)
        if data.total_revenue > 0:
            operating_margin = (data.operate_profit / data.total_revenue) * 100
            if operating_margin >= 25:
                score += 25
            elif operating_margin >= 15:
                score += 20
            elif operating_margin >= 10:
                score += 15
            elif operating_margin >= 5:
                score += 10
            else:
                score += 0
        
        return min(score, 100)
    
    def _score_solvency(self, data: FinancialData) -> float:
        """偿债能力评分"""
        score = 0
        
        # 资产负债率评分 (50%)
        debt_ratio = data.debt_to_assets
        if debt_ratio <= 30:
            score += 50
        elif debt_ratio <= 50:
            score += 40
        elif debt_ratio <= 60:
            score += 30
        elif debt_ratio <= 70:
            score += 20
        else:
            score += 10
        
        # 流动比率评分 (50%)
        current_ratio = data.current_ratio
        if current_ratio >= 2.0:
            score += 50
        elif current_ratio >= 1.5:
            score += 40
        elif current_ratio >= 1.2:
            score += 30
        elif current_ratio >= 1.0:
            score += 20
        else:
            score += 10
        
        return min(score, 100)
    
    def _score_operation(self, data: FinancialData) -> float:
        """运营能力评分 - 基于现有数据的简化评分"""
        score = 50  # 基础分
        
        # 基于总资产规模和营收的相关性
        if data.total_assets > 0 and data.total_revenue > 0:
            asset_turnover = data.total_revenue / data.total_assets
            if asset_turnover >= 1.0:
                score += 30
            elif asset_turnover >= 0.5:
                score += 20
            elif asset_turnover >= 0.3:
                score += 10
        
        # 基于现金流运营效率
        if data.n_cashflow_act > 0 and data.n_income_attr_p > 0:
            cash_conversion = data.n_cashflow_act / data.n_income_attr_p
            if cash_conversion >= 1.2:
                score += 20
            elif cash_conversion >= 1.0:
                score += 15
            elif cash_conversion >= 0.8:
                score += 10
        
        return min(score, 100)
    
    def _score_growth(self, data: FinancialData) -> float:
        """成长能力评分 - 基于单期数据的评估"""
        score = 50  # 基础分
        
        # 基于ROE水平判断成长潜力
        if data.roe >= 15:
            score += 25
        elif data.roe >= 10:
            score += 15
        elif data.roe >= 5:
            score += 10
        
        # 基于现金流状况
        if data.n_cashflow_act > 0:
            score += 25
        elif data.n_cashflow_act > data.n_income_attr_p * 0.5:
            score += 15
        
        return min(score, 100)
    
    def _get_rating(self, score: float) -> str:
        """根据评分获取评级"""
        if score >= 90:
            return 'AAA'
        elif score >= 80:
            return 'AA'
        elif score >= 70:
            return 'A'
        elif score >= 60:
            return 'BBB'
        elif score >= 50:
            return 'BB'
        elif score >= 40:
            return 'B'
        else:
            return 'CCC'
    
    def _format_financial_data_for_llm(self, data: FinancialData) -> str:
        """格式化财务数据用于LLM分析，增加None值检查"""
        # 安全地格式化数值，处理None值
        def safe_format_billions(value, default="N/A"):
            if value is None:
                return default
            try:
                return f"{value/100000000:.2f}亿元"
            except (TypeError, ZeroDivisionError):
                return default
        
        def safe_format_percent(value, default="N/A"):
            if value is None:
                return default
            try:
                return f"{value:.2f}%"
            except (TypeError, ValueError):
                return default
        
        def safe_format_ratio(value, default="N/A"):
            if value is None:
                return default
            try:
                return f"{value:.2f}"
            except (TypeError, ValueError):
                return default
        
        return f"""
        报告期: {data.end_date if data.end_date else "N/A"}
        营业总收入: {safe_format_billions(data.total_revenue)}
        净利润: {safe_format_billions(data.n_income_attr_p)}
        总资产: {safe_format_billions(data.total_assets)}
        总负债: {safe_format_billions(data.total_liab)}
        股东权益: {safe_format_billions(data.total_hldr_eqy_inc_min_int)}
        经营现金流: {safe_format_billions(data.n_cashflow_act)}
        ROE: {safe_format_percent(data.roe)}
        资产负债率: {safe_format_percent(data.debt_to_assets)}
        流动比率: {safe_format_ratio(data.current_ratio)}
        """
    
    def _format_health_metrics(self, health_score: Dict) -> str:
        """格式化健康度指标"""
        return f"""
        总体评分: {health_score['total_score']}/100
        财务评级: {health_score['rating']}
        
        分维度评分:
        - 盈利能力: {health_score['dimension_scores']['profitability']}/100
        - 偿债能力: {health_score['dimension_scores']['solvency']}/100  
        - 运营能力: {health_score['dimension_scores']['operation']}/100
        - 成长能力: {health_score['dimension_scores']['growth']}/100
        """
    
    def _generate_health_insights(self, health_score: Dict, data: FinancialData) -> str:
        """生成健康度关键洞察"""
        insights = []
        
        # 总体评级洞察
        rating = health_score['rating']
        if rating in ['AAA', 'AA']:
            insights.append("财务状况优秀，各项指标表现良好")
        elif rating in ['A', 'BBB']:
            insights.append("财务状况良好，但部分指标有改进空间")
        else:
            insights.append("财务状况需要关注，存在一定风险")
        
        # 具体指标洞察
        scores = health_score['dimension_scores']
        if scores['profitability'] < 60:
            insights.append("盈利能力相对较弱，需关注ROE和净利率")
        if scores['solvency'] < 60:
            insights.append("偿债能力有压力，需关注负债水平")
        if data.n_cashflow_act < data.n_income_attr_p * 0.8:
            insights.append("经营现金流与净利润匹配度不高，需关注现金流质量")
        
        return "; ".join(insights)
    
    def _calculate_dupont_metrics(self, data: FinancialData) -> Dict[str, Any]:
        """计算杜邦分析指标"""
        try:
            # 避免除零错误
            if data.total_revenue == 0 or data.total_assets == 0 or data.total_hldr_eqy_inc_min_int == 0:
                return {
                    'net_profit_margin': 0,
                    'asset_turnover': 0,
                    'equity_multiplier': 0,
                    'calculated_roe': 0,
                    'reported_roe': data.roe,
                    'variance': abs(data.roe),
                    'valid': False
                }
            
            # 杜邦分析三要素
            net_profit_margin = (data.n_income_attr_p / data.total_revenue) * 100  # 净利率(%)
            asset_turnover = data.total_revenue / data.total_assets  # 总资产周转率
            equity_multiplier = data.total_assets / data.total_hldr_eqy_inc_min_int  # 权益乘数
            
            # 计算ROE = 净利率 × 总资产周转率 × 权益乘数
            calculated_roe = (net_profit_margin / 100) * asset_turnover * equity_multiplier * 100
            reported_roe = data.roe
            variance = abs(calculated_roe - reported_roe)
            
            return {
                'net_profit_margin': round(net_profit_margin, 2),
                'asset_turnover': round(asset_turnover, 3),
                'equity_multiplier': round(equity_multiplier, 2),
                'calculated_roe': round(calculated_roe, 2),
                'reported_roe': round(reported_roe, 2),
                'variance': round(variance, 2),
                'valid': True
            }
            
        except Exception as e:
            self.logger.warning(f"杜邦分析计算错误: {e}")
            return {
                'net_profit_margin': 0,
                'asset_turnover': 0,
                'equity_multiplier': 0,
                'calculated_roe': 0,
                'reported_roe': data.roe,
                'variance': abs(data.roe),
                'valid': False
            }
    
    def _format_dupont_metrics(self, dupont_metrics: Dict) -> str:
        """格式化杜邦分析指标"""
        if not dupont_metrics['valid']:
            return "数据不完整，无法进行杜邦分析"
        
        return f"""
        杜邦分析指标:
        - 净利率: {dupont_metrics['net_profit_margin']:.2f}%
        - 总资产周转率: {dupont_metrics['asset_turnover']:.3f}次
        - 权益乘数: {dupont_metrics['equity_multiplier']:.2f}倍
        
        ROE分解:
        - 计算ROE: {dupont_metrics['calculated_roe']:.2f}%
        - 报告ROE: {dupont_metrics['reported_roe']:.2f}%
        - 差异: {dupont_metrics['variance']:.2f}%
        """
    
    def _generate_dupont_insights(self, dupont_metrics: Dict, trend_analysis: List[Dict]) -> str:
        """生成杜邦分析洞察"""
        if not dupont_metrics['valid']:
            return "数据不完整，无法生成有效洞察"
        
        insights = []
        
        # ROE驱动因素分析
        npm = dupont_metrics['net_profit_margin']
        ato = dupont_metrics['asset_turnover']
        em = dupont_metrics['equity_multiplier']
        
        # 净利率水平判断
        if npm >= 15:
            insights.append("净利率优秀，盈利效率很高")
        elif npm >= 10:
            insights.append("净利率良好，盈利效率较高")
        elif npm >= 5:
            insights.append("净利率一般，盈利效率有待提升")
        else:
            insights.append("净利率偏低，需关注成本控制")
        
        # 资产周转率分析
        if ato >= 1.0:
            insights.append("资产周转效率高，运营能力强")
        elif ato >= 0.5:
            insights.append("资产周转效率中等")
        else:
            insights.append("资产周转效率偏低，需提升资产利用率")
        
        # 权益乘数分析
        if em >= 3.0:
            insights.append("财务杠杆较高，需关注偿债风险")
        elif em >= 2.0:
            insights.append("财务杠杆适中")
        else:
            insights.append("财务杠杆保守，安全性较高")
        
        # 趋势分析
        if len(trend_analysis) >= 2:
            latest_roe = trend_analysis[0]['calculated_roe']
            previous_roe = trend_analysis[1]['calculated_roe']
            if latest_roe > previous_roe:
                insights.append("ROE呈上升趋势，财务表现改善")
            elif latest_roe < previous_roe:
                insights.append("ROE呈下降趋势，需关注业绩变化")
        
        return "; ".join(insights)
    
    def _analyze_cash_flow_quality(self, financial_data: List[FinancialData]) -> Dict[str, Any]:
        """分析现金流质量"""
        try:
            quality_metrics = []
            
            for data in financial_data:
                # 计算现金流质量指标
                operating_cf = data.n_cashflow_act
                net_income = data.n_income_attr_p
                
                # 现金含量比率 (经营现金流 / 净利润)
                cash_content_ratio = operating_cf / net_income if net_income != 0 else 0
                
                # 现金流稳定性指标
                investing_cf = data.n_cashflow_inv_act
                financing_cf = data.n_cash_flows_fnc_act
                total_cf = operating_cf + investing_cf + financing_cf
                
                quality_metrics.append({
                    'period': data.end_date,
                    'operating_cf_billion': round(operating_cf / 100000000, 2),
                    'net_income_billion': round(net_income / 100000000, 2),
                    'investing_cf_billion': round(investing_cf / 100000000, 2),
                    'financing_cf_billion': round(financing_cf / 100000000, 2),
                    'cash_content_ratio': round(cash_content_ratio, 2),
                    'quality_rating': self._rate_cash_quality(cash_content_ratio)
                })
            
            # 计算平均指标
            avg_cash_content = np.mean([m['cash_content_ratio'] for m in quality_metrics if m['cash_content_ratio'] != 0])
            stability_score = self._calculate_cash_flow_stability(quality_metrics)
            
            return {
                'periods': quality_metrics,
                'average_cash_content': round(avg_cash_content, 2),
                'stability_score': stability_score,
                'overall_rating': self._get_overall_cash_quality_rating(avg_cash_content, stability_score),
                'trend': self._analyze_cash_flow_trend(quality_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"现金流质量分析计算错误: {e}")
            return {
                'periods': [],
                'average_cash_content': 0,
                'stability_score': 0,
                'overall_rating': 'F',
                'trend': '无法分析'
            }
    
    def _rate_cash_quality(self, cash_content_ratio: float) -> str:
        """评价现金流质量等级"""
        if cash_content_ratio >= 1.2:
            return 'A'  # 优秀
        elif cash_content_ratio >= 1.0:
            return 'B'  # 良好
        elif cash_content_ratio >= 0.8:
            return 'C'  # 一般
        elif cash_content_ratio >= 0.5:
            return 'D'  # 较差
        else:
            return 'F'  # 很差
    
    def _calculate_cash_flow_stability(self, quality_metrics: List[Dict]) -> float:
        """计算现金流稳定性评分"""
        if len(quality_metrics) < 2:
            return 50
        
        # 基于现金含量比率的标准差计算稳定性
        ratios = [m['cash_content_ratio'] for m in quality_metrics if m['cash_content_ratio'] != 0]
        if not ratios:
            return 0
        
        std_dev = np.std(ratios)
        # 标准差越小，稳定性越高
        if std_dev <= 0.2:
            return 90
        elif std_dev <= 0.5:
            return 70
        elif std_dev <= 1.0:
            return 50
        else:
            return 30
    
    def _get_overall_cash_quality_rating(self, avg_cash_content: float, stability_score: float) -> str:
        """综合现金流质量评级"""
        # 综合评分 = 平均现金含量权重70% + 稳定性权重30%
        content_score = min(avg_cash_content * 50, 100)  # 现金含量转换为百分制
        total_score = content_score * 0.7 + stability_score * 0.3
        
        if total_score >= 80:
            return 'A'
        elif total_score >= 70:
            return 'B'
        elif total_score >= 60:
            return 'C'
        elif total_score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _analyze_cash_flow_trend(self, quality_metrics: List[Dict]) -> str:
        """分析现金流趋势"""
        if len(quality_metrics) < 3:
            return '数据不足，无法分析趋势'
        
        recent_ratios = [m['cash_content_ratio'] for m in quality_metrics[:3]]
        
        if all(recent_ratios[i] >= recent_ratios[i+1] for i in range(len(recent_ratios)-1)):
            return '改善趋势'
        elif all(recent_ratios[i] <= recent_ratios[i+1] for i in range(len(recent_ratios)-1)):
            return '恶化趋势'
        else:
            return '波动较大'
    
    def _format_cash_flow_metrics(self, quality_analysis: Dict) -> str:
        """格式化现金流指标"""
        return f"""
        现金流质量指标:
        - 平均现金含量比率: {quality_analysis['average_cash_content']:.2f}
        - 稳定性评分: {quality_analysis['stability_score']:.0f}/100
        - 综合评级: {quality_analysis['overall_rating']}
        - 趋势: {quality_analysis['trend']}
        
        近期现金流情况:
        {self._format_recent_periods(quality_analysis['periods'][:4])}
        """
    
    def _format_recent_periods(self, periods: List[Dict]) -> str:
        """格式化近期数据"""
        lines = []
        for p in periods:
            lines.append(f"  {p['period']}: 经营现金流{p['operating_cf_billion']}亿, 净利润{p['net_income_billion']}亿, 现金含量{p['cash_content_ratio']:.2f}")
        return "\n".join(lines)
    
    def _generate_cash_flow_insights(self, quality_analysis: Dict) -> str:
        """生成现金流质量洞察"""
        insights = []
        
        avg_content = quality_analysis['average_cash_content']
        rating = quality_analysis['overall_rating']
        trend = quality_analysis['trend']
        
        # 现金流质量评价
        if rating in ['A', 'B']:
            insights.append("现金流质量优良，经营现金流与净利润匹配度高")
        elif rating == 'C':
            insights.append("现金流质量一般，需关注现金回收效率")
        else:
            insights.append("现金流质量较差，存在应收账款增长或利润质量问题")
        
        # 趋势分析
        if trend == '改善趋势':
            insights.append("现金流质量呈改善趋势，经营效率提升")
        elif trend == '恶化趋势':
            insights.append("现金流质量恶化，需重点关注应收账款和存货管理")
        
        # 具体建议
        if avg_content < 0.8:
            insights.append("建议加强应收账款管理，提高现金回收效率")
        
        return "; ".join(insights)
    
    def _perform_multi_period_analysis(self, financial_data: List[FinancialData]) -> Dict[str, Any]:
        """执行多期财务对比分析"""
        try:
            # 计算同比增长率
            yoy_growth = self._calculate_yoy_growth(financial_data)
            
            # 计算环比增长率
            qoq_growth = self._calculate_qoq_growth(financial_data)
            
            # 趋势分析
            trend_analysis = self._analyze_financial_trends(financial_data)
            
            # 波动性分析
            volatility_analysis = self._analyze_volatility(financial_data)
            
            return {
                'yoy_growth': yoy_growth,
                'qoq_growth': qoq_growth,
                'trend_analysis': trend_analysis,
                'volatility_analysis': volatility_analysis,
                'period_count': len(financial_data)
            }
            
        except Exception as e:
            self.logger.error(f"多期分析计算错误: {e}")
            return {
                'yoy_growth': {},
                'qoq_growth': {},
                'trend_analysis': {},
                'volatility_analysis': {},
                'period_count': 0
            }
    
    def _calculate_yoy_growth(self, financial_data: List[FinancialData]) -> Dict[str, float]:
        """计算同比增长率"""
        if len(financial_data) < 5:  # 需要至少5期数据才能计算年度同比
            return {}
        
        try:
            # 假设数据按季度排列，第4期前的数据作为同比基数
            current = financial_data[0]
            year_ago = financial_data[4] if len(financial_data) > 4 else None
            
            if not year_ago:
                return {}
            
            def calculate_growth(current_val, previous_val):
                if previous_val == 0:
                    return 0
                return ((current_val - previous_val) / abs(previous_val)) * 100
            
            return {
                'revenue_yoy': round(calculate_growth(current.total_revenue, year_ago.total_revenue), 2),
                'net_income_yoy': round(calculate_growth(current.n_income_attr_p, year_ago.n_income_attr_p), 2),
                'operating_cf_yoy': round(calculate_growth(current.n_cashflow_act, year_ago.n_cashflow_act), 2),
                'total_assets_yoy': round(calculate_growth(current.total_assets, year_ago.total_assets), 2),
                'roe_yoy': round(current.roe - year_ago.roe, 2)
            }
            
        except Exception as e:
            self.logger.warning(f"同比增长率计算错误: {e}")
            return {}
    
    def _calculate_qoq_growth(self, financial_data: List[FinancialData]) -> Dict[str, float]:
        """计算环比增长率"""
        if len(financial_data) < 2:
            return {}
        
        try:
            current = financial_data[0]
            previous = financial_data[1]
            
            def calculate_growth(current_val, previous_val):
                if previous_val == 0:
                    return 0
                return ((current_val - previous_val) / abs(previous_val)) * 100
            
            return {
                'revenue_qoq': round(calculate_growth(current.total_revenue, previous.total_revenue), 2),
                'net_income_qoq': round(calculate_growth(current.n_income_attr_p, previous.n_income_attr_p), 2),
                'operating_cf_qoq': round(calculate_growth(current.n_cashflow_act, previous.n_cashflow_act), 2),
                'total_assets_qoq': round(calculate_growth(current.total_assets, previous.total_assets), 2),
                'roe_qoq': round(current.roe - previous.roe, 2)
            }
            
        except Exception as e:
            self.logger.warning(f"环比增长率计算错误: {e}")
            return {}
    
    def _analyze_financial_trends(self, financial_data: List[FinancialData]) -> Dict[str, str]:
        """分析财务趋势"""
        if len(financial_data) < 3:
            return {'trend': '数据不足'}
        
        try:
            # 分析近3期ROE趋势
            recent_roe = [data.roe for data in financial_data[:3]]
            roe_trend = self._determine_trend(recent_roe)
            
            # 分析营收趋势
            recent_revenue = [data.total_revenue for data in financial_data[:3]]
            revenue_trend = self._determine_trend(recent_revenue)
            
            # 分析净利润趋势
            recent_profit = [data.n_income_attr_p for data in financial_data[:3]]
            profit_trend = self._determine_trend(recent_profit)
            
            return {
                'roe_trend': roe_trend,
                'revenue_trend': revenue_trend,
                'profit_trend': profit_trend
            }
            
        except Exception as e:
            self.logger.warning(f"趋势分析错误: {e}")
            return {'trend': '分析失败'}
    
    def _determine_trend(self, values: List[float]) -> str:
        """判断数值序列的趋势"""
        if len(values) < 2:
            return '数据不足'
        
        # 计算连续变化方向
        changes = []
        for i in range(len(values) - 1):
            if values[i] > values[i + 1]:
                changes.append('up')
            elif values[i] < values[i + 1]:
                changes.append('down')
            else:
                changes.append('flat')
        
        if all(change == 'up' for change in changes):
            return '上升趋势'
        elif all(change == 'down' for change in changes):
            return '下降趋势'
        elif all(change == 'flat' for change in changes):
            return '平稳趋势'
        else:
            return '波动趋势'
    
    def _analyze_volatility(self, financial_data: List[FinancialData]) -> Dict[str, Any]:
        """分析财务指标波动性"""
        if len(financial_data) < 3:
            return {'volatility': '数据不足'}
        
        try:
            # 计算ROE波动率
            roe_values = [data.roe for data in financial_data]
            roe_volatility = np.std(roe_values)
            
            # 计算营收波动率
            revenue_values = [data.total_revenue for data in financial_data]
            revenue_volatility = np.std(revenue_values) / np.mean(revenue_values) if np.mean(revenue_values) > 0 else 0
            
            return {
                'roe_volatility': round(roe_volatility, 2),
                'revenue_volatility': round(revenue_volatility * 100, 2),  # 转换为百分比
                'stability_rating': self._rate_stability(roe_volatility, revenue_volatility)
            }
            
        except Exception as e:
            self.logger.warning(f"波动性分析错误: {e}")
            return {'volatility': '分析失败'}
    
    def _rate_stability(self, roe_volatility: float, revenue_volatility: float) -> str:
        """评价财务稳定性"""
        # 综合评价ROE和营收的波动性
        if roe_volatility <= 2 and revenue_volatility <= 0.1:
            return '非常稳定'
        elif roe_volatility <= 5 and revenue_volatility <= 0.2:
            return '比较稳定'
        elif roe_volatility <= 10 and revenue_volatility <= 0.3:
            return '一般稳定'
        else:
            return '波动较大'
    
    def _format_multi_period_data(self, financial_data: List[FinancialData]) -> str:
        """格式化多期财务数据"""
        lines = ["近期财务数据:"]
        for data in financial_data:
            lines.append(f"""
            {data.end_date}: 
            - 营收: {data.total_revenue/100000000:.2f}亿元
            - 净利润: {data.n_income_attr_p/100000000:.2f}亿元  
            - ROE: {data.roe:.2f}%
            - 经营现金流: {data.n_cashflow_act/100000000:.2f}亿元
            """)
        return "\n".join(lines)
    
    def _format_comparison_metrics(self, comparison_analysis: Dict) -> str:
        """格式化对比分析指标"""
        yoy = comparison_analysis.get('yoy_growth', {})
        qoq = comparison_analysis.get('qoq_growth', {})
        trends = comparison_analysis.get('trend_analysis', {})
        volatility = comparison_analysis.get('volatility_analysis', {})
        
        return f"""
        增长率分析:
        同比增长率: 营收{yoy.get('revenue_yoy', 'N/A')}%, 净利润{yoy.get('net_income_yoy', 'N/A')}%
        环比增长率: 营收{qoq.get('revenue_qoq', 'N/A')}%, 净利润{qoq.get('net_income_qoq', 'N/A')}%
        
        趋势分析:
        ROE趋势: {trends.get('roe_trend', 'N/A')}
        营收趋势: {trends.get('revenue_trend', 'N/A')}
        净利润趋势: {trends.get('profit_trend', 'N/A')}
        
        稳定性分析:
        财务稳定性: {volatility.get('stability_rating', 'N/A')}
        ROE波动率: {volatility.get('roe_volatility', 'N/A')}%
        """
    
    def _generate_comparison_insights(self, comparison_analysis: Dict) -> str:
        """生成对比分析洞察"""
        insights = []
        
        yoy = comparison_analysis.get('yoy_growth', {})
        qoq = comparison_analysis.get('qoq_growth', {})
        trends = comparison_analysis.get('trend_analysis', {})
        volatility = comparison_analysis.get('volatility_analysis', {})
        
        # 增长率洞察
        revenue_yoy = yoy.get('revenue_yoy', 0)
        if revenue_yoy > 20:
            insights.append("营收同比增长强劲，业务扩张迅速")
        elif revenue_yoy > 10:
            insights.append("营收同比增长良好，业务稳健发展")
        elif revenue_yoy < -10:
            insights.append("营收同比下滑明显，需关注业务变化")
        
        # 趋势洞察
        if trends.get('roe_trend') == '上升趋势':
            insights.append("ROE持续改善，盈利能力增强")
        elif trends.get('roe_trend') == '下降趋势':
            insights.append("ROE持续下滑，盈利能力减弱")
        
        # 稳定性洞察
        stability = volatility.get('stability_rating', '')
        if stability in ['非常稳定', '比较稳定']:
            insights.append("财务表现稳定，经营风险较低")
        elif stability == '波动较大':
            insights.append("财务指标波动较大，需关注经营稳定性")
        
        return "; ".join(insights) if insights else "财务数据分析完成"
    
    def _format_financial_metrics(self, data: FinancialData) -> Dict:
        """格式化财务指标用于输出"""
        return {
            'revenue_billion': round(data.total_revenue / 100000000, 2),
            'net_income_billion': round(data.n_income_attr_p / 100000000, 2),
            'total_assets_billion': round(data.total_assets / 100000000, 2),
            'roe_percent': round(data.roe, 2),
            'debt_ratio_percent': round(data.debt_to_assets, 2),
            'current_ratio': round(data.current_ratio, 2),
            'operating_cashflow_billion': round(data.n_cashflow_act / 100000000, 2)
        }
    
    def dupont_analysis(self, ts_code: str) -> Dict[str, Any]:
        """杜邦分析 - ROE分解"""
        try:
            financial_data = self.get_financial_data(ts_code, periods=4)
            
            if not financial_data:
                return {
                    'success': False,
                    'error': f'未找到股票 {ts_code} 的财务数据'
                }
            
            latest_data = financial_data[0]
            
            # 杜邦分析：ROE = 净利率 × 总资产周转率 × 权益乘数
            dupont_metrics = self._calculate_dupont_metrics(latest_data)
            
            # 多期杜邦分析趋势
            trend_analysis = []
            for data in financial_data:
                period_dupont = self._calculate_dupont_metrics(data)
                trend_analysis.append({
                    'period': data.end_date,
                    **period_dupont
                })
            
            # 使用LLM生成详细分析
            stock_name = self._get_stock_name(ts_code)
            analysis_report = self.analysis_chain.invoke({
                'stock_info': f"{stock_name} ({ts_code})",
                'analysis_type': '杜邦分析 - ROE分解',
                'financial_data': self._format_financial_data_for_llm(latest_data),
                'metrics': self._format_dupont_metrics(dupont_metrics),
                'insights': self._generate_dupont_insights(dupont_metrics, trend_analysis)
            })
            
            return {
                'success': True,
                'ts_code': ts_code,
                'analysis_type': 'dupont_analysis',
                'period': latest_data.end_date,
                'dupont_metrics': dupont_metrics,
                'trend_analysis': trend_analysis,
                'analysis_report': analysis_report,
                'type': 'financial_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"杜邦分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'financial_analysis'
            }
    
    def cash_flow_quality_analysis(self, ts_code: str) -> Dict[str, Any]:
        """现金流质量分析"""
        try:
            financial_data = self.get_financial_data(ts_code, periods=8)  # 获取更多期数据用于趋势分析
            
            if not financial_data:
                return {
                    'success': False,
                    'error': f'未找到股票 {ts_code} 的财务数据'
                }
            
            # 现金流质量分析
            quality_analysis = self._analyze_cash_flow_quality(financial_data)
            
            # 使用LLM生成详细分析
            stock_name = self._get_stock_name(ts_code)
            analysis_report = self.analysis_chain.invoke({
                'stock_info': f"{stock_name} ({ts_code})",
                'analysis_type': '现金流质量分析',
                'financial_data': self._format_financial_data_for_llm(financial_data[0]),
                'metrics': self._format_cash_flow_metrics(quality_analysis),
                'insights': self._generate_cash_flow_insights(quality_analysis)
            })
            
            return {
                'success': True,
                'ts_code': ts_code,
                'analysis_type': 'cash_flow_quality',
                'quality_analysis': quality_analysis,
                'analysis_report': analysis_report,
                'type': 'financial_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"现金流质量分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'financial_analysis'
            }
    
    def multi_period_comparison(self, ts_code: str) -> Dict[str, Any]:
        """多期财务对比分析"""
        try:
            financial_data = self.get_financial_data(ts_code, periods=8)  # 获取8期数据进行对比
            
            if len(financial_data) < 2:
                return {
                    'success': False,
                    'error': f'股票 {ts_code} 的历史数据不足，无法进行多期对比'
                }
            
            # 多期对比分析
            comparison_analysis = self._perform_multi_period_analysis(financial_data)
            
            # 使用LLM生成详细分析
            stock_name = self._get_stock_name(ts_code)
            analysis_report = self.analysis_chain.invoke({
                'stock_info': f"{stock_name} ({ts_code})",
                'analysis_type': '多期财务对比分析',
                'financial_data': self._format_multi_period_data(financial_data[:4]),
                'metrics': self._format_comparison_metrics(comparison_analysis),
                'insights': self._generate_comparison_insights(comparison_analysis)
            })
            
            return {
                'success': True,
                'ts_code': ts_code,
                'analysis_type': 'multi_period_comparison',
                'comparison_analysis': comparison_analysis,
                'analysis_report': analysis_report,
                'type': 'financial_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"多期财务对比分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'financial_analysis'
            }
    
    def comprehensive_analysis(self, ts_code: str) -> Dict[str, Any]:
        """综合财务分析"""
        # 默认进行财务健康度分析
        return self.analyze_financial_health(ts_code)


# 测试代码
if __name__ == "__main__":
    print("Financial Analysis Agent 模块创建成功!")
    print("支持的分析功能:")
    print("1. 财务健康度分析")
    print("2. 杜邦分析")
    print("3. 现金流质量分析")
    print("4. 多期财务对比")
    print("5. 综合财务分析")