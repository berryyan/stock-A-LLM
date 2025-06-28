"""
资金流向分析Agent v1.0
专门处理资金流向相关的查询和分析
"""

import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.llms import OpenAI

from database.mysql_connector import MySQLConnector
from utils.money_flow_analyzer import MoneyFlowAnalyzer, format_money_flow_report
from utils.logger import setup_logger
from config.settings import settings
from utils.schema_knowledge_base import schema_kb


class MoneyFlowAgent:
    """资金流向分析Agent"""
    
    def __init__(self, mysql_connector: MySQLConnector = None):
        """初始化资金流向分析Agent"""
        self.mysql_conn = mysql_connector or MySQLConnector()
        self.money_flow_analyzer = MoneyFlowAnalyzer(self.mysql_conn)
        self.logger = setup_logger("money_flow_agent")
        
        # 初始化LLM
        try:
            self.llm = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=2000
            )
        except Exception as e:
            self.logger.error(f"LLM初始化失败: {e}")
            self.llm = None
        
        # 使用Schema知识库获取资金流向字段（性能优化）
        self.money_flow_fields = schema_kb.get_money_flow_fields()
        self.logger.info(f"从Schema知识库获取资金流向字段: {len(self.money_flow_fields)}个")
        
        # 记录性能提升
        stats = schema_kb.get_performance_stats()
        self.logger.info(f"Schema知识库统计: 共{stats['field_count']}个字段, "
                        f"中文映射{stats['chinese_mapping_count']}个")
        
        # 资金流向查询模式
        self.MONEY_FLOW_PATTERNS = [
            r'资金流向|资金流入|资金流出',
            r'主力资金|机构资金|大资金',
            r'超大单|大单|中单|小单',
            r'主力.*净流入|主力.*净流出',
            r'资金.*流向.*分析',
            r'机构.*行为|主力.*行为',
            r'买入.*卖出|流入.*流出',
            r'散户.*机构|个人.*机构'
        ]
        
        # 创建分析提示模板
        self.analysis_prompt = PromptTemplate(
            input_variables=["ts_code", "analysis_data", "user_question"],
            template="""
你是一个专业的股票资金流向分析师。基于以下资金流向分析数据，回答用户的问题。

股票代码：{ts_code}
用户问题：{user_question}

资金流向分析数据：
{analysis_data}

请根据以上数据，用专业且通俗易懂的语言回答用户的问题。要求：
1. 重点突出主力资金和超大单的分析
2. 用具体数字说话，避免空泛描述
3. 提供明确的投资建议和风险提示
4. 使用中文回答，语言专业但易懂
5. 如果数据显示异常情况，要特别提醒用户注意

分析回答：
"""
        )
    
    def is_money_flow_query(self, question: str) -> bool:
        """判断是否是资金流向相关查询"""
        try:
            question_lower = question.lower()
            
            # 检查是否包含资金流向相关关键词
            for pattern in self.MONEY_FLOW_PATTERNS:
                if re.search(pattern, question, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"判断资金流向查询失败: {e}")
            return False
    
    def extract_ts_code(self, question: str) -> Optional[str]:
        """从问题中提取股票代码"""
        try:
            # 股票代码模式：6位数字 + .SH/.SZ 或 单独6位数字
            patterns = [
                r'\b(\d{6}\.(?:SH|SZ))\b',  # 完整格式
                r'\b(\d{6})\b',             # 仅数字
            ]
            
            for pattern in patterns:
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    code = match.group(1)
                    # 如果只有数字，需要添加交易所后缀
                    if '.' not in code:
                        # 简单规则：6开头是上交所，0/3开头是深交所
                        if code.startswith('6'):
                            code += '.SH'
                        elif code.startswith(('0', '3')):
                            code += '.SZ'
                    return code
            
            # 如果没有找到代码，尝试通过公司名称查找
            return self._find_ts_code_by_name(question)
            
        except Exception as e:
            self.logger.error(f"提取股票代码失败: {e}")
            return None
    
    def _find_ts_code_by_name(self, question: str) -> Optional[str]:
        """通过公司名称查找股票代码"""
        try:
            # 常见公司名称关键词
            name_keywords = [
                ('贵州茅台', '600519.SH'),
                ('茅台', '600519.SH'),
                ('平安银行', '000001.SZ'),
                ('万科', '000002.SZ'),
                ('五粮液', '000858.SZ'),
                ('比亚迪', '002594.SZ'),
                ('宁德时代', '300750.SZ'),
                ('腾讯控股', '00700.HK'),  # 港股暂不支持
                ('阿里巴巴', '09988.HK'),  # 港股暂不支持
            ]
            
            for name, code in name_keywords:
                if name in question:
                    # 暂时不支持港股
                    if '.HK' in code:
                        continue
                    return code
            
            # 如果都没找到，尝试数据库查询
            return self._query_ts_code_from_db(question)
            
        except Exception as e:
            self.logger.error(f"通过名称查找股票代码失败: {e}")
            return None
    
    def _query_ts_code_from_db(self, question: str) -> Optional[str]:
        """从数据库查询股票代码"""
        try:
            # 提取可能的公司名称
            # 简单实现：查找中文字符序列
            chinese_pattern = r'[\u4e00-\u9fff]+'
            names = re.findall(chinese_pattern, question)
            
            for name in names:
                if len(name) >= 2:  # 至少2个字符
                    query = f"""
                    SELECT ts_code, name 
                    FROM tu_stock_basic 
                    WHERE name LIKE '%{name}%' 
                    LIMIT 1
                    """
                    
                    results = self.mysql_conn.execute_query(query)
                    if results:
                        return results[0].get('ts_code')
            
            return None
            
        except Exception as e:
            self.logger.error(f"数据库查询股票代码失败: {e}")
            return None
    
    def extract_analysis_period(self, question: str) -> int:
        """提取分析周期，默认30天"""
        try:
            # 查找天数
            day_patterns = [
                r'(\d+)天',
                r'最近(\d+)天',
                r'近(\d+)天',
                r'(\d+)日'
            ]
            
            for pattern in day_patterns:
                match = re.search(pattern, question)
                if match:
                    days = int(match.group(1))
                    # 限制在合理范围内
                    return min(max(days, 1), 365)
            
            # 查找周、月等时间单位
            if '周' in question:
                week_match = re.search(r'(\d+)周', question)
                if week_match:
                    weeks = int(week_match.group(1))
                    return min(weeks * 7, 365)
                else:
                    return 7  # 默认一周
            
            if '月' in question:
                month_match = re.search(r'(\d+)月', question)
                if month_match:
                    months = int(month_match.group(1))
                    return min(months * 30, 365)
                else:
                    return 30  # 默认一个月
            
            # 默认30天
            return 30
            
        except Exception as e:
            self.logger.error(f"提取分析周期失败: {e}")
            return 30
    
    def analyze_money_flow(self, ts_code: str, days: int = 30) -> Dict[str, Any]:
        """执行资金流向分析"""
        try:
            self.logger.info(f"开始资金流向分析: {ts_code}, {days}天")
            
            # 使用分析器进行分析
            result = self.money_flow_analyzer.analyze_money_flow(ts_code, days)
            
            # 转换为字典格式
            money_flow_data = {
                'ts_code': ts_code,
                'analysis_period': f"{days}天",
                'main_capital': {
                    'net_flow': result.main_capital_net_flow,
                    'flow_trend': result.main_capital_flow_trend,
                    'flow_strength': result.main_capital_flow_strength,
                    'flow_consistency': result.main_capital_flow_consistency
                },
                'super_large_orders': {
                    'net_flow': result.super_large_net_flow,
                    'buy_ratio': result.super_large_buy_ratio,
                    'frequency': result.super_large_frequency,
                    'behavior_pattern': result.super_large_behavior_pattern,
                    'dominance': result.super_large_dominance,
                    'price_correlation': result.super_large_vs_price_correlation
                },
                'fund_distribution': result.fund_distribution,
                'assessment': {
                    'overall': result.overall_assessment,
                    'risk_warning': result.risk_warning,
                    'investment_suggestion': result.investment_suggestion
                }
            }
            
            return {
                'success': True,
                'data': money_flow_data,
                'report': format_money_flow_report(result, ts_code)
            }
            
        except Exception as e:
            self.logger.error(f"资金流向分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None,
                'report': None
            }
    
    def query(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理资金流向查询"""
        try:
            self.logger.info(f"处理资金流向查询: {question}")
            
            # 输入验证
            if not question or not question.strip():
                return {
                    'success': False,
                    'error': '查询问题不能为空',
                    'answer': None,
                    'money_flow_data': None
                }
            
            # 判断是否是资金流向查询
            if not self.is_money_flow_query(question):
                return {
                    'success': False,
                    'error': '这不是资金流向相关的查询',
                    'answer': None,
                    'money_flow_data': None
                }
            
            # 提取股票代码
            ts_code = self.extract_ts_code(question)
            if not ts_code:
                return {
                    'success': False,
                    'error': '无法识别股票代码，请提供完整的股票代码或公司名称',
                    'answer': None,
                    'money_flow_data': None
                }
            
            # 提取分析周期
            days = self.extract_analysis_period(question)
            
            # 执行资金流向分析
            analysis_result = self.analyze_money_flow(ts_code, days)
            
            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': analysis_result['error'],
                    'answer': None,
                    'money_flow_data': None
                }
            
            # 生成LLM分析
            llm_analysis = ""
            if self.llm:
                try:
                    analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()
                    llm_analysis = analysis_chain.invoke({
                        "ts_code": ts_code,
                        "analysis_data": json.dumps(analysis_result['data'], ensure_ascii=False, indent=2),
                        "user_question": question
                    })
                except Exception as e:
                    self.logger.error(f"LLM分析失败: {e}")
                    llm_analysis = "LLM分析暂时不可用"
            
            # 组合最终答案
            final_answer = analysis_result['report']
            if llm_analysis:
                final_answer += f"\n\n### AI深度分析\n{llm_analysis}"
            
            return {
                'success': True,
                'answer': final_answer,
                'money_flow_data': analysis_result['data'],
                'query_type': 'money_flow',
                'ts_code': ts_code,
                'analysis_period': days,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"资金流向查询处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': None,
                'money_flow_data': None
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Agent统计信息"""
        return {
            'agent_type': 'money_flow',
            'version': '1.0',
            'supported_patterns': len(self.MONEY_FLOW_PATTERNS),
            'status': 'operational'
        }


# 测试函数
if __name__ == "__main__":
    agent = MoneyFlowAgent()
    
    # 测试查询
    test_questions = [
        "分析贵州茅台的资金流向",
        "600519.SH最近的主力资金流入情况",
        "茅台的超大单资金分析",
        "平安银行的资金流向如何？"
    ]
    
    for question in test_questions:
        print(f"\n测试问题: {question}")
        result = agent.query(question)
        print(f"成功: {result['success']}")
        if result['success']:
            print(f"答案: {result['answer'][:200]}...")
        else:
            print(f"错误: {result['error']}")