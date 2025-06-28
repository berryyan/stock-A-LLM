#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL查询模板库
用于常见查询的快速执行，避免LLM生成
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class SQLTemplates:
    """SQL模板管理器"""
    
    # 股价查询模板
    STOCK_PRICE_LATEST = """
        SELECT 
            ts_code,
            trade_date,
            open,
            high,
            low,
            close,
            vol,
            amount,
            pct_chg
        FROM tu_daily_detail
        WHERE ts_code = :ts_code
        ORDER BY trade_date DESC
        LIMIT 1
    """
    
    STOCK_PRICE_RANGE = """
        SELECT 
            ts_code,
            trade_date,
            open,
            high,
            low,
            close,
            vol,
            amount,
            pct_chg
        FROM tu_daily_detail
        WHERE ts_code = :ts_code
            AND trade_date BETWEEN :start_date AND :end_date
        ORDER BY trade_date DESC
    """
    
    # 财务数据查询模板
    FINANCIAL_LATEST = """
        SELECT 
            i.ts_code,
            i.end_date,
            i.revenue,
            i.n_income,
            i.n_income_attr_p,
            b.total_assets,
            b.total_liab,
            f.roe,
            f.roa,
            f.debt_to_assets
        FROM tu_income i
        JOIN tu_balancesheet b ON i.ts_code = b.ts_code AND i.end_date = b.end_date
        JOIN tu_fina_indicator f ON i.ts_code = f.ts_code AND i.end_date = f.end_date
        WHERE i.ts_code = :ts_code
        ORDER BY i.end_date DESC
        LIMIT 1
    """
    
    # 资金流向查询模板
    MONEY_FLOW_LATEST = """
        SELECT 
            ts_code,
            trade_date,
            buy_elg_vol,
            sell_elg_vol,
            buy_lg_vol,
            sell_lg_vol,
            buy_md_vol,
            sell_md_vol,
            buy_sm_vol,
            sell_sm_vol,
            net_mf_vol
        FROM tu_moneyflow_dc
        WHERE ts_code = :ts_code
        ORDER BY trade_date DESC
        LIMIT :days
    """
    
    # 公告查询模板
    ANNOUNCEMENT_LATEST = """
        SELECT 
            ts_code,
            ann_date,
            title,
            type
        FROM tu_anns_d
        WHERE ts_code = :ts_code
        ORDER BY ann_date DESC
        LIMIT 10
    """
    
    @staticmethod
    def format_stock_price_result(data: Dict[str, Any], stock_name: str = None) -> str:
        """格式化股价查询结果"""
        if not data:
            return "未查询到相关股价数据"
            
        ts_code = data.get('ts_code', '')
        if stock_name:
            stock_info = f"{stock_name}（{ts_code}）"
        else:
            stock_info = ts_code
            
        return f"""{stock_info}在{data['trade_date']}的股价信息：
开盘价：{data['open']:.2f}元
最高价：{data['high']:.2f}元
最低价：{data['low']:.2f}元
收盘价：{data['close']:.2f}元
成交量：{data['vol']/10000:.2f}万手
成交额：{data['amount']/10000:.2f}万元
涨跌幅：{data['pct_chg']:.2f}%"""
    
    @staticmethod
    def format_financial_result(data: Dict[str, Any], stock_name: str = None) -> str:
        """格式化财务数据结果"""
        if not data:
            return "未查询到相关财务数据"
            
        ts_code = data.get('ts_code', '')
        if stock_name:
            stock_info = f"{stock_name}（{ts_code}）"
        else:
            stock_info = ts_code
            
        # 转换单位
        revenue_yi = data['revenue'] / 100000000 if data.get('revenue') else 0
        income_yi = data['n_income'] / 100000000 if data.get('n_income') else 0
        assets_yi = data['total_assets'] / 100000000 if data.get('total_assets') else 0
        liab_yi = data['total_liab'] / 100000000 if data.get('total_liab') else 0
        
        return f"""{stock_info}最新财务数据（{data['end_date']}）：
营业收入：{revenue_yi:.2f}亿元
净利润：{income_yi:.2f}亿元
总资产：{assets_yi:.2f}亿元
总负债：{liab_yi:.2f}亿元
净资产收益率(ROE)：{data.get('roe', 0):.2f}%
总资产收益率(ROA)：{data.get('roa', 0):.2f}%
资产负债率：{data.get('debt_to_assets', 0):.2f}%"""
    
    @staticmethod
    def get_template(query_type: str) -> Optional[str]:
        """根据查询类型获取SQL模板"""
        templates = {
            '最新股价': SQLTemplates.STOCK_PRICE_LATEST,
            '历史股价': SQLTemplates.STOCK_PRICE_RANGE,
            '最新财务': SQLTemplates.FINANCIAL_LATEST,
            '资金流向': SQLTemplates.MONEY_FLOW_LATEST,
            '最新公告': SQLTemplates.ANNOUNCEMENT_LATEST
        }
        return templates.get(query_type)