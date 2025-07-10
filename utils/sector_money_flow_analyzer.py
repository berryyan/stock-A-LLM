#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块资金流向分析器
提供板块级别的资金流向分析功能
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger
from utils.date_intelligence import get_latest_trading_day
from utils.sector_code_mapper import SectorCodeMapper


@dataclass
class SectorMoneyFlowResult:
    """板块资金流向分析结果"""
    sector_name: str                          # 板块名称
    sector_code: str                          # 板块代码
    analysis_period: str                      # 分析周期
    
    # 板块整体资金流向
    total_net_flow: float                     # 板块总净流入（万元）
    avg_daily_net_flow: float                 # 日均净流入（万元）
    flow_trend: str                           # 流向趋势：持续流入/持续流出/震荡
    flow_strength: float                      # 资金强度（0-1）
    flow_consistency: float                   # 一致性评分（0-1）
    
    # 板块内股票分析
    total_stocks: int                         # 板块内股票总数
    inflow_stocks: int                        # 净流入股票数
    outflow_stocks: int                       # 净流出股票数
    leader_stocks: List[Dict]                 # 龙头股票列表
    
    # 资金分布
    super_large_net_flow: float               # 超大单净流入（万元）
    large_net_flow: float                     # 大单净流入（万元）  
    medium_net_flow: float                    # 中单净流入（万元）
    small_net_flow: float                     # 小单净流入（万元）
    
    # 板块表现
    sector_pct_change: float                  # 板块涨跌幅
    avg_stock_pct_change: float               # 个股平均涨跌幅
    sector_rank: int                          # 板块排名
    
    # 综合评估
    overall_assessment: str                   # 整体评估
    investment_suggestion: str                # 投资建议
    risk_warning: str                         # 风险提示


class SectorMoneyFlowAnalyzer:
    """板块资金流向分析器"""
    
    def __init__(self, mysql_connector: MySQLConnector = None):
        """初始化分析器"""
        self.mysql = mysql_connector or MySQLConnector()
        self.logger = setup_logger("sector_money_flow_analyzer")
        self.sector_mapper = SectorCodeMapper()
        
    def analyze_sector_money_flow(self, sector_name: str, days: int = 30) -> SectorMoneyFlowResult:
        """
        分析板块资金流向
        
        Args:
            sector_name: 板块名称
            days: 分析天数
            
        Returns:
            板块资金流向分析结果
        """
        try:
            self.logger.info(f"开始分析 {sector_name} 的资金流向（{days}天）")
            
            # 1. 获取板块代码
            sector_code = self.sector_mapper.get_sector_code(sector_name)
            if not sector_code:
                # 特殊处理某些大概念板块
                if sector_name in ['新能源', '新能源板块']:
                    raise ValueError(f"'{sector_name}' 是一个大概念，请选择具体板块，如：光伏设备、风电设备、电池、汽车整车等")
                raise ValueError(f"无法找到板块 '{sector_name}' 的代码")
            
            # 2. 获取板块资金流向数据
            sector_data = self._get_sector_flow_data(sector_code, days)
            if sector_data.empty:
                raise ValueError(f"未找到板块 {sector_name} 的资金流向数据")
            
            # 3. 获取板块内股票资金流向
            stock_data = self._get_sector_stocks_flow(sector_name, days)
            
            # 4. 分析资金流向
            result = self._analyze_flow_pattern(sector_name, sector_code, sector_data, stock_data, days)
            
            self.logger.info(f"板块资金流向分析完成: {sector_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"板块资金流向分析失败: {e}")
            raise
    
    def _get_sector_flow_data(self, sector_code: str, days: int) -> pd.DataFrame:
        """获取板块资金流向数据"""
        # 获取最新交易日
        latest_date = get_latest_trading_day()
        if not latest_date:
            latest_date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算起始日期
        start_date = (datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            trade_date,
            name,
            ts_code,
            content_type,
            pct_change,
            close as sector_index,
            net_amount / 10000 as net_amount,          -- 转换为万元
            net_amount_rate,
            buy_elg_amount / 10000 as super_large_net, -- 超大单净流入
            buy_lg_amount / 10000 as large_net,        -- 大单净流入
            buy_md_amount / 10000 as medium_net,       -- 中单净流入
            buy_sm_amount / 10000 as small_net,        -- 小单净流入
            `rank` as sector_rank
        FROM tu_moneyflow_ind_dc
        WHERE ts_code = '{sector_code}'
        AND trade_date >= '{start_date}'
        AND trade_date <= '{latest_date}'
        -- 移除content_type限制，支持所有类型板块
        ORDER BY trade_date DESC
        """
        
        result = self.mysql.execute_query(query)
        return pd.DataFrame(result) if result else pd.DataFrame()
    
    def _get_sector_stocks_flow(self, sector_name: str, days: int) -> pd.DataFrame:
        """获取板块内股票的资金流向数据"""
        # 获取最新交易日
        latest_date = get_latest_trading_day()
        if not latest_date:
            latest_date = datetime.now().strftime('%Y-%m-%d')
        
        # 获取板块内的股票
        sector_stocks_query = f"""
        SELECT DISTINCT ts_code 
        FROM tu_stock_basic 
        WHERE industry = '{sector_name}'
        """
        stocks_result = self.mysql.execute_query(sector_stocks_query)
        
        if not stocks_result:
            return pd.DataFrame()
        
        stock_codes = [row['ts_code'] for row in stocks_result]
        stock_codes_str = "','".join(stock_codes)
        
        # 获取这些股票的资金流向数据
        query = f"""
        SELECT 
            mf.ts_code,
            sb.name as stock_name,
            SUM(mf.net_amount) as total_net_flow,
            AVG(d.pct_chg) as avg_pct_change,
            COUNT(DISTINCT mf.trade_date) as trading_days
        FROM tu_moneyflow_dc mf
        JOIN tu_stock_basic sb ON mf.ts_code = sb.ts_code
        LEFT JOIN tu_daily_detail d ON mf.ts_code = d.ts_code AND mf.trade_date = d.trade_date
        WHERE mf.ts_code IN ('{stock_codes_str}')
        AND mf.trade_date = '{latest_date}'
        GROUP BY mf.ts_code, sb.name
        ORDER BY total_net_flow DESC
        """
        
        result = self.mysql.execute_query(query)
        return pd.DataFrame(result) if result else pd.DataFrame()
    
    def _analyze_flow_pattern(self, sector_name: str, sector_code: str, 
                            sector_data: pd.DataFrame, stock_data: pd.DataFrame, 
                            days: int) -> SectorMoneyFlowResult:
        """分析资金流向模式"""
        if sector_data.empty:
            # 返回空结果
            return self._create_empty_result(sector_name, sector_code, days)
        
        # 计算板块整体指标
        total_net_flow = sector_data['net_amount'].sum()
        avg_daily_net_flow = sector_data['net_amount'].mean()
        
        # 计算流向趋势
        inflow_days = (sector_data['net_amount'] > 0).sum()
        outflow_days = (sector_data['net_amount'] < 0).sum()
        
        if inflow_days > outflow_days * 1.5:
            flow_trend = "持续净流入"
        elif outflow_days > inflow_days * 1.5:
            flow_trend = "持续净流出"
        else:
            flow_trend = "震荡"
        
        # 计算资金强度
        total_volume = abs(sector_data['net_amount']).sum()
        flow_strength = min(total_volume / (days * 10000), 1.0)  # 归一化
        
        # 计算一致性
        flow_consistency = inflow_days / len(sector_data) if len(sector_data) > 0 else 0.5
        
        # 资金分布
        super_large_net = sector_data['super_large_net'].sum()
        large_net = sector_data['large_net'].sum()
        medium_net = sector_data['medium_net'].sum()
        small_net = sector_data['small_net'].sum()
        
        # 板块表现
        latest_data = sector_data.iloc[0] if not sector_data.empty else None
        sector_pct_change = float(latest_data['pct_change']) if latest_data is not None else 0
        sector_rank = int(latest_data['sector_rank']) if latest_data is not None else 0
        
        # 个股分析
        if not stock_data.empty:
            total_stocks = len(stock_data)
            inflow_stocks = (stock_data['total_net_flow'] > 0).sum()
            outflow_stocks = (stock_data['total_net_flow'] < 0).sum()
            avg_stock_pct_change = stock_data['avg_pct_change'].mean()
            
            # 龙头股票（净流入前5）
            leader_stocks = []
            for _, row in stock_data.head(5).iterrows():
                leader_stocks.append({
                    'ts_code': row['ts_code'],
                    'name': row['stock_name'],
                    'net_flow': row['total_net_flow'],
                    'pct_change': row['avg_pct_change']
                })
        else:
            total_stocks = 0
            inflow_stocks = 0
            outflow_stocks = 0
            avg_stock_pct_change = 0
            leader_stocks = []
        
        # 综合评估
        overall_assessment = self._generate_assessment(
            total_net_flow, flow_trend, flow_strength, 
            flow_consistency, sector_rank
        )
        
        investment_suggestion = self._generate_suggestion(
            flow_trend, flow_strength, sector_rank,
            super_large_net, total_net_flow
        )
        
        risk_warning = self._generate_risk_warning(
            flow_consistency, flow_strength, sector_rank
        )
        
        return SectorMoneyFlowResult(
            sector_name=sector_name,
            sector_code=sector_code,
            analysis_period=f"{days}天",
            total_net_flow=round(total_net_flow, 2),
            avg_daily_net_flow=round(avg_daily_net_flow, 2),
            flow_trend=flow_trend,
            flow_strength=round(flow_strength, 3),
            flow_consistency=round(flow_consistency, 3),
            total_stocks=total_stocks,
            inflow_stocks=inflow_stocks,
            outflow_stocks=outflow_stocks,
            leader_stocks=leader_stocks,
            super_large_net_flow=round(super_large_net, 2),
            large_net_flow=round(large_net, 2),
            medium_net_flow=round(medium_net, 2),
            small_net_flow=round(small_net, 2),
            sector_pct_change=round(sector_pct_change, 2),
            avg_stock_pct_change=round(avg_stock_pct_change, 2),
            sector_rank=sector_rank,
            overall_assessment=overall_assessment,
            investment_suggestion=investment_suggestion,
            risk_warning=risk_warning
        )
    
    def _create_empty_result(self, sector_name: str, sector_code: str, days: int) -> SectorMoneyFlowResult:
        """创建空结果"""
        return SectorMoneyFlowResult(
            sector_name=sector_name,
            sector_code=sector_code,
            analysis_period=f"{days}天",
            total_net_flow=0,
            avg_daily_net_flow=0,
            flow_trend="无数据",
            flow_strength=0,
            flow_consistency=0,
            total_stocks=0,
            inflow_stocks=0,
            outflow_stocks=0,
            leader_stocks=[],
            super_large_net_flow=0,
            large_net_flow=0,
            medium_net_flow=0,
            small_net_flow=0,
            sector_pct_change=0,
            avg_stock_pct_change=0,
            sector_rank=0,
            overall_assessment="数据不足，无法分析",
            investment_suggestion="建议等待更多数据",
            risk_warning="数据缺失风险"
        )
    
    def _generate_assessment(self, total_net_flow: float, flow_trend: str,
                           flow_strength: float, flow_consistency: float,
                           sector_rank: int) -> str:
        """生成整体评估"""
        assessments = []
        
        # 资金流向评估
        if total_net_flow > 50000:
            assessments.append("板块资金大幅流入")
        elif total_net_flow > 10000:
            assessments.append("板块资金温和流入")
        elif total_net_flow < -50000:
            assessments.append("板块资金大幅流出")
        elif total_net_flow < -10000:
            assessments.append("板块资金温和流出")
        else:
            assessments.append("板块资金相对平衡")
        
        # 趋势评估
        assessments.append(f"呈现{flow_trend}态势")
        
        # 强度评估
        if flow_strength > 0.8:
            assessments.append("资金活跃度极高")
        elif flow_strength > 0.5:
            assessments.append("资金活跃度较高")
        else:
            assessments.append("资金活跃度一般")
        
        # 排名评估
        if sector_rank <= 5:
            assessments.append(f"板块排名第{sector_rank}，表现优异")
        elif sector_rank <= 10:
            assessments.append(f"板块排名第{sector_rank}，表现良好")
        
        return "；".join(assessments)
    
    def _generate_suggestion(self, flow_trend: str, flow_strength: float,
                           sector_rank: int, super_large_net: float,
                           total_net_flow: float) -> str:
        """生成投资建议"""
        if flow_trend == "持续净流入" and sector_rank <= 10:
            if super_large_net > 0 and super_large_net / total_net_flow > 0.5:
                return "板块获得超大资金青睐，建议积极关注龙头个股"
            else:
                return "板块资金面向好，可适度关注"
        elif flow_trend == "持续净流出":
            return "板块资金流出明显，建议谨慎观望"
        else:
            return "板块资金方向不明，建议等待趋势明朗"
    
    def _generate_risk_warning(self, flow_consistency: float, 
                             flow_strength: float, sector_rank: int) -> str:
        """生成风险提示"""
        warnings = []
        
        if flow_consistency < 0.4:
            warnings.append("资金流向一致性较差")
        
        if flow_strength < 0.3:
            warnings.append("板块交投清淡")
        
        if sector_rank > 20:
            warnings.append("板块排名靠后")
        
        if warnings:
            return "风险提示：" + "，".join(warnings)
        else:
            return "暂无明显风险信号"


def format_sector_money_flow_report(result: SectorMoneyFlowResult) -> str:
    """格式化板块资金流向分析报告"""
    report = f"""### {result.sector_name}（{result.sector_code}）板块资金流向分析报告

#### 1. 板块资金流向概况 ⭐⭐⭐
- **分析周期**: {result.analysis_period}
- **板块排名**: 第{result.sector_rank}名
- **总净流入**: {result.total_net_flow:,.0f}万元
- **日均净流入**: {result.avg_daily_net_flow:,.0f}万元
- **流向趋势**: {result.flow_trend}
- **资金强度**: {result.flow_strength:.1%}
- **一致性**: {result.flow_consistency:.1%}

#### 2. 板块内个股表现 ⭐⭐
- **板块涨跌幅**: {result.sector_pct_change:+.2f}%
- **个股平均涨幅**: {result.avg_stock_pct_change:+.2f}%
- **板块股票总数**: {result.total_stocks}只
- **净流入个股**: {result.inflow_stocks}只
- **净流出个股**: {result.outflow_stocks}只
"""

    # 添加龙头股票信息
    if result.leader_stocks:
        report += "\n#### 3. 资金流入龙头股 ⭐⭐\n"
        for i, stock in enumerate(result.leader_stocks[:5], 1):
            report += f"{i}. {stock['name']}（{stock['ts_code']}）: 净流入{stock['net_flow']:,.0f}万元\n"
    
    # 资金分布
    report += f"""
#### 4. 资金类型分布
- **超大单**: {result.super_large_net_flow:+,.0f}万元
- **大单**: {result.large_net_flow:+,.0f}万元
- **中单**: {result.medium_net_flow:+,.0f}万元
- **小单**: {result.small_net_flow:+,.0f}万元

#### 5. 综合分析
- **整体评估**: {result.overall_assessment}
- **投资建议**: {result.investment_suggestion}
- **{result.risk_warning}**
"""
    
    return report