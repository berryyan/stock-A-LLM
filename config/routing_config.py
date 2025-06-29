#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路由配置文件
包含触发词、模式匹配等路由相关配置
"""

from typing import Dict, List


class RoutingConfig:
    """路由配置类"""
    
    # 触发词映射配置
    TRIGGER_WORDS = {
        "排行分析：": "rank",
        "查询公告：": "anns", 
        "董秘互动：": "qa"
    }
    
    # Agent职责描述
    AGENT_DESCRIPTIONS = {
        "sql": "基础数据查询（股价、简单财务指标、基础统计）",
        "rag": "文档内容搜索（公告内容、管理层分析、定性信息）",
        "financial": "专业财务分析（财务健康度、杜邦分析、现金流质量）",
        "money_flow": "资金流向分析（主力资金、超大单、资金分布）",
        "rank": "专业排名分析（涨跌幅榜、市值榜、板块排名、ST过滤）",
        "anns": "公告元数据查询（公告列表、发布时间、公告类型）",
        "qa": "董秘互动查询（投资者提问、公司回复、互动记录）"
    }
    
    # 模板路由调整映射（用于修正现有模板的路由目标）
    TEMPLATE_ROUTE_OVERRIDE = {
        "涨幅排名": "rank",      # 原本是SQL_ONLY，改为rank
        "市值排名": "rank",      # 原本是SQL_ONLY，改为rank
        "总市值排名": "rank",    # 原本是SQL_ONLY，改为rank
        "流通市值排名": "rank",  # 原本是SQL_ONLY，改为rank
        "最新公告": "anns",      # 当查询公告列表时路由到anns
    }
    
    # 区分简单查询和专业分析的关键词
    PROFESSIONAL_KEYWORDS = {
        "rank": ["排行榜", "龙虎榜", "涨跌榜", "排除ST", "板块排名", "行业排名"],
        "anns": ["公告列表", "最新公告", "公告时间", "公告类型"],
        "sql": ["最新股价", "今日股价", "成交量", "市盈率", "市净率"]
    }


# 创建全局配置实例
routing_config = RoutingConfig()