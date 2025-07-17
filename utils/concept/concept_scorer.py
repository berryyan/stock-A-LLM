#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念股评分计算器
基于多维度数据计算概念股综合得分
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConceptScorer:
    """概念股评分器"""
    
    def __init__(self):
        """初始化"""
        logger.info("ConceptScorer初始化完成")
    
    def calculate_scores(
        self,
        concept_stocks: List[Dict[str, Any]],
        technical_data: Dict[str, Dict[str, Any]],
        money_flow_data: Dict[str, Dict[str, Any]],
        weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        计算概念股综合得分
        
        Args:
            concept_stocks: 概念股列表
            technical_data: 技术指标数据
            money_flow_data: 资金流向数据
            weights: 评分权重配置
            
        Returns:
            包含得分的股票列表，按总分降序排列
        """
        scored_stocks = []
        
        for stock in concept_stocks:
            ts_code = stock['ts_code']
            
            # 获取该股票的技术和资金数据
            tech = technical_data.get(ts_code, {})
            money = money_flow_data.get(ts_code, {})
            
            # 计算三个维度得分
            concept_score = self._calculate_concept_score(stock)
            money_score = self._calculate_money_flow_score(money)
            technical_score = self._calculate_technical_score(tech)
            
            # 计算总分
            total_score = (
                concept_score * weights.get('concept_relevance', 0.4) +
                money_score * weights.get('money_flow', 0.3) +
                technical_score * weights.get('technical', 0.3)
            )
            
            # 组装结果
            scored_stock = stock.copy()
            scored_stock.update({
                'concept_score': concept_score,
                'money_score': money_score,
                'technical_score': technical_score,
                'total_score': total_score,
                'score_details': {
                    'concept': self._get_concept_score_details(stock),
                    'money_flow': self._get_money_score_details(money),
                    'technical': self._get_technical_score_details(tech)
                }
            })
            
            scored_stocks.append(scored_stock)
        
        # 按总分降序排序
        scored_stocks.sort(key=lambda x: x['total_score'], reverse=True)
        
        logger.info(f"完成 {len(scored_stocks)} 只股票的评分计算")
        
        return scored_stocks
    
    def _calculate_concept_score(self, stock: Dict[str, Any]) -> float:
        """
        计算概念关联度得分（满分40）
        
        评分规则：
        - 在成分股表中: 10分
        - 板块率先涨停: 10分（最近5天前3个）
        - 财报提及: 5分
        - 互动平台提及: 5分
        - 公告提及: 5分
        - 板块活跃度: 5分（涨幅前20%）
        """
        score = 0
        
        # 1. 在成分股表中（基础分）
        if stock.get('data_source'):
            score += 10
        
        # 2. 板块率先涨停
        if stock.get('first_limit_date'):
            # TODO: 判断是否在板块前3个涨停
            score += 10
        
        # 3. 财报提及
        if stock.get('financial_report_mention'):
            score += 5
        
        # 4. 互动平台提及
        if stock.get('interaction_mention'):
            score += 5
        
        # 5. 公告提及
        if stock.get('announcement_mention'):
            score += 5
        
        # 6. 板块活跃度
        if stock.get('sector_rank_pct', 1.0) <= 0.2:
            score += 5
        
        return min(score, 40)  # 确保不超过40分
    
    def _calculate_money_flow_score(self, money_data: Dict[str, Any]) -> float:
        """
        计算资金流向得分（满分30）
        
        评分规则：
        - 日周双净流入: 10分（日5分+周5分）
        - 净流入排名: 10分（前10%:10分, 前30%:7分, 前50%:5分）
        - 板块资金表现: 5分
        - 连续净流入: 5分（5天:5分, 3天:3分）
        """
        score = 0
        
        if not money_data:
            return score
        
        # 1. 日周双净流入
        if money_data.get('daily_net_inflow', 0) > 0:
            score += 5
        if money_data.get('weekly_net_inflow', 0) > 0:
            score += 5
        
        # 2. 净流入排名
        net_inflow_pct = money_data.get('net_inflow_pct', 0)
        if net_inflow_pct >= 0.9:  # 前10%
            score += 10
        elif net_inflow_pct >= 0.7:  # 前30%
            score += 7
        elif net_inflow_pct >= 0.5:  # 前50%
            score += 5
        
        # 3. 板块资金表现
        # TODO: 需要板块整体资金数据
        score += 2.5  # 暂时给中间分
        
        # 4. 连续净流入
        continuous_days = money_data.get('continuous_inflow_days', 0)
        if continuous_days >= 5:
            score += 5
        elif continuous_days >= 3:
            score += 3
        
        return min(score, 30)  # 确保不超过30分
    
    def _calculate_technical_score(self, tech_data: Dict[str, Any]) -> float:
        """
        计算技术形态得分（满分30）
        
        评分规则：
        - MACD状态: 15分
          - MACD水上红柱(MACD>0 AND DIF>0): 10分
          - 板块内率先水上(最近2天): 5分
        - 均线排列: 15分
          - MA5>MA10: 15分
        """
        score = 0
        
        if not tech_data:
            return score
        
        # 1. MACD状态
        macd = tech_data.get('latest_macd', 0)
        dif = tech_data.get('latest_dif', 0)
        
        # MACD水上红柱
        if macd > 0 and dif > 0:
            score += 10
        
        # 板块内率先水上
        if tech_data.get('macd_above_water_date'):
            # TODO: 判断是否最近2天内
            score += 5
        
        # 2. 均线排列
        ma5 = tech_data.get('ma5', 0)
        ma10 = tech_data.get('ma10', 0)
        
        if ma5 > ma10 and ma5 > 0 and ma10 > 0:
            score += 15
        
        return min(score, 30)  # 确保不超过30分
    
    def _get_concept_score_details(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """获取概念关联度得分详情"""
        return {
            "is_member": bool(stock.get('data_source')),
            "first_limit": bool(stock.get('first_limit_date')),
            "financial_mention": stock.get('financial_report_mention', False),
            "interaction_mention": stock.get('interaction_mention', False),
            "announcement_mention": stock.get('announcement_mention', False),
            "sector_active": stock.get('sector_rank_pct', 1.0) <= 0.2
        }
    
    def _get_money_score_details(self, money_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取资金流向得分详情"""
        if not money_data:
            return {}
        
        return {
            "daily_inflow": money_data.get('daily_net_inflow', 0) > 0,
            "weekly_inflow": money_data.get('weekly_net_inflow', 0) > 0,
            "rank_percentile": money_data.get('net_inflow_pct', 0),
            "continuous_days": money_data.get('continuous_inflow_days', 0)
        }
    
    def _get_technical_score_details(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取技术形态得分详情"""
        if not tech_data:
            return {}
        
        macd = tech_data.get('latest_macd', 0)
        dif = tech_data.get('latest_dif', 0)
        ma5 = tech_data.get('ma5', 0)
        ma10 = tech_data.get('ma10', 0)
        
        return {
            "macd_above_water": macd > 0 and dif > 0,
            "macd_value": macd,
            "dif_value": dif,
            "ma5_gt_ma10": ma5 > ma10 and ma5 > 0 and ma10 > 0,
            "ma5": ma5,
            "ma10": ma10
        }
    
    def filter_by_score(
        self,
        scored_stocks: List[Dict[str, Any]],
        min_total_score: float = 50,
        min_concept_score: float = None,
        min_money_score: float = None,
        min_technical_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        根据得分过滤股票
        
        Args:
            scored_stocks: 已评分的股票列表
            min_total_score: 最低总分要求
            min_concept_score: 最低概念关联度要求
            min_money_score: 最低资金流向得分要求
            min_technical_score: 最低技术形态得分要求
            
        Returns:
            符合条件的股票列表
        """
        filtered = []
        
        for stock in scored_stocks:
            # 检查总分
            if stock['total_score'] < min_total_score:
                continue
            
            # 检查各维度得分
            if min_concept_score and stock['concept_score'] < min_concept_score:
                continue
            
            if min_money_score and stock['money_score'] < min_money_score:
                continue
            
            if min_technical_score and stock['technical_score'] < min_technical_score:
                continue
            
            filtered.append(stock)
        
        return filtered


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scorer = ConceptScorer()
    
    # 模拟数据
    test_stocks = [
        {
            'ts_code': '000001.SZ',
            'name': '平安银行',
            'concepts': ['金融科技', '银行'],
            'data_source': ['THS', 'DC'],
            'first_limit_date': '2025-07-10'
        },
        {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒'],
            'data_source': ['THS'],
            'first_limit_date': None
        }
    ]
    
    test_tech = {
        '000001.SZ': {
            'latest_macd': 0.15,
            'latest_dif': 0.20,
            'ma5': 12.5,
            'ma10': 12.3
        },
        '600519.SH': {
            'latest_macd': -0.05,
            'latest_dif': -0.10,
            'ma5': 1800,
            'ma10': 1850
        }
    }
    
    test_money = {
        '000001.SZ': {
            'daily_net_inflow': 5000000,
            'weekly_net_inflow': 25000000,
            'continuous_inflow_days': 4,
            'net_inflow_pct': 0.85
        },
        '600519.SH': {
            'daily_net_inflow': -10000000,
            'weekly_net_inflow': -50000000,
            'continuous_inflow_days': 0,
            'net_inflow_pct': 0.15
        }
    }
    
    # 计算得分
    weights = {
        'concept_relevance': 0.4,
        'money_flow': 0.3,
        'technical': 0.3
    }
    
    scored = scorer.calculate_scores(test_stocks, test_tech, test_money, weights)
    
    # 打印结果
    for stock in scored:
        print(f"\n{stock['name']}({stock['ts_code']})")
        print(f"  总分: {stock['total_score']:.1f}")
        print(f"  概念关联: {stock['concept_score']:.1f}/40")
        print(f"  资金流向: {stock['money_score']:.1f}/30")
        print(f"  技术形态: {stock['technical_score']:.1f}/30")