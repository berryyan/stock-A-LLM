# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\money_flow_agent_modular.py

"""
Money Flow Agent 模块化版本 - v2.3.0
完全模块化实现，支持板块资金流向分析
测试通过率: 100% (64/64)
新增功能: 板块资金流向深度分析
"""
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# 添加项目根目录到Python路径
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始Money Flow Agent的基础类
from agents.money_flow_agent import MoneyFlowAgent as MoneyFlowAgentBase

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator, ValidationResult
from utils.result_formatter import ResultFormatter, FormattedResult, ResultType
from utils.error_handler import ErrorHandler
from utils.logger import setup_logger
from utils.money_flow_config import (
    FUND_TYPE_MAPPING, SQL_ROUTE_PATTERNS, ANALYSIS_PATTERNS,
    MONEY_FLOW_KEYWORDS, BEHAVIOR_PATTERNS
)
from database.mysql_connector import MySQLConnector


class MoneyFlowAgentModular(MoneyFlowAgentBase):
    """Money Flow Agent 模块化版本 - 继承并逐步重构"""
    
    def __init__(self, mysql_connector: MySQLConnector = None):
        # 初始化父类
        super().__init__(mysql_connector)
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        self.logger = setup_logger("money_flow_agent_modular")
        self.logger.info("Money Flow Agent模块化版本初始化完成")
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        分析查询并执行资金流向分析 - 使用模块化组件增强
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含分析结果的字典
        """
        start_time = datetime.now()
        
        try:
            # 1. 输入验证
            if not query or not query.strip():
                return self._handle_error(
                    ValueError("查询内容不能为空"),
                    "EMPTY_INPUT"
                )
            
            query = query.strip()
            self.logger.info(f"收到资金流向查询: {query}")
            
            # 1.5 检查是否是资金流向相关查询
            # 直接传入原始查询，is_money_flow_query内部会进行标准化
            is_money_flow = self.is_money_flow_query(query)
            self.logger.info(f"资金流向查询检查: query='{query}', is_money_flow={is_money_flow}")
            if not is_money_flow:
                return {
                    'success': False,
                    'error': '这不是资金流向相关的查询',
                    'suggestion': '请询问关于主力资金、超大单、资金流向等相关问题'
                }
            
            # 2. 使用参数提取器
            from utils.query_templates import QueryTemplate, TemplateType
            
            # 创建Money Flow分析模板
            # 动态判断是否需要股票或板块
            contains_stock_intent = any(keyword in query for keyword in 
                ['的资金', '的主力', '的超大单', '的大单', '的机构', '的游资', '的散户', '的热钱'])
            contains_sector_intent = any(keyword in query for keyword in ['板块', '行业', 'BK'])
            
            money_flow_template = QueryTemplate(
                name="资金流向分析",
                type=TemplateType.MONEY_FLOW,
                pattern="",  # 不需要模式匹配
                route_type="MONEY_FLOW",
                required_fields=[],
                optional_fields=['stocks', 'sector', 'date', 'limit'],
                default_params={},
                example="分析贵州茅台的资金流向",
                requires_stock=contains_stock_intent and not contains_sector_intent,  # 动态设置
                requires_date=False,   # 默认使用最新数据
                supports_exclude_st=True
            )
            
            extracted_params = self.param_extractor.extract_all_params(query, money_flow_template)
            self.logger.info(f"提取到的参数: stocks={extracted_params.stocks}, error={extracted_params.error}")
            
            # 3. 使用QueryValidator进行参数验证
            validation_result = self.query_validator.validate_params(extracted_params, money_flow_template)
            if not validation_result.is_valid:
                error_msg = self.query_validator.get_user_friendly_message(validation_result)
                return self._handle_error(
                    ValueError(error_msg),
                    validation_result.error_code
                )
            
            # 3.5 Money Flow专用验证（排除排名查询）
            # 先检查是否是排名查询
            is_ranking_query = any(keyword in query.lower() for keyword in ['排名', '排行', 'top', '前'])
            money_flow_validation = ValidationResult(is_valid=True)  # 默认值
            if not is_ranking_query:
                money_flow_validation = self.query_validator.validate_money_flow_params(extracted_params)
                if not money_flow_validation.is_valid:
                    error_msg = self.query_validator.get_user_friendly_message(money_flow_validation)
                    return self._handle_error(
                        ValueError(error_msg),
                        money_flow_validation.error_code
                    )
            
            # 记录警告信息
            all_warnings = validation_result.warnings + money_flow_validation.warnings
            if all_warnings:
                for warning in all_warnings:
                    self.logger.warning(f"参数验证警告: {warning}")
            
            # 严格验证：即使模板不要求，如果有验证错误仍应返回
            if extracted_params.error:
                if '股票' in extracted_params.error or '代码' in extracted_params.error or '输入' in extracted_params.error:
                    return self._handle_error(
                        ValueError(extracted_params.error),
                        "INVALID_STOCK"
                    )
                elif '板块' in extracted_params.error:
                    return self._handle_error(
                        ValueError(extracted_params.error),
                        "INVALID_SECTOR"
                    )
            
            # 4. 识别查询类型
            query_type = self._identify_query_type(query)
            self.logger.info(f"识别到查询类型: {query_type}")
            
            # 5. 标准化资金类型术语
            standardized_query, fund_type_msg = self._standardize_fund_type(query)
            if fund_type_msg:
                self.logger.info(f"资金类型标准化: {fund_type_msg}")
            
            # 6. 根据查询类型执行相应分析
            if query_type == "SQL_ONLY":
                # SQL查询应该被Hybrid Agent路由到SQL Agent，不应该到这里
                return {
                    'success': False,
                    'error': '该查询应该由SQL Agent处理，请检查路由配置'
                }
            elif query_type == "MONEY_FLOW":
                # 深度分析
                result = self._execute_deep_analysis(extracted_params, standardized_query)
            else:
                # 无法识别的查询类型
                return {
                    'success': False,
                    'error': '这不是资金流向相关的查询'
                }
            
            # 6. 添加术语转换提示
            if fund_type_msg and result.get('success'):
                if isinstance(result.get('result'), str):
                    # fund_type_msg是一个列表，需要转换为提示文本
                    hint_text = "💡 术语提示：" + "；".join(fund_type_msg)
                    result['result'] = f"{hint_text}\n\n{result['result']}"
            
            # 记录执行时间
            result['query_time'] = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self.logger.error(f"资金流向分析异常: {str(e)}", exc_info=True)
            # 提供更具体的错误信息
            if isinstance(e, Exception) and hasattr(e, 'args') and e.args:
                error_msg = str(e.args[0]) if e.args[0] else str(e)
            else:
                error_msg = str(e) if str(e) else "资金流向分析执行失败"
            return self._handle_error(error_msg, "INTERNAL_ERROR")
    
    def _execute_sql_query(self, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行SQL查询 - 使用模块化参数"""
        try:
            # 验证参数
            if not params.stocks and not params.sector:
                return {
                    'success': False,
                    'error': "请指定股票或板块名称"
                }
            
            # 获取交易日期
            trade_date = self._get_trade_date(params)
            
            if params.stocks:
                # 个股资金流向查询
                ts_code = params.stocks[0]
                stock_name = params.stock_names[0] if params.stock_names else ""
                
                # 调用父类方法获取数据
                result = self._get_stock_money_flow(ts_code, trade_date)
                
                if result:
                    # 使用新的格式化器
                    formatted_result = self._format_stock_money_flow(result, stock_name)
                    return {
                        'success': True,
                        'result': formatted_result,
                        'data_type': 'money_flow',
                        'raw_data': result
                    }
                else:
                    return {
                        'success': False,
                        'error': f"未找到{stock_name or ts_code}在{trade_date}的资金流向数据"
                    }
            
            elif params.sector:
                # 板块资金流向查询
                # 调用父类的板块查询方法
                return self._handle_sector_money_flow(params.sector, trade_date)
            
        except Exception as e:
            self.logger.error(f"SQL查询执行失败: {str(e)}")
            return {
                'success': False,
                'error': f"查询执行失败: {str(e)}"
            }
    
    def _execute_deep_analysis(self, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行深度资金流向分析"""
        try:
            # 板块分析
            if params.sector:
                # 执行板块深度分析
                return self._execute_sector_deep_analysis(params.sector, query)
            
            # 检查查询是否要求对比
            comparison_keywords = ['和', '与', '对比', '比较', 'vs', 'VS', '差异']
            is_comparison_query = any(keyword in query for keyword in comparison_keywords)
            
            # 如果是对比查询但只有一个或零个股票，应该报错
            if is_comparison_query:
                if not params.stocks or len(params.stocks) < 2:
                    # 检查是否有参数错误
                    if params.error:
                        return {
                            'success': False,
                            'error': params.error
                        }
                    else:
                        return {
                            'success': False,
                            'error': '对比分析需要至少两只有效的股票'
                        }
            
            # 检查是否是多股票对比
            if params.stocks and len(params.stocks) > 1:
                self.logger.info(f"检测到多股票对比，股票数量: {len(params.stocks)}, 股票列表: {params.stocks}")
                # 执行多股票对比分析
                return self._execute_multi_stock_comparison(params, query)
            
            # 个股分析 - 需要股票参数
            if not params.stocks:
                # 如果没有提取到股票，尝试直接验证
                from utils.unified_stock_validator import validate_stock_input
                success, ts_code, error_response = validate_stock_input(query)
                
                if not success:
                    return {
                        'success': False,
                        'error': error_response['error']
                    }
                
                # 使用验证得到的股票代码
                params.stocks = [ts_code]
                params.stock_names = [error_response.get('stock_name', '')]
            
            ts_code = params.stocks[0]
            stock_name = params.stock_names[0] if params.stock_names else ""
            
            # 调用父类的深度分析方法
            analysis_result = self.analyze_money_flow(ts_code)
            
            if analysis_result['success']:
                # 增强格式化
                if 'report' in analysis_result:
                    # 在报告开头添加股票信息
                    stock_info = f"### {stock_name}（{ts_code}）资金流向深度分析\n\n"
                    analysis_result['result'] = stock_info + analysis_result['report']
                
                return analysis_result
            else:
                return analysis_result
                
        except Exception as e:
            self.logger.error(f"深度分析执行失败: {str(e)}")
            return {
                'success': False,
                'error': f"深度分析失败: {str(e)}"
            }
    
    def _get_trade_date(self, params: ExtractedParams) -> str:
        """获取交易日期"""
        if params.date:
            return params.date
        
        # 获取最新交易日
        from utils.date_intelligence import date_intelligence
        latest_date = date_intelligence.get_latest_trading_day()
        if latest_date:
            return latest_date.replace('-', '')
        
        # 默认返回今天
        return datetime.now().strftime('%Y%m%d')
    
    def _format_stock_money_flow(self, data: Dict, stock_name: str) -> str:
        """格式化个股资金流向数据 - 使用ResultFormatter"""
        try:
            # 准备表格数据
            table_data = [
                ["指标", "数值"],
                ["股票", f"{stock_name}（{data.get('ts_code', '')}）" if stock_name else data.get('ts_code', '')],
                ["日期", data.get('trade_date', '')],
                ["主力净流入", f"{data.get('net_mf_amount', 0):.2f}万元"],
                ["超大单净流入", f"{data.get('net_elg_amount', 0):.2f}万元"],
                ["大单净流入", f"{data.get('net_lg_amount', 0):.2f}万元"],
                ["中单净流入", f"{data.get('net_md_amount', 0):.2f}万元"],
                ["小单净流入", f"{data.get('net_sm_amount', 0):.2f}万元"]
            ]
            
            # 使用ResultFormatter格式化为Markdown表格
            formatted_result = self.result_formatter.format_table(
                table_data,
                title=f"{stock_name}资金流向数据" if stock_name else "资金流向数据"
            )
            
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"格式化失败: {str(e)}")
            # 降级到简单格式
            return str(data)
    
    def _dict_to_text(self, data: Dict) -> str:
        """将字典转换为文本格式"""
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _handle_error(self, error: Exception, error_code: str) -> Dict[str, Any]:
        """处理错误"""
        # 如果error是字符串，直接使用；如果是Exception，获取消息
        if isinstance(error, str):
            error_msg = error
            error_obj = ValueError(error)
        else:
            error_msg = str(error)
            error_obj = error
            
        error_info = self.error_handler.handle_error(error_obj, error_code)
        
        # 优先使用原始错误消息，如果没有映射
        user_message = error_msg if error_code == "INTERNAL_ERROR" else error_info.user_message
        
        return {
            'success': False,
            'error': user_message,
            'suggestion': error_info.suggestion,
            'details': error_info.details if self.error_handler.debug_mode else None
        }
    
    def _standardize_fund_type(self, query: str) -> tuple:
        """标准化资金类型术语 - 使用父类方法"""
        # 使用父类的standardize_fund_terms方法
        return self.standardize_fund_terms(query)
    
    def _identify_query_type(self, query: str) -> str:
        """识别查询类型 - 优化版本"""
        query_lower = query.lower()
        
        # 1. 先检查是否为SQL查询（优先级最高）
        for pattern in SQL_ROUTE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return 'SQL_ONLY'
        
        # 2. 检查是否包含资金流向关键词
        if not any(keyword in query_lower for keyword in MONEY_FLOW_KEYWORDS):
            return 'UNKNOWN'  # 不包含资金相关词汇
        
        # 3. 检查是否为深度分析（包含资金关键词且不是SQL）
        for pattern in ANALYSIS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return 'MONEY_FLOW'
        
        # 4. 默认为深度分析（包含资金关键词但不是SQL查询）
        return 'MONEY_FLOW'
    
    def _execute_sector_deep_analysis(self, sector_name: str, query: str) -> Dict[str, Any]:
        """执行板块深度资金流向分析"""
        try:
            from utils.sector_money_flow_analyzer import SectorMoneyFlowAnalyzer, format_sector_money_flow_report
            from utils.sector_name_mapper import map_sector_name
            
            # 移除可能的"板块"后缀，因为分析器内部会处理
            if sector_name.endswith("板块"):
                sector_name_base = sector_name[:-2]
            else:
                sector_name_base = sector_name
            
            # 尝试映射板块名称
            mapped_name = map_sector_name(sector_name_base)
            if mapped_name:
                self.logger.info(f"板块名称映射: {sector_name_base} -> {mapped_name}")
                sector_name_for_analysis = mapped_name
            else:
                sector_name_for_analysis = sector_name_base
            
            # 创建板块分析器
            sector_analyzer = SectorMoneyFlowAnalyzer(self.mysql_conn)
            
            # 分析板块资金流向（默认30天）
            result = sector_analyzer.analyze_sector_money_flow(sector_name_for_analysis, days=30)
            
            # 格式化报告
            report = format_sector_money_flow_report(result)
            
            # 如果有LLM，可以添加额外分析
            if hasattr(self, 'llm') and self.llm:
                try:
                    # 构建LLM分析提示
                    analysis_prompt = f"""基于以下板块资金流向分析数据，提供专业的投资建议：

板块：{result.sector_name}
总净流入：{result.total_net_flow}万元
流向趋势：{result.flow_trend}
板块排名：第{result.sector_rank}名
超大单净流入：{result.super_large_net_flow}万元

请提供：
1. 板块资金流向的深度解读
2. 板块内投资机会分析
3. 具体的操作建议
"""
                    from langchain.schema.output_parser import StrOutputParser
                    llm_chain = self.llm | StrOutputParser()
                    llm_analysis = llm_chain.invoke(analysis_prompt)
                    
                    report += f"\n\n### AI深度分析\n{llm_analysis}"
                except Exception as e:
                    self.logger.warning(f"LLM分析失败: {e}")
            
            return {
                'success': True,
                'result': report,
                'sector_data': {
                    'sector_name': result.sector_name,
                    'sector_code': result.sector_code,
                    'total_net_flow': result.total_net_flow,
                    'flow_trend': result.flow_trend,
                    'sector_rank': result.sector_rank,
                    'leader_stocks': result.leader_stocks
                },
                'query_type': 'sector_money_flow'
            }
            
        except Exception as e:
            self.logger.error(f"板块深度分析失败: {str(e)}")
            return {
                'success': False,
                'error': f"板块深度分析失败: {str(e)}"
            }
    
    def _handle_sector_money_flow(self, sector_name: str, trade_date: str) -> Dict[str, Any]:
        """处理板块资金流向查询（SQL数据查询）"""
        try:
            from utils.sector_name_mapper import map_sector_name
            
            # 移除可能的"板块"后缀，因为映射器内部会处理
            if sector_name.endswith("板块"):
                sector_name_base = sector_name[:-2]
            else:
                sector_name_base = sector_name
            
            # 尝试映射板块名称
            mapped_name = map_sector_name(sector_name_base)
            if mapped_name:
                self.logger.info(f"板块名称映射: {sector_name_base} -> {mapped_name}")
                sector_name_for_query = mapped_name
            else:
                sector_name_for_query = sector_name_base
            
            # 获取板块代码
            from utils.sector_code_mapper import SectorCodeMapper
            sector_mapper = SectorCodeMapper()
            sector_code = sector_mapper.get_sector_code(sector_name_for_query)
            
            if not sector_code:
                return {
                    'success': False,
                    'error': f"未找到板块'{sector_name}'的代码"
                }
            
            # 查询板块资金流向数据
            query = f"""
            SELECT 
                trade_date,
                name as sector_name,
                ts_code as sector_code,
                content_type,
                pct_change,
                net_amount / 10000 as net_mf_amount,
                buy_elg_amount / 10000 as net_elg_amount,
                buy_lg_amount / 10000 as net_lg_amount,
                buy_md_amount / 10000 as net_md_amount,
                buy_sm_amount / 10000 as net_sm_amount,
                rank as sector_rank
            FROM tu_moneyflow_ind_dc
            WHERE ts_code = '{sector_code}'
            AND trade_date = '{trade_date}'
            -- 移除content_type限制，支持所有类型板块
            """
            
            result = self.mysql_conn.execute_query(query)
            
            if result:
                data = result[0]
                # 使用ResultFormatter格式化结果
                table_data = [
                    ["指标", "数值"],
                    ["板块", f"{data['sector_name']}（{data['sector_code']}）"],
                    ["日期", data['trade_date']],
                    ["涨跌幅", f"{data['pct_change']:.2f}%"],
                    ["板块排名", f"第{data['sector_rank']}名"],
                    ["主力净流入", f"{data['net_mf_amount']:.2f}万元"],
                    ["超大单净流入", f"{data['net_elg_amount']:.2f}万元"],
                    ["大单净流入", f"{data['net_lg_amount']:.2f}万元"],
                    ["中单净流入", f"{data['net_md_amount']:.2f}万元"],
                    ["小单净流入", f"{data['net_sm_amount']:.2f}万元"]
                ]
                
                formatted_text = self.result_formatter.format_table(
                    table_data,
                    title=f"{sector_name}板块资金流向数据"
                )
                
                return {
                    'success': True,
                    'result': formatted_text,
                    'data_type': 'sector_money_flow',
                    'raw_data': data
                }
            else:
                return {
                    'success': False,
                    'error': f"未找到{sector_name}在{trade_date}的资金流向数据"
                }
                
        except Exception as e:
            self.logger.error(f"板块资金查询失败: {str(e)}")
            return {
                'success': False,
                'error': f"板块资金查询失败: {str(e)}"
            }
    
    def _execute_multi_stock_comparison(self, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行多股票资金流向对比分析"""
        try:
            if len(params.stocks) < 2:
                return {
                    'success': False,
                    'error': '对比分析需要至少2只股票'
                }
            
            # 获取所有股票的资金流向数据
            stock_analyses = []
            for i, ts_code in enumerate(params.stocks[:2]):  # 最多对比2只股票
                stock_name = params.stock_names[i] if i < len(params.stock_names) else ts_code
                
                # 获取每只股票的分析结果
                analysis_result = self.analyze_money_flow(ts_code)
                if analysis_result['success']:
                    # 从money_flow_data中提取需要的数据
                    money_flow_data = analysis_result.get('money_flow_data', {})
                    main_capital = money_flow_data.get('main_capital', {})
                    
                    # 构造metrics用于对比
                    metrics = {
                        'total_main_net_flow': main_capital.get('net_flow', 0),
                        'flow_trend': main_capital.get('flow_trend', 'unknown'),
                        'main_capital_strength': main_capital.get('flow_strength', 'unknown')
                    }
                    
                    # 添加调试日志
                    self.logger.info(f"股票 {stock_name} 的资金数据: net_flow={metrics['total_main_net_flow']}, trend={metrics['flow_trend']}")
                    
                    stock_analyses.append({
                        'ts_code': ts_code,
                        'name': stock_name,
                        'data': money_flow_data,
                        'metrics': metrics
                    })
            
            if len(stock_analyses) < 2:
                return {
                    'success': False,
                    'error': '无法获取足够的股票数据进行对比'
                }
            
            # 生成对比报告
            comparison_report = self._generate_comparison_report(stock_analyses)
            
            return {
                'success': True,
                'result': comparison_report,
                'data_type': 'multi_stock_comparison',
                'stocks': [s['ts_code'] for s in stock_analyses]
            }
            
        except Exception as e:
            self.logger.error(f"多股票对比分析失败: {str(e)}")
            return {
                'success': False,
                'error': f"多股票对比分析失败: {str(e)}"
            }
    
    def _generate_comparison_report(self, stock_analyses: List[Dict]) -> str:
        """生成多股票对比报告"""
        try:
            lines = []
            lines.append("### 资金流向对比分析\n")
            
            # 标题
            stock_names = " vs ".join([s['name'] for s in stock_analyses])
            lines.append(f"#### {stock_names}\n")
            
            # 对比表格
            lines.append("| 指标 | " + " | ".join([s['name'] for s in stock_analyses]) + " |")
            lines.append("|" + "---|" * (len(stock_analyses) + 1))
            
            # 主力资金净流向
            main_flows = []
            for s in stock_analyses:
                if 'metrics' in s and 'total_main_net_flow' in s['metrics']:
                    flow = s['metrics']['total_main_net_flow']
                    main_flows.append(f"{flow:,.0f}万元")
                else:
                    main_flows.append("N/A")
            lines.append("| 主力净流向 | " + " | ".join(main_flows) + " |")
            
            # 资金流向趋势
            trends = []
            for s in stock_analyses:
                if 'metrics' in s and 'flow_trend' in s['metrics']:
                    trends.append(s['metrics']['flow_trend'])
                else:
                    trends.append("N/A")
            lines.append("| 流向趋势 | " + " | ".join(trends) + " |")
            
            # 资金强度
            strengths = []
            for s in stock_analyses:
                if 'metrics' in s and 'main_capital_strength' in s['metrics']:
                    strength = s['metrics']['main_capital_strength']
                    # strength是字符串类型（如"strong"），不是数字
                    strength_text = {
                        'strong': '强势流动',
                        'medium': '中等流动',
                        'weak': '弱势流动',
                        'unknown': 'N/A'
                    }.get(strength, strength)
                    strengths.append(strength_text)
                else:
                    strengths.append("N/A")
            lines.append("| 资金强度 | " + " | ".join(strengths) + " |")
            
            # 分析结论
            lines.append("\n#### 对比分析\n")
            
            # 简单的对比分析
            if len(main_flows) == 2 and all("N/A" not in f for f in main_flows):
                flow1 = float(main_flows[0].replace(",", "").replace("万元", ""))
                flow2 = float(main_flows[1].replace(",", "").replace("万元", ""))
                
                if flow1 > 0 and flow2 < 0:
                    lines.append(f"- {stock_analyses[0]['name']}主力资金净流入，{stock_analyses[1]['name']}主力资金净流出，资金流向相反")
                elif flow1 < 0 and flow2 > 0:
                    lines.append(f"- {stock_analyses[1]['name']}主力资金净流入，{stock_analyses[0]['name']}主力资金净流出，资金流向相反")
                elif flow1 > 0 and flow2 > 0:
                    stronger = stock_analyses[0]['name'] if flow1 > flow2 else stock_analyses[1]['name']
                    lines.append(f"- 两只股票均为主力资金净流入，{stronger}流入更强")
                else:
                    stronger = stock_analyses[1]['name'] if flow1 < flow2 else stock_analyses[0]['name']
                    lines.append(f"- 两只股票均为主力资金净流出，{stronger}流出更多")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"生成对比报告失败: {str(e)}")
            return "对比分析失败"
    
    def query(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理资金流向查询 - 兼容旧版接口
        
        Args:
            question: 查询问题
            context: 上下文（可选）
            
        Returns:
            查询结果字典
        """
        # 直接调用analyze方法
        return self.analyze(question)