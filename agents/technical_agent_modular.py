#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Technical Analysis Agent - 模块化版本
提供技术指标查询和分析功能
"""

import os
import sys
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatDeepSeek
from langchain.schema import StrOutputParser
from sqlalchemy import text

from database.mysql_connector import MySQLConnector
from utils.parameter_extractor import ParameterExtractor
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter
from utils.error_handler import ErrorHandler
from utils.agent_response import AgentResponse
from utils.date_intelligence import DateIntelligence
from utils.logger import setup_logger
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from config.sql_templates import (
    TECHNICAL_MA,
    TECHNICAL_MACD,
    TECHNICAL_KDJ,
    TECHNICAL_RSI,
    TECHNICAL_BOLL,
    TECHNICAL_CROSS,
    TECHNICAL_COMPREHENSIVE
)

# 设置日志
logger = setup_logger('technical_agent_modular', 'logs/technical_agent_modular.log')


class TechnicalAgentModular:
    """技术分析Agent模块化版本"""
    
    def __init__(self):
        """初始化Agent"""
        # 初始化LLM
        self.llm = ChatDeepSeek(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model="deepseek-chat",
            temperature=0
        )
        
        # 初始化模块
        self.parameter_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        self.date_intelligence = DateIntelligence()
        self.db = MySQLConnector()
        
        # 技术指标模板
        self.indicator_templates = {
            "ma": {
                "pattern": r"(.*?)的?(5|10|20|30|60|120|250)?日?均线",
                "params": ["stock", "period"],
                "sql": TECHNICAL_MA,
                "description": "移动平均线"
            },
            "macd": {
                "pattern": r"(.*?)的?MACD(金叉|死叉|指标)?",
                "params": ["stock", "signal_type"],
                "sql": TECHNICAL_MACD,
                "description": "MACD指标"
            },
            "kdj": {
                "pattern": r"(.*?)的?KDJ(指标|超买|超卖)?",
                "params": ["stock", "condition"],
                "sql": TECHNICAL_KDJ,
                "description": "KDJ指标"
            },
            "rsi": {
                "pattern": r"(.*?)的?RSI(指标|超买|超卖)?",
                "params": ["stock", "condition"],
                "sql": TECHNICAL_RSI,
                "description": "RSI指标"
            },
            "boll": {
                "pattern": r"(.*?)的?(布林带|BOLL|布林线)",
                "params": ["stock"],
                "sql": TECHNICAL_BOLL,
                "description": "布林带"
            },
            "cross": {
                "pattern": r"(.*?)的?(金叉|死叉|交叉信号)",
                "params": ["stock", "cross_type"],
                "sql": TECHNICAL_CROSS,
                "description": "交叉信号"
            }
        }
        
        # 分析提示词模板
        self.analysis_prompt = PromptTemplate(
            input_variables=["query", "data", "indicator_type"],
            template="""作为专业的技术分析师，请根据以下技术指标数据分析{query}：

技术指标类型：{indicator_type}
数据：
{data}

请提供：
1. 技术指标解读
2. 当前趋势判断
3. 关键价位提示
4. 操作建议（仅供参考）

注意：
- 使用专业术语但要易懂
- 结合多个指标综合判断
- 提示风险和不确定性
"""
        )
    
    async def process_query(self, query: str) -> AgentResponse:
        """处理技术分析查询"""
        try:
            logger.info(f"处理技术分析查询: {query}")
            
            # 1. 参数提取
            params = self.parameter_extractor.extract(query)
            if params.get('error'):
                return AgentResponse.error(params['error_message'])
            
            # 2. 识别指标类型
            indicator_type = self._identify_indicator_type(query)
            if not indicator_type:
                return await self._handle_complex_analysis(query, params)
            
            # 3. 参数验证
            validation_result = self.query_validator.validate(
                params, 
                template_type=f"technical_{indicator_type}"
            )
            if not validation_result['valid']:
                return AgentResponse.error(validation_result['message'])
            
            # 4. 快速查询
            if self._is_quick_query(query, indicator_type):
                return await self._quick_query(params, indicator_type)
            
            # 5. 高级分析
            return await self._advanced_analysis(query, params, indicator_type)
            
        except Exception as e:
            logger.error(f"处理查询时出错: {str(e)}")
            return self.error_handler.handle(e)
    
    def _identify_indicator_type(self, query: str) -> Optional[str]:
        """识别技术指标类型"""
        for indicator, config in self.indicator_templates.items():
            if re.search(config['pattern'], query, re.IGNORECASE):
                return indicator
        return None
    
    def _is_quick_query(self, query: str, indicator_type: str) -> bool:
        """判断是否为快速查询"""
        # 简单的指标查询使用快速路径
        analysis_keywords = ['分析', '判断', '解读', '如何', '怎么样', '趋势']
        return not any(keyword in query for keyword in analysis_keywords)
    
    async def _quick_query(self, params: Dict, indicator_type: str) -> AgentResponse:
        """快速查询技术指标"""
        try:
            # 获取股票代码
            ts_code = params.get('stocks', [{}])[0].get('ts_code')
            if not ts_code:
                return AgentResponse.error("未识别到有效的股票")
            
            # 获取交易日期
            trade_date = self._get_trade_date(params)
            
            # 根据指标类型执行查询
            result = await self._execute_indicator_query(
                ts_code, trade_date, indicator_type, params
            )
            
            if result['success']:
                # 格式化结果
                formatted = self._format_indicator_result(
                    result['data'], indicator_type, params
                )
                return AgentResponse.success(data=formatted)
            else:
                return AgentResponse.error(result['error'])
                
        except Exception as e:
            logger.error(f"快速查询失败: {str(e)}")
            return self.error_handler.handle(e)
    
    async def _execute_indicator_query(
        self, 
        ts_code: str, 
        trade_date: str, 
        indicator_type: str,
        params: Dict
    ) -> Dict:
        """执行技术指标查询"""
        try:
            config = self.indicator_templates[indicator_type]
            
            # 准备SQL参数
            sql_params = {
                'ts_code': ts_code,
                'trade_date': trade_date
            }
            
            # 特殊处理某些指标
            if indicator_type == 'macd':
                # MACD需要查询一段时间的数据
                sql_params['start_date'] = self._get_n_days_before(trade_date, 30)
                sql_params['limit'] = 30
            elif indicator_type == 'cross':
                # 交叉信号需要查询历史数据
                sql_params['start_date'] = self._get_n_days_before(trade_date, 60)
            
            # 执行查询
            df = pd.read_sql(
                text(config['sql']), 
                self.db.engine,
                params=sql_params
            )
            
            if df.empty:
                return {
                    'success': False,
                    'error': f"未找到{ts_code}在{trade_date}的技术指标数据"
                }
            
            return {
                'success': True,
                'data': df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"执行指标查询失败: {str(e)}")
            return {
                'success': False,
                'error': f"查询失败: {str(e)}"
            }
    
    def _format_indicator_result(
        self, 
        data: List[Dict], 
        indicator_type: str,
        params: Dict
    ) -> str:
        """格式化技术指标结果"""
        if not data:
            return "未找到相关数据"
        
        # 根据不同指标类型格式化
        if indicator_type == 'ma':
            return self._format_ma_result(data, params)
        elif indicator_type == 'macd':
            return self._format_macd_result(data)
        elif indicator_type == 'kdj':
            return self._format_kdj_result(data)
        elif indicator_type == 'rsi':
            return self._format_rsi_result(data)
        elif indicator_type == 'boll':
            return self._format_boll_result(data)
        elif indicator_type == 'cross':
            return self._format_cross_result(data)
        else:
            # 默认表格格式
            return self.result_formatter.format_as_table(data)
    
    def _format_ma_result(self, data: List[Dict], params: Dict) -> str:
        """格式化均线结果"""
        latest = data[0]
        stock_name = params.get('stocks', [{}])[0].get('name', '')
        
        # 提取请求的均线周期
        period = params.get('period', '5')
        ma_key = f'ma_{period}'
        
        result = f"**{stock_name}均线数据**\n\n"
        result += f"日期：{latest['trade_date']}\n"
        result += f"收盘价：{latest.get('close_price', 'N/A')}\n\n"
        
        # 显示所有均线
        ma_periods = [5, 10, 20, 30, 60, 120, 250]
        result += "| 均线 | 数值 | 状态 |\n"
        result += "|------|------|------|\n"
        
        close_price = float(latest.get('close_price', 0))
        
        for p in ma_periods:
            ma_value = latest.get(f'ma_{p}')
            if ma_value and ma_value != 'NULL':
                ma_value = float(ma_value)
                status = "上方" if close_price > ma_value else "下方"
                result += f"| MA{p} | {ma_value:.2f} | {status} |\n"
        
        return result
    
    def _format_macd_result(self, data: List[Dict]) -> str:
        """格式化MACD结果"""
        result = "**MACD指标数据**\n\n"
        
        # 显示最近10条数据
        result += "| 日期 | DIF | DEA | MACD柱 | 信号 |\n"
        result += "|------|-----|-----|---------|------|\n"
        
        for row in data[:10]:
            signal = row.get('macd_cross_signal', '')
            result += (f"| {row['trade_date']} | "
                      f"{float(row.get('macd_dif', 0)):.4f} | "
                      f"{float(row.get('macd_dea', 0)):.4f} | "
                      f"{float(row.get('macd_histogram', 0)):.4f} | "
                      f"{signal} |\n")
        
        # 分析最新状态
        latest = data[0]
        if float(latest.get('macd_histogram', 0)) > 0:
            result += "\n当前MACD柱状图为正值，多头占优"
        else:
            result += "\n当前MACD柱状图为负值，空头占优"
        
        return result
    
    def _format_kdj_result(self, data: List[Dict]) -> str:
        """格式化KDJ结果"""
        latest = data[0]
        
        result = "**KDJ指标数据**\n\n"
        result += f"日期：{latest['trade_date']}\n\n"
        
        k_value = float(latest.get('kdj_k', 0))
        d_value = float(latest.get('kdj_d', 0))
        j_value = float(latest.get('kdj_j', 0))
        
        result += f"K值：{k_value:.2f}\n"
        result += f"D值：{d_value:.2f}\n"
        result += f"J值：{j_value:.2f}\n\n"
        
        # 判断状态
        if j_value > 100:
            result += "⚠️ J值超过100，处于超买区域，注意回调风险"
        elif j_value < 0:
            result += "⚠️ J值低于0，处于超卖区域，可能有反弹机会"
        elif 80 < j_value <= 100:
            result += "J值偏高，接近超买区域"
        elif 0 <= j_value <= 20:
            result += "J值偏低，接近超卖区域"
        else:
            result += "KDJ指标处于正常区间"
        
        return result
    
    def _format_rsi_result(self, data: List[Dict]) -> str:
        """格式化RSI结果"""
        latest = data[0]
        
        result = "**RSI指标数据**\n\n"
        result += f"日期：{latest['trade_date']}\n\n"
        
        rsi_6 = float(latest.get('rsi_6', 0))
        rsi_12 = float(latest.get('rsi_12', 0))
        rsi_24 = float(latest.get('rsi_24', 0))
        
        result += f"RSI(6)：{rsi_6:.2f}\n"
        result += f"RSI(12)：{rsi_12:.2f}\n"
        result += f"RSI(24)：{rsi_24:.2f}\n\n"
        
        # 判断状态
        if rsi_6 > 70:
            result += "⚠️ RSI(6)超过70，处于超买区域"
        elif rsi_6 < 30:
            result += "⚠️ RSI(6)低于30，处于超卖区域"
        else:
            result += "RSI指标处于正常区间"
        
        return result
    
    def _format_boll_result(self, data: List[Dict]) -> str:
        """格式化布林带结果"""
        latest = data[0]
        
        result = "**布林带指标数据**\n\n"
        result += f"日期：{latest['trade_date']}\n\n"
        
        close_price = float(latest.get('close_price', 0))
        upper = float(latest.get('boll_upper', 0))
        middle = float(latest.get('boll_middle', 0))
        lower = float(latest.get('boll_lower', 0))
        
        result += f"收盘价：{close_price:.2f}\n"
        result += f"上轨：{upper:.2f}\n"
        result += f"中轨：{middle:.2f}\n"
        result += f"下轨：{lower:.2f}\n\n"
        
        # 判断位置
        if close_price > upper:
            result += "⚠️ 股价突破布林带上轨，处于超买状态"
        elif close_price < lower:
            result += "⚠️ 股价跌破布林带下轨，处于超卖状态"
        else:
            position = (close_price - lower) / (upper - lower) * 100
            result += f"股价位于布林带内，相对位置：{position:.1f}%"
        
        return result
    
    def _format_cross_result(self, data: List[Dict]) -> str:
        """格式化交叉信号结果"""
        result = "**交叉信号记录**\n\n"
        
        # 筛选有信号的记录
        signals = [row for row in data if row.get('ma_cross_signal') or row.get('macd_cross_signal')]
        
        if not signals:
            return "最近60天内没有发现交叉信号"
        
        result += "| 日期 | 收盘价 | MA信号 | MACD信号 |\n"
        result += "|------|--------|--------|----------|\n"
        
        for row in signals[:10]:
            result += (f"| {row['trade_date']} | "
                      f"{float(row.get('close_price', 0)):.2f} | "
                      f"{row.get('ma_cross_signal', '')} | "
                      f"{row.get('macd_cross_signal', '')} |\n")
        
        return result
    
    async def _advanced_analysis(
        self, 
        query: str, 
        params: Dict,
        indicator_type: str
    ) -> AgentResponse:
        """高级技术分析"""
        try:
            # 获取基础数据
            quick_result = await self._quick_query(params, indicator_type)
            
            if not quick_result.success:
                return quick_result
            
            # 获取更多数据用于分析
            comprehensive_data = await self._get_comprehensive_data(params)
            
            # 使用LLM进行深度分析
            analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()
            
            analysis = await analysis_chain.ainvoke({
                "query": query,
                "data": comprehensive_data,
                "indicator_type": self.indicator_templates[indicator_type]['description']
            })
            
            # 组合结果
            result = f"{quick_result.data}\n\n---\n\n**深度技术分析**\n\n{analysis}"
            
            return AgentResponse.success(data=result)
            
        except Exception as e:
            logger.error(f"高级分析失败: {str(e)}")
            return self.error_handler.handle(e)
    
    async def _handle_complex_analysis(self, query: str, params: Dict) -> AgentResponse:
        """处理复杂的技术分析请求"""
        try:
            # 获取综合技术数据
            comprehensive_data = await self._get_comprehensive_data(params)
            
            if not comprehensive_data:
                return AgentResponse.error("未找到相关技术数据")
            
            # 构建分析提示词
            complex_prompt = PromptTemplate(
                input_variables=["query", "data"],
                template="""作为专业的技术分析师，请根据以下综合技术指标数据回答问题：{query}

技术指标数据：
{data}

请提供：
1. 技术面整体评估
2. 主要技术指标解读
3. 趋势和形态分析
4. 支撑压力位
5. 综合操作建议

注意：技术分析仅供参考，投资需谨慎。
"""
            )
            
            # LLM分析
            analysis_chain = complex_prompt | self.llm | StrOutputParser()
            result = await analysis_chain.ainvoke({
                "query": query,
                "data": comprehensive_data
            })
            
            return AgentResponse.success(data=result)
            
        except Exception as e:
            logger.error(f"复杂分析失败: {str(e)}")
            return self.error_handler.handle(e)
    
    async def _get_comprehensive_data(self, params: Dict) -> str:
        """获取综合技术数据"""
        try:
            ts_code = params.get('stocks', [{}])[0].get('ts_code')
            if not ts_code:
                return ""
            
            trade_date = self._get_trade_date(params)
            
            # 执行综合查询
            df = pd.read_sql(
                text(TECHNICAL_COMPREHENSIVE),
                self.db.engine,
                params={
                    'ts_code': ts_code,
                    'trade_date': trade_date
                }
            )
            
            if df.empty:
                return ""
            
            # 格式化为易读的文本
            data = df.to_dict('records')[0]
            result = f"股票代码：{ts_code}\n"
            result += f"日期：{trade_date}\n\n"
            
            # 价格信息
            result += f"收盘价：{data.get('close_price', 'N/A')}\n"
            
            # 均线
            result += "\n均线系统：\n"
            for period in [5, 10, 20, 60]:
                ma_value = data.get(f'ma_{period}')
                if ma_value:
                    result += f"MA{period}: {ma_value}\n"
            
            # MACD
            result += f"\nMACD指标：\n"
            result += f"DIF: {data.get('macd_dif', 'N/A')}\n"
            result += f"DEA: {data.get('macd_dea', 'N/A')}\n"
            result += f"MACD: {data.get('macd_histogram', 'N/A')}\n"
            
            # 其他指标
            result += f"\nKDJ: K={data.get('kdj_k', 'N/A')}, D={data.get('kdj_d', 'N/A')}, J={data.get('kdj_j', 'N/A')}\n"
            result += f"RSI(6): {data.get('rsi_6', 'N/A')}\n"
            result += f"布林带: 上轨={data.get('boll_upper', 'N/A')}, 中轨={data.get('boll_middle', 'N/A')}, 下轨={data.get('boll_lower', 'N/A')}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"获取综合数据失败: {str(e)}")
            return ""
    
    def _get_trade_date(self, params: Dict) -> str:
        """获取交易日期"""
        # 优先使用参数中的日期
        if params.get('date'):
            return params['date']
        
        # 默认使用最新交易日
        return self.date_intelligence.get_latest_trading_day()
    
    def _get_n_days_before(self, base_date: str, n: int) -> str:
        """获取N天前的日期"""
        date_obj = datetime.strptime(base_date, '%Y%m%d')
        target_date = date_obj - timedelta(days=n)
        return target_date.strftime('%Y%m%d')


# 用于测试
async def test_technical_agent():
    """测试技术分析Agent"""
    agent = TechnicalAgentModular()
    
    test_queries = [
        "贵州茅台的5日均线",
        "宁德时代的MACD金叉",
        "比亚迪的KDJ指标",
        "茅台的RSI超买了吗",
        "贵州茅台的布林带",
        "分析贵州茅台的技术趋势"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = await agent.process_query(query)
        print(f"结果: {result.data if result.success else result.error}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_technical_agent())