"""
资金流向分析模块 v1.0
基于tu_moneyflow_dc表数据，实现专业的资金流向分析

核心分析维度：
1. 主力资金净流入/流出 (最高优先级)
2. 超大单资金分析 (重点单独分析)
3. 四级资金分布分析 (超大单、大单、中单、小单)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger


@dataclass
class MoneyFlowData:
    """资金流向数据结构（基于实际数据库表结构）"""
    trade_date: str
    ts_code: str
    name: str
    pct_change: float         # 涨跌幅
    close: float              # 收盘价
    # 买入金额（万元）
    buy_sm_amount: float      # 小单买入
    buy_md_amount: float      # 中单买入
    buy_lg_amount: float      # 大单买入
    buy_elg_amount: float     # 超大单买入
    # 净流入金额（万元）
    net_amount: float         # 总净流入
    # 买入占比
    buy_sm_amount_rate: float # 小单买入占比
    buy_md_amount_rate: float # 中单买入占比
    buy_lg_amount_rate: float # 大单买入占比
    buy_elg_amount_rate: float # 超大单买入占比


@dataclass
class MoneyFlowAnalysisResult:
    """资金流向分析结果"""
    # 1. 主力资金净流入/流出 (最高优先级)
    main_capital_net_flow: float          # 主力资金净流入金额(万元)
    main_capital_flow_trend: str          # 流向趋势: 'inflow'/'outflow'/'balanced'
    main_capital_flow_strength: str       # 流向强度: 'strong'/'medium'/'weak'
    main_capital_flow_consistency: float  # 流向一致性评分(0-1)
    
    # 2. 超大单资金分析 (重点单独分析)
    super_large_net_flow: float           # 超大单净流入(万元)
    super_large_buy_ratio: float          # 超大单买入占比
    super_large_frequency: int            # 超大单交易频率
    super_large_vs_price_correlation: float  # 与股价相关性
    super_large_behavior_pattern: str     # 行为模式: 'accumulating'/'distributing'/'washing'
    super_large_dominance: float          # 超大单主导度(0-1)
    
    # 3. 四级资金分布
    fund_distribution: Dict[str, Dict[str, float]]  # 各级资金的买入、卖出、净流入
    
    # 4. 综合评估
    overall_assessment: str               # 综合评估
    risk_warning: Optional[str]           # 风险提示
    investment_suggestion: str            # 投资建议


class MoneyFlowAnalyzer:
    """资金流向分析器"""
    
    def __init__(self, mysql_connector: MySQLConnector = None):
        """初始化分析器"""
        self.mysql_conn = mysql_connector or MySQLConnector()
        self.logger = setup_logger("money_flow_analyzer")
        
        # 资金级别定义（万元）
        self.FUND_LEVELS = {
            'small': {'min': 0, 'max': 4, 'name': '小单'},
            'medium': {'min': 4, 'max': 20, 'name': '中单'},
            'large': {'min': 20, 'max': 100, 'name': '大单'},
            'super_large': {'min': 100, 'max': float('inf'), 'name': '超大单'}
        }
    
    def fetch_money_flow_data(self, ts_code: str, days: int = 30) -> List[MoneyFlowData]:
        """获取资金流向数据"""
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            query = f"""
            SELECT 
                trade_date, ts_code, name, pct_change, close,
                buy_sm_amount, buy_md_amount, buy_lg_amount, buy_elg_amount,
                net_amount,
                buy_sm_amount_rate, buy_md_amount_rate, buy_lg_amount_rate, buy_elg_amount_rate
            FROM tu_moneyflow_dc
            WHERE ts_code = '{ts_code}'
            AND trade_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY trade_date DESC
            """
            
            results = self.mysql_conn.execute_query(query)
            
            money_flow_data = []
            for row in results:
                data = MoneyFlowData(
                    trade_date=str(row.get('trade_date', '')),
                    ts_code=row.get('ts_code', ''),
                    name=row.get('name', ''),
                    pct_change=float(row.get('pct_change', 0) or 0),
                    close=float(row.get('close', 0) or 0),
                    buy_sm_amount=float(row.get('buy_sm_amount', 0) or 0),
                    buy_md_amount=float(row.get('buy_md_amount', 0) or 0),
                    buy_lg_amount=float(row.get('buy_lg_amount', 0) or 0),
                    buy_elg_amount=float(row.get('buy_elg_amount', 0) or 0),
                    net_amount=float(row.get('net_amount', 0) or 0),
                    buy_sm_amount_rate=float(row.get('buy_sm_amount_rate', 0) or 0),
                    buy_md_amount_rate=float(row.get('buy_md_amount_rate', 0) or 0),
                    buy_lg_amount_rate=float(row.get('buy_lg_amount_rate', 0) or 0),
                    buy_elg_amount_rate=float(row.get('buy_elg_amount_rate', 0) or 0)
                )
                money_flow_data.append(data)
            
            self.logger.info(f"获取到 {len(money_flow_data)} 条资金流向数据")
            return money_flow_data
            
        except Exception as e:
            self.logger.error(f"获取资金流向数据失败: {e}")
            return []
    
    def analyze_main_capital_flow(self, data: List[MoneyFlowData]) -> Dict[str, Any]:
        """分析主力资金净流入/流出 - 最高优先级"""
        if not data:
            return {}
        
        try:
            # 计算主力资金净流入总额（大单+超大单）
            total_main_net_flow = 0
            daily_flows = []
            
            for day_data in data:
                # 主力资金 = 大单 + 超大单（只有买入数据，使用净流入估算）
                # 根据买入占比推算主力资金净流入
                main_buy = day_data.buy_lg_amount + day_data.buy_elg_amount
                
                # 使用净流入数据估算主力资金净流向
                # 假设主力资金占总净流入的比例与其买入占总买入的比例相似
                total_buy = (day_data.buy_sm_amount + day_data.buy_md_amount + 
                           day_data.buy_lg_amount + day_data.buy_elg_amount)
                
                if total_buy > 0:
                    main_ratio = main_buy / total_buy
                    main_net = day_data.net_amount * main_ratio
                else:
                    main_net = day_data.net_amount * 0.5  # 默认主力占50%
                
                total_main_net_flow += main_net
                daily_flows.append(main_net)
            
            # 计算流向趋势
            positive_days = sum(1 for flow in daily_flows if flow > 0)
            negative_days = sum(1 for flow in daily_flows if flow < 0)
            total_days = len(daily_flows)
            
            if positive_days / total_days >= 0.6:
                flow_trend = 'inflow'
            elif negative_days / total_days >= 0.6:
                flow_trend = 'outflow'
            else:
                flow_trend = 'balanced'
            
            # 计算流向强度
            avg_abs_flow = np.mean([abs(flow) for flow in daily_flows])
            if avg_abs_flow > 5000:  # 500万以上
                flow_strength = 'strong'
            elif avg_abs_flow > 1000:  # 100万以上
                flow_strength = 'medium'
            else:
                flow_strength = 'weak'
            
            # 计算流向一致性
            if total_days > 0:
                consistency = max(positive_days, negative_days) / total_days
            else:
                consistency = 0
            
            return {
                'main_capital_net_flow': total_main_net_flow,
                'main_capital_flow_trend': flow_trend,
                'main_capital_flow_strength': flow_strength,
                'main_capital_flow_consistency': consistency,
                'daily_flows': daily_flows,
                'analysis_period': f"{len(data)}天"
            }
            
        except Exception as e:
            self.logger.error(f"主力资金分析失败: {e}")
            return {}
    
    def analyze_super_large_orders(self, data: List[MoneyFlowData], price_data: List[Dict] = None) -> Dict[str, Any]:
        """分析超大单资金 - 重点单独分析"""
        if not data:
            return {}
        
        try:
            # 超大单数据分析
            super_large_flows = []
            super_large_buy_total = 0
            super_large_sell_total = 0
            active_days = 0  # 有超大单交易的天数
            
            for day_data in data:
                super_large_buy = day_data.buy_elg_amount
                
                # 使用净流入数据和超大单买入占比估算超大单净流向
                total_buy = (day_data.buy_sm_amount + day_data.buy_md_amount + 
                           day_data.buy_lg_amount + day_data.buy_elg_amount)
                
                if total_buy > 0:
                    super_large_ratio = super_large_buy / total_buy
                    super_large_net = day_data.net_amount * super_large_ratio
                else:
                    super_large_net = 0
                
                super_large_buy_total += super_large_buy
                super_large_flows.append(super_large_net)
                
                # 判断是否有显著的超大单交易
                if super_large_buy > 100:  # 100万以上算活跃
                    active_days += 1
            
            super_large_net_flow = sum(super_large_flows)
            
            # 计算超大单买入占比（基于净流向推算）
            # 假设买入占比与净流向成正比
            if super_large_buy_total > 0:
                # 简化处理：根据净流向推算买入占比
                if super_large_net_flow > 0:
                    buy_ratio = 0.6 + min(0.3, super_large_net_flow / super_large_buy_total)
                else:
                    buy_ratio = 0.4 + max(-0.3, super_large_net_flow / super_large_buy_total)
            else:
                buy_ratio = 0.5
            
            # 分析行为模式
            if buy_ratio > 0.65 and super_large_net_flow > 0:
                behavior_pattern = 'accumulating'  # 建仓
            elif buy_ratio < 0.35 and super_large_net_flow < 0:
                behavior_pattern = 'distributing'  # 减仓
            elif abs(super_large_net_flow) / max(super_large_buy_total, 1) < 0.2:
                behavior_pattern = 'washing'  # 洗盘
            else:
                behavior_pattern = 'uncertain'  # 不确定
            
            # 计算超大单主导度
            total_flow = sum(abs(flow) for flow in super_large_flows)
            all_net_flow = sum(day_data.net_amount for day_data in data)
            
            if abs(all_net_flow) > 0:
                dominance = min(abs(super_large_net_flow) / abs(all_net_flow), 1.0)
            else:
                dominance = 0
            
            # 与股价相关性分析（如果有价格数据）
            price_correlation = 0.0
            if price_data and len(price_data) == len(super_large_flows):
                try:
                    price_changes = [p.get('pct_chg', 0) for p in price_data]
                    if len(price_changes) > 1:
                        correlation_matrix = np.corrcoef(super_large_flows, price_changes)
                        price_correlation = correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0
                except:
                    price_correlation = 0.0
            
            return {
                'super_large_net_flow': super_large_net_flow,
                'super_large_buy_ratio': buy_ratio,
                'super_large_frequency': active_days,
                'super_large_vs_price_correlation': price_correlation,
                'super_large_behavior_pattern': behavior_pattern,
                'super_large_dominance': dominance,
                'super_large_buy_total': super_large_buy_total,
                'super_large_sell_total': 0  # 没有卖出数据
            }
            
        except Exception as e:
            self.logger.error(f"超大单分析失败: {e}")
            return {}
    
    def analyze_four_tier_distribution(self, data: List[MoneyFlowData]) -> Dict[str, Dict[str, float]]:
        """分析四级资金分布"""
        if not data:
            return {}
        
        try:
            # 初始化统计数据
            distribution = {
                'super_large': {'buy': 0, 'sell': 0, 'net': 0, 'percentage': 0},
                'large': {'buy': 0, 'sell': 0, 'net': 0, 'percentage': 0},
                'medium': {'buy': 0, 'sell': 0, 'net': 0, 'percentage': 0},
                'small': {'buy': 0, 'sell': 0, 'net': 0, 'percentage': 0}
            }
            
            # 累计各级别资金数据（只有买入数据，根据净流入估算卖出）
            for day_data in data:
                total_buy = (day_data.buy_sm_amount + day_data.buy_md_amount + 
                           day_data.buy_lg_amount + day_data.buy_elg_amount)
                
                # 超大单
                distribution['super_large']['buy'] += day_data.buy_elg_amount
                if total_buy > 0:
                    ratio = day_data.buy_elg_amount / total_buy
                    net_flow = day_data.net_amount * ratio
                else:
                    net_flow = 0
                
                # 大单
                distribution['large']['buy'] += day_data.buy_lg_amount
                if total_buy > 0:
                    ratio = day_data.buy_lg_amount / total_buy
                    net_flow_lg = day_data.net_amount * ratio
                else:
                    net_flow_lg = 0
                
                # 中单
                distribution['medium']['buy'] += day_data.buy_md_amount
                if total_buy > 0:
                    ratio = day_data.buy_md_amount / total_buy
                    net_flow_md = day_data.net_amount * ratio
                else:
                    net_flow_md = 0
                
                # 小单
                distribution['small']['buy'] += day_data.buy_sm_amount
                if total_buy > 0:
                    ratio = day_data.buy_sm_amount / total_buy
                    net_flow_sm = day_data.net_amount * ratio
                else:
                    net_flow_sm = 0
                
                # 累计净流入（这里暂存到sell字段，后面会重新计算）
                distribution['super_large']['sell'] += net_flow
                distribution['large']['sell'] += net_flow_lg
                distribution['medium']['sell'] += net_flow_md
                distribution['small']['sell'] += net_flow_sm
            
            # 计算净流入和占比（sell字段实际存储的是净流入）
            total_net_flow = 0
            for level in distribution:
                net_flow = distribution[level]['sell']  # 之前存储的净流入
                distribution[level]['net'] = net_flow
                distribution[level]['sell'] = 0  # 重置sell字段
                total_net_flow += abs(net_flow)
            
            # 计算各级别占比
            for level in distribution:
                if total_net_flow > 0:
                    distribution[level]['percentage'] = abs(distribution[level]['net']) / total_net_flow * 100
                else:
                    distribution[level]['percentage'] = 0
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"四级资金分布分析失败: {e}")
            return {}
    
    def generate_comprehensive_assessment(self, 
                                        main_capital: Dict[str, Any],
                                        super_large: Dict[str, Any],
                                        distribution: Dict[str, Dict[str, float]]) -> Tuple[str, Optional[str], str]:
        """生成综合评估、风险提示和投资建议"""
        try:
            # 综合评估
            assessment_parts = []
            
            # 主力资金评估
            main_flow = main_capital.get('main_capital_net_flow', 0)
            if main_flow > 0:
                assessment_parts.append(f"主力资金净流入{main_flow:.0f}万元")
            else:
                assessment_parts.append(f"主力资金净流出{abs(main_flow):.0f}万元")
            
            # 超大单评估
            super_flow = super_large.get('super_large_net_flow', 0)
            behavior = super_large.get('super_large_behavior_pattern', 'uncertain')
            behavior_map = {
                'accumulating': '机构建仓',
                'distributing': '机构减仓',
                'washing': '主力洗盘',
                'uncertain': '行为不明'
            }
            assessment_parts.append(f"超大单呈现{behavior_map[behavior]}特征")
            
            overall_assessment = "，".join(assessment_parts)
            
            # 风险提示
            risk_warning = None
            if main_flow < -5000:  # 主力资金大幅流出
                risk_warning = "主力资金大幅流出，请注意投资风险"
            elif behavior == 'distributing' and super_large.get('super_large_dominance', 0) > 0.7:
                risk_warning = "机构大幅减仓，短期可能面临调整压力"
            
            # 投资建议
            suggestion_parts = []
            
            if main_flow > 0 and behavior == 'accumulating':
                suggestion_parts.append("主力资金持续流入，可适当关注")
            elif main_flow < 0 and behavior == 'distributing':
                suggestion_parts.append("资金面偏弱，建议谨慎操作")
            else:
                suggestion_parts.append("资金面相对平衡，建议结合技术面分析")
            
            # 基于一致性的建议
            consistency = main_capital.get('main_capital_flow_consistency', 0)
            if consistency > 0.8:
                suggestion_parts.append("资金流向一致性较强")
            elif consistency < 0.4:
                suggestion_parts.append("资金流向分歧较大，需观察后续走势")
            
            investment_suggestion = "，".join(suggestion_parts)
            
            return overall_assessment, risk_warning, investment_suggestion
            
        except Exception as e:
            self.logger.error(f"生成综合评估失败: {e}")
            return "数据分析中，请稍后再试", "数据获取异常", "建议等待数据更新后再做判断"
    
    def analyze_money_flow(self, ts_code: str, days: int = 30) -> MoneyFlowAnalysisResult:
        """执行完整的资金流向分析"""
        try:
            self.logger.info(f"开始分析 {ts_code} 的资金流向（{days}天）")
            
            # 1. 获取数据
            money_flow_data = self.fetch_money_flow_data(ts_code, days)
            if not money_flow_data:
                raise ValueError(f"未找到股票 {ts_code} 的资金流向数据")
            
            # 2. 主力资金分析 (最高优先级)
            main_capital_analysis = self.analyze_main_capital_flow(money_flow_data)
            
            # 3. 超大单分析 (重点单独分析)
            super_large_analysis = self.analyze_super_large_orders(money_flow_data)
            
            # 4. 四级资金分布分析
            distribution_analysis = self.analyze_four_tier_distribution(money_flow_data)
            
            # 5. 生成综合评估
            overall_assessment, risk_warning, investment_suggestion = self.generate_comprehensive_assessment(
                main_capital_analysis, super_large_analysis, distribution_analysis
            )
            
            # 6. 构建分析结果
            result = MoneyFlowAnalysisResult(
                # 主力资金
                main_capital_net_flow=main_capital_analysis.get('main_capital_net_flow', 0),
                main_capital_flow_trend=main_capital_analysis.get('main_capital_flow_trend', 'balanced'),
                main_capital_flow_strength=main_capital_analysis.get('main_capital_flow_strength', 'weak'),
                main_capital_flow_consistency=main_capital_analysis.get('main_capital_flow_consistency', 0),
                
                # 超大单
                super_large_net_flow=super_large_analysis.get('super_large_net_flow', 0),
                super_large_buy_ratio=super_large_analysis.get('super_large_buy_ratio', 0.5),
                super_large_frequency=super_large_analysis.get('super_large_frequency', 0),
                super_large_vs_price_correlation=super_large_analysis.get('super_large_vs_price_correlation', 0),
                super_large_behavior_pattern=super_large_analysis.get('super_large_behavior_pattern', 'uncertain'),
                super_large_dominance=super_large_analysis.get('super_large_dominance', 0),
                
                # 四级分布
                fund_distribution=distribution_analysis,
                
                # 综合评估
                overall_assessment=overall_assessment,
                risk_warning=risk_warning,
                investment_suggestion=investment_suggestion
            )
            
            self.logger.info(f"资金流向分析完成: {ts_code}")
            return result
            
        except Exception as e:
            self.logger.error(f"资金流向分析失败: {e}")
            # 返回空的分析结果
            return MoneyFlowAnalysisResult(
                main_capital_net_flow=0,
                main_capital_flow_trend='unknown',
                main_capital_flow_strength='unknown',
                main_capital_flow_consistency=0,
                super_large_net_flow=0,
                super_large_buy_ratio=0.5,
                super_large_frequency=0,
                super_large_vs_price_correlation=0,
                super_large_behavior_pattern='unknown',
                super_large_dominance=0,
                fund_distribution={},
                overall_assessment=f"分析失败: {str(e)}",
                risk_warning="数据获取异常",
                investment_suggestion="建议联系系统管理员"
            )


def format_money_flow_report(result: MoneyFlowAnalysisResult, ts_code: str) -> str:
    """格式化资金流向分析报告"""
    try:
        report = f"""
### {ts_code} 资金流向分析报告

#### 1. 主力资金流向 ⭐⭐⭐
- **净流向**: {'+' if result.main_capital_net_flow >= 0 else ''}{result.main_capital_net_flow:.0f}万元
- **流向趋势**: {'持续净流入' if result.main_capital_flow_trend == 'inflow' else '持续净流出' if result.main_capital_flow_trend == 'outflow' else '相对平衡'}
- **资金强度**: {'强势' if result.main_capital_flow_strength == 'strong' else '中等' if result.main_capital_flow_strength == 'medium' else '较弱'}流动
- **一致性**: {result.main_capital_flow_consistency:.1%}

#### 2. 超大单资金行为 ⭐⭐
- **超大单净流向**: {'+' if result.super_large_net_flow >= 0 else ''}{result.super_large_net_flow:.0f}万元
- **买入占比**: {result.super_large_buy_ratio:.1%}
- **交易活跃度**: {result.super_large_frequency}天有显著超大单交易
- **行为判断**: {'机构积极建仓' if result.super_large_behavior_pattern == 'accumulating' else '机构减仓离场' if result.super_large_behavior_pattern == 'distributing' else '主力洗盘整理' if result.super_large_behavior_pattern == 'washing' else '行为模式不明'}
- **主导程度**: {result.super_large_dominance:.1%}

#### 3. 四级资金分布
"""
        
        # 添加四级资金分布
        if result.fund_distribution:
            level_names = {
                'super_large': '超大单',
                'large': '大单',
                'medium': '中单',
                'small': '小单'
            }
            
            for level, name in level_names.items():
                if level in result.fund_distribution:
                    data = result.fund_distribution[level]
                    net_flow = data.get('net', 0)
                    percentage = data.get('percentage', 0)
                    flow_icon = '📈' if net_flow > 0 else '📉' if net_flow < 0 else '➡️'
                    report += f"- **{name}**: {'+' if net_flow >= 0 else ''}{net_flow:.0f}万 ({percentage:.1f}%) {flow_icon}\n"
        
        report += f"""
#### 4. 综合评估
- **整体判断**: {result.overall_assessment}
- **投资建议**: {result.investment_suggestion}
"""
        
        if result.risk_warning:
            report += f"- **风险提示**: ⚠️ {result.risk_warning}\n"
        
        return report.strip()
        
    except Exception as e:
        return f"报告生成失败: {str(e)}"


# 测试函数
if __name__ == "__main__":
    analyzer = MoneyFlowAnalyzer()
    result = analyzer.analyze_money_flow("600519.SH", days=30)
    report = format_money_flow_report(result, "600519.SH")
    print(report)