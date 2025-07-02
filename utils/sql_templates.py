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
    
    # 指定日期的股价查询
    STOCK_PRICE_BY_DATE = """
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
            AND trade_date = :trade_date
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
    
    # 市值排名模板
    MARKET_CAP_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            b.total_mv,
            b.circ_mv,
            d.pct_chg,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
        ORDER BY b.total_mv DESC
        LIMIT :limit
    """
    
    # 涨跌幅排名模板
    PCT_CHG_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.pct_chg,
            d.vol,
            d.amount,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
            AND s.name NOT LIKE '%ST%'
        ORDER BY d.pct_chg DESC
        LIMIT :limit
    """
    
    # 跌幅排名模板（升序）
    PCT_CHG_RANKING_DESC = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.pct_chg,
            d.vol,
            d.amount,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
            AND s.name NOT LIKE '%ST%'
        ORDER BY d.pct_chg ASC
        LIMIT :limit
    """
    
    # 成交额排名模板
    AMOUNT_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.pct_chg,
            d.amount,
            d.vol,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
        ORDER BY d.amount DESC
        LIMIT :limit
    """
    
    # 成交量排名模板
    VOLUME_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.pct_chg,
            d.vol,
            d.amount,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
        ORDER BY d.vol DESC
        LIMIT :limit
    """
    
    # 流通市值排名模板（修正：ORDER BY circ_mv）
    CIRC_MV_RANKING = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            b.total_mv,
            b.circ_mv,
            d.pct_chg,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.trade_date = :trade_date
        ORDER BY b.circ_mv DESC
        LIMIT :limit
    """
    
    # 指定日期的成交量查询
    VOLUME_BY_DATE = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            d.pct_chg,
            d.vol,
            d.amount,
            b.turnover_rate,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        LEFT JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
        WHERE d.ts_code = :ts_code
            AND d.trade_date = :trade_date
        LIMIT 1
    """
    
    # 日期范围的K线查询
    KLINE_RANGE = """
        SELECT 
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
        ORDER BY trade_date ASC
    """
    
    # 主力净流入排行
    MAIN_FORCE_RANKING = """
        SELECT 
            m.ts_code,
            m.name,
            m.close,
            m.pct_change as pct_chg,
            m.net_amount,
            m.net_amount_rate,
            m.buy_elg_amount,
            m.buy_lg_amount,
            m.trade_date
        FROM tu_moneyflow_dc m
        WHERE m.trade_date = :trade_date
            AND m.name NOT LIKE '%ST%'
        ORDER BY m.net_amount DESC
        LIMIT :limit
    """
    
    # 个股资金流向查询
    STOCK_MONEY_FLOW = """
        SELECT 
            m.ts_code,
            m.name,
            m.trade_date,
            m.net_amount,
            m.net_amount_rate,
            m.buy_elg_amount,
            m.buy_elg_amount_rate,
            m.buy_lg_amount,
            m.buy_lg_amount_rate,
            m.buy_md_amount,
            m.buy_md_amount_rate,
            m.buy_sm_amount,
            m.buy_sm_amount_rate,
            m.close,
            m.pct_change,
            d.amount
        FROM tu_moneyflow_dc m
        JOIN tu_daily_detail d ON m.ts_code = d.ts_code AND m.trade_date = d.trade_date
        WHERE m.ts_code = :ts_code
            AND m.trade_date = :trade_date
        LIMIT 1
    """
    
    # 板块资金流向查询模板
    SECTOR_MONEY_FLOW = """
        SELECT 
            ts_code,
            name,
            content_type,
            trade_date,
            net_amount,
            buy_elg_amount,
            buy_lg_amount,
            buy_md_amount,
            buy_sm_amount,
            pct_change,
            buy_sm_amount_stock as top_inflow_stock,
            `rank`
        FROM tu_moneyflow_ind_dc
        WHERE name = :sector_name
            AND trade_date = :trade_date
        ORDER BY net_amount DESC
        LIMIT 1
    """
    
    # PE/PB查询模板
    VALUATION_METRICS = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            b.pe,
            b.pe_ttm,
            b.pb,
            b.ps,
            b.ps_ttm,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.ts_code = :ts_code
        ORDER BY d.trade_date DESC
        LIMIT 1
    """
    
    # 指定日期的估值指标查询
    VALUATION_METRICS_BY_DATE = """
        SELECT 
            d.ts_code,
            s.name,
            d.close,
            b.pe,
            b.pe_ttm,
            b.pb,
            b.ps,
            b.ps_ttm,
            d.trade_date
        FROM tu_daily_detail d
        JOIN tu_daily_basic b ON d.ts_code = b.ts_code AND d.trade_date = b.trade_date
        JOIN tu_stock_basic s ON d.ts_code = s.ts_code
        WHERE d.ts_code = :ts_code
            AND d.trade_date = :trade_date
        LIMIT 1
    """
    
    # 历史K线查询模板
    HISTORICAL_KLINE = """
        SELECT 
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
            AND trade_date >= :start_date
        ORDER BY trade_date DESC
        LIMIT :limit
    """
    
    # 板块股票查询模板
    SECTOR_STOCKS = """
        SELECT 
            s.ts_code,
            s.name,
            s.industry,
            d.close,
            d.pct_chg,
            b.total_mv
        FROM tu_stock_basic s
        JOIN tu_daily_detail d ON s.ts_code = d.ts_code
        JOIN tu_daily_basic b ON s.ts_code = b.ts_code AND d.trade_date = b.trade_date
        WHERE s.industry = :industry
            AND d.trade_date = :trade_date
        ORDER BY b.total_mv DESC
        LIMIT :limit
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
    def format_ranking_result(data: list, ranking_type: str) -> str:
        """格式化排名结果为Markdown表格"""
        if not data:
            return "未查询到相关排名数据"
            
        # 构建标题
        title_map = {
            'market_cap': '总市值排名',
            'circ_mv': '流通市值排名',
            'pct_chg': '涨跌幅排名',
            'amount': '成交额排名',
            'volume': '成交量排名'
        }
        title = title_map.get(ranking_type, '排名结果')
        
        # 构建Markdown表格
        lines = [f"## {title} - {data[0]['trade_date']}\n"]
        
        # 构建表头
        if ranking_type == 'market_cap':
            lines.append("| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 总市值(亿) |")
            lines.append("|------|----------|----------|----------|--------|------------|")
        elif ranking_type == 'circ_mv':
            lines.append("| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 流通市值(亿) |")
            lines.append("|------|----------|----------|----------|--------|--------------|")
        elif ranking_type == 'amount':
            lines.append("| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 成交额(亿) |")
            lines.append("|------|----------|----------|----------|--------|------------|")
        elif ranking_type == 'volume':
            lines.append("| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | 成交量(万手) |")
            lines.append("|------|----------|----------|----------|--------|--------------|")
        else:
            lines.append("| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 |")
            lines.append("|------|----------|----------|----------|--------|")
        
        # 构建数据行
        for i, row in enumerate(data, 1):
            if ranking_type == 'market_cap':
                total_mv = row['total_mv'] / 10000 if row.get('total_mv') else 0
                line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% | {total_mv:.2f} |"
            elif ranking_type == 'circ_mv':
                circ_mv = row['circ_mv'] / 10000 if row.get('circ_mv') else 0
                line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% | {circ_mv:.2f} |"
            elif ranking_type == 'amount':
                amount = row['amount'] / 100000000 if row.get('amount') else 0
                line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% | {amount:.2f} |"
            elif ranking_type == 'volume':
                volume = row['vol'] / 10000 if row.get('vol') else 0
                line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% | {volume:.2f} |"
            else:
                line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% |"
                
            lines.append(line)
            
        return "\n".join(lines)
    
    @staticmethod
    def format_valuation_result(data: Dict[str, Any], stock_name: str = None) -> str:
        """格式化估值指标结果"""
        if not data:
            return "未查询到相关估值数据"
            
        ts_code = data.get('ts_code', '')
        if stock_name:
            stock_info = f"{stock_name}（{ts_code}）"
        else:
            stock_info = ts_code
            
        return f"""{stock_info}在{data['trade_date']}的估值指标：
当前股价：{data['close']:.2f}元
市盈率(PE)：{data.get('pe', 0):.2f}
滚动市盈率(PE_TTM)：{data.get('pe_ttm', 0):.2f}
市净率(PB)：{data.get('pb', 0):.2f}
市销率(PS)：{data.get('ps', 0):.2f}
滚动市销率(PS_TTM)：{data.get('ps_ttm', 0):.2f}"""
    
    @staticmethod
    def format_volume_result(data: Dict[str, Any], stock_name: str = None) -> str:
        """格式化成交量结果"""
        if not data:
            return "未查询到相关成交数据"
            
        ts_code = data.get('ts_code', '')
        if stock_name:
            stock_info = f"{stock_name}（{ts_code}）"
        else:
            stock_info = ts_code
            
        # 转换单位
        vol_wan = data['vol'] / 10000 if data.get('vol') else 0
        amount_yi = data['amount'] / 100000000 if data.get('amount') else 0
        
        result = f"""{stock_info}在{data['trade_date']}的成交数据：
成交量：{vol_wan:.2f}万手
成交额：{amount_yi:.2f}亿元"""
        
        if data.get('turnover_rate'):
            result += f"\n换手率：{data['turnover_rate']:.2f}%"
        
        result += f"\n收盘价：{data['close']:.2f}元\n涨跌幅：{data['pct_chg']:.2f}%"
        
        return result
    
    @staticmethod
    def format_money_flow_result(data: Dict[str, Any], stock_name: str = None) -> str:
        """格式化资金流向结果"""
        if not data:
            return "未查询到相关资金流向数据"
            
        ts_code = data.get('ts_code', '')
        if stock_name:
            stock_info = stock_name
        else:
            stock_info = data.get('name', ts_code)
            
        # 直接使用净流入字段（已经是万元）
        net_amount = data.get('net_amount', 0)
        net_rate = data.get('net_amount_rate', 0)
        
        # 各级别净流入（已经是万元）
        elg_net = data.get('buy_elg_amount', 0)
        lg_net = data.get('buy_lg_amount', 0)
        md_net = data.get('buy_md_amount', 0)
        sm_net = data.get('buy_sm_amount', 0)
        
        # 各级别占比
        elg_rate = data.get('buy_elg_amount_rate', 0)
        lg_rate = data.get('buy_lg_amount_rate', 0)
        md_rate = data.get('buy_md_amount_rate', 0)
        sm_rate = data.get('buy_sm_amount_rate', 0)
        
        return f"""{stock_info}在{data['trade_date']}的资金流向：
主力净流入：{net_amount:.2f}万元（占比{net_rate:.2f}%）
  - 超大单净流入：{elg_net:.2f}万元（占比{elg_rate:.2f}%）
  - 大单净流入：{lg_net:.2f}万元（占比{lg_rate:.2f}%）
中单净流入：{md_net:.2f}万元（占比{md_rate:.2f}%）
小单净流入：{sm_net:.2f}万元（占比{sm_rate:.2f}%）

股价表现：
收盘价：{data.get('close', 0):.2f}元
涨跌幅：{data.get('pct_change', 0):.2f}%"""
    
    @staticmethod
    def format_money_flow_ranking(data: list, is_outflow: bool = False) -> str:
        """格式化主力净流入/流出排名结果为Markdown表格"""
        if not data:
            return "未查询到相关排名数据"
            
        title = "主力净流出排名" if is_outflow else "主力净流入排名"
        column_name = "主力净流出(万)" if is_outflow else "主力净流入(万)"
        
        # 构建Markdown表格
        lines = [f"## {title} - {data[0]['trade_date']}\n"]
        lines.append(f"| 排名 | 股票名称 | 股票代码 | 股价(元) | 涨跌幅 | {column_name} | 占比 |")
        lines.append("|------|----------|----------|----------|--------|--------------|------|")
        
        for i, row in enumerate(data, 1):
            # net_amount已经是万元为单位，直接使用
            net_mf = row.get('net_amount', 0)
            net_rate = row.get('net_amount_rate', 0)
            
            # 流出时取绝对值显示
            if is_outflow:
                net_mf = abs(net_mf)
            
            line = f"| {i} | {row['name']} | {row['ts_code']} | {row['close']:.2f} | {row['pct_chg']:.2f}% | {net_mf:.2f} | {net_rate:.2f}% |"
            lines.append(line)
            
        return "\n".join(lines)
    
    @staticmethod
    def get_template(query_type: str) -> Optional[str]:
        """根据查询类型获取SQL模板"""
        templates = {
            '最新股价': SQLTemplates.STOCK_PRICE_LATEST,
            '指定日期股价': SQLTemplates.STOCK_PRICE_BY_DATE,
            '历史股价': SQLTemplates.STOCK_PRICE_RANGE,
            '最新财务': SQLTemplates.FINANCIAL_LATEST,
            '资金流向': SQLTemplates.MONEY_FLOW_LATEST,
            '个股资金流向': SQLTemplates.STOCK_MONEY_FLOW,
            '主力净流入排行': SQLTemplates.MAIN_FORCE_RANKING,
            '最新公告': SQLTemplates.ANNOUNCEMENT_LATEST,
            '市值排名': SQLTemplates.MARKET_CAP_RANKING,
            '流通市值排名': SQLTemplates.CIRC_MV_RANKING,
            '涨幅排名': SQLTemplates.PCT_CHG_RANKING,
            '跌幅排名': SQLTemplates.PCT_CHG_RANKING_DESC,
            '成交额排名': SQLTemplates.AMOUNT_RANKING,
            '成交量查询': SQLTemplates.VOLUME_BY_DATE,
            '估值指标': SQLTemplates.VALUATION_METRICS,
            '指定日期估值': SQLTemplates.VALUATION_METRICS_BY_DATE,
            '历史K线': SQLTemplates.HISTORICAL_KLINE,
            'K线范围': SQLTemplates.KLINE_RANGE,
            '板块股票': SQLTemplates.SECTOR_STOCKS
        }
        return templates.get(query_type)