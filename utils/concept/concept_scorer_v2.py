#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念股评分计算器 V2
基于证据的多维度评分系统，完全实现原始设计
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

# 添加项目根目录到Python路径
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.concept.evidence_collector import EvidenceCollector

logger = logging.getLogger(__name__)


class ConceptScorerV2:
    """概念股评分器V2 - 基于证据系统"""
    
    def __init__(self):
        """初始化"""
        self.evidence_collector = EvidenceCollector()
        logger.info("ConceptScorerV2初始化完成")
    
    def calculate_scores_with_evidence(
        self,
        concept_stocks: List[Dict[str, Any]],
        technical_data: Dict[str, Dict[str, Any]],
        money_flow_data: Dict[str, Dict[str, Any]],
        weights: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        基于证据计算概念股综合得分
        
        Args:
            concept_stocks: 概念股列表
            technical_data: 技术指标数据
            money_flow_data: 资金流向数据
            weights: 评分权重配置（可选）
            
        Returns:
            包含得分和证据的股票列表，按总分降序排列
        """
        # 默认权重：原始设计的权重
        if weights is None:
            weights = {
                'evidence': 1.0,      # 证据系统占100%（原始设计）
                'technical': 0.0,     # 技术指标暂时不计入
                'money_flow': 0.0     # 资金流向暂时不计入
            }
        
        scored_stocks = []
        
        for i, stock in enumerate(concept_stocks):
            ts_code = stock['ts_code']
            
            logger.info(f"处理股票 {i+1}/{len(concept_stocks)}: {ts_code} {stock.get('name', '')}")
            
            # 1. 收集证据
            concepts = stock.get('concepts', [])
            if not concepts:
                # 从stock中提取概念
                concepts = [stock.get('concept', '')]
            
            evidence = self.evidence_collector.collect_evidence(
                ts_code=ts_code,
                concepts=concepts,
                data_sources=stock.get('data_source', [])
            )
            
            # 2. 计算证据得分（原始设计的4维度）
            evidence_scores = self.evidence_collector.calculate_total_score(evidence)
            concept_score = evidence_scores['total']  # 满分100
            
            # 3. 获取技术和资金数据（备用）
            tech = technical_data.get(ts_code, {})
            money = money_flow_data.get(ts_code, {})
            
            # 4. 计算其他维度得分（如果需要）
            technical_score = self._calculate_technical_score(tech) if weights.get('technical', 0) > 0 else 0
            money_score = self._calculate_money_flow_score(money) if weights.get('money_flow', 0) > 0 else 0
            
            # 5. 计算总分
            total_score = (
                concept_score * weights.get('evidence', 1.0) +
                technical_score * weights.get('technical', 0.0) +
                money_score * weights.get('money_flow', 0.0)
            )
            
            # 6. 组装结果
            scored_stock = stock.copy()
            scored_stock.update({
                # 证据相关
                'evidence': evidence,
                'evidence_list': self.evidence_collector.flatten_evidence(evidence),
                'evidence_scores': evidence_scores,
                
                # 各维度得分
                'concept_score': concept_score,
                'technical_score': technical_score,
                'money_score': money_score,
                'total_score': total_score,
                
                # 详细信息
                'score_details': {
                    'evidence': evidence_scores,
                    'technical': self._get_technical_score_details(tech),
                    'money_flow': self._get_money_score_details(money)
                },
                
                # 关联强度分级
                'relevance_level': self._get_relevance_level(concept_score)
            })
            
            scored_stocks.append(scored_stock)
        
        # 按总分降序排序
        scored_stocks.sort(key=lambda x: x['total_score'], reverse=True)
        
        logger.info(f"完成 {len(scored_stocks)} 只股票的评分计算")
        
        return scored_stocks
    
    def _get_relevance_level(self, score: float) -> str:
        """
        根据得分获取关联强度等级
        
        基于原始设计：
        - 核心概念股（80-100分）：多维度强关联
        - 重要概念股（60-79分）：有明确业务关联
        - 相关概念股（40-59分）：有一定关联
        - 边缘概念股（20-39分）：弱关联
        - 无关股票（0-19分）：基本无关
        """
        if score >= 80:
            return "核心概念股"
        elif score >= 60:
            return "重要概念股"
        elif score >= 40:
            return "相关概念股"
        elif score >= 20:
            return "边缘概念股"
        else:
            return "无关股票"
    
    def _calculate_technical_score(self, tech_data: Dict[str, Any]) -> float:
        """
        计算技术形态得分（备用，满分100）
        
        当需要结合技术指标时使用
        """
        if not tech_data:
            return 0
        
        score = 0
        
        # MACD状态（40分）
        macd = tech_data.get('latest_macd', 0)
        dif = tech_data.get('latest_dif', 0)
        
        if macd > 0 and dif > 0:
            score += 40
        elif dif > tech_data.get('latest_dea', 0):
            score += 20
        
        # 均线排列（30分）
        ma5 = tech_data.get('ma5', 0)
        ma10 = tech_data.get('ma10', 0)
        ma20 = tech_data.get('ma20', 0)
        
        if ma5 > 0 and ma10 > 0 and ma20 > 0:
            if ma5 > ma10 > ma20:
                score += 30  # 多头排列
            elif ma5 > ma10:
                score += 15
        
        # RSI状态（15分）
        rsi = tech_data.get('rsi_14', 50)
        if 40 <= rsi <= 60:
            score += 15  # 中性区间
        elif 60 < rsi <= 70:
            score += 10  # 强势但未超买
        
        # KDJ状态（15分）
        k = tech_data.get('k', 50)
        d = tech_data.get('d', 50)
        if k > d and k < 80:
            score += 15  # 金叉且未超买
        elif k > d:
            score += 8
        
        return min(score, 100)
    
    def _calculate_money_flow_score(self, money_data: Dict[str, Any]) -> float:
        """
        计算资金流向得分（备用，满分100）
        
        当需要结合资金流向时使用
        """
        if not money_data:
            return 0
        
        score = 0
        
        # 日净流入（30分）
        if money_data.get('daily_net_inflow', 0) > 0:
            score += 30
        
        # 周净流入（30分）
        if money_data.get('weekly_net_inflow', 0) > 0:
            score += 30
        
        # 净流入排名（20分）
        net_inflow_pct = money_data.get('net_inflow_pct', 0)
        if net_inflow_pct >= 0.8:  # 前20%
            score += 20
        elif net_inflow_pct >= 0.6:  # 前40%
            score += 10
        
        # 连续净流入（20分）
        continuous_days = money_data.get('continuous_inflow_days', 0)
        if continuous_days >= 5:
            score += 20
        elif continuous_days >= 3:
            score += 10
        
        return min(score, 100)
    
    def _get_technical_score_details(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取技术形态得分详情"""
        if not tech_data:
            return {}
        
        return {
            "macd": tech_data.get('latest_macd', 0),
            "dif": tech_data.get('latest_dif', 0),
            "dea": tech_data.get('latest_dea', 0),
            "ma5": tech_data.get('ma5', 0),
            "ma10": tech_data.get('ma10', 0),
            "ma20": tech_data.get('ma20', 0),
            "rsi": tech_data.get('rsi_14', 0),
            "k": tech_data.get('k', 0),
            "d": tech_data.get('d', 0)
        }
    
    def _get_money_score_details(self, money_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取资金流向得分详情"""
        if not money_data:
            return {}
        
        return {
            "daily_net_inflow": money_data.get('daily_net_inflow', 0),
            "weekly_net_inflow": money_data.get('weekly_net_inflow', 0),
            "net_inflow_pct": money_data.get('net_inflow_pct', 0),
            "continuous_inflow_days": money_data.get('continuous_inflow_days', 0)
        }
    
    def format_evidence_report(self, stock: Dict[str, Any]) -> str:
        """
        格式化证据报告
        
        Args:
            stock: 包含证据的股票信息
            
        Returns:
            格式化的证据报告字符串
        """
        lines = [
            f"## {stock['name']}({stock['ts_code']}) - 概念关联证据分析\n",
            f"**关联强度**: {stock['relevance_level']} (总分: {stock['concept_score']}/100)\n"
        ]
        
        # 按证据类型分组展示
        evidence = stock.get('evidence', {})
        
        # 1. 软件收录证据
        if evidence.get('software'):
            lines.append("### 1. 软件收录证据")
            for ev in evidence['software']:
                lines.append(f"- **{ev['source']}**: {ev['content']} (得分: {ev['score']}分)")
            lines.append("")
        
        # 2. 财报证据
        if evidence.get('report'):
            lines.append("### 2. 财报证据")
            for ev in evidence['report']:
                lines.append(f"- **{ev['source']}**: {ev['content']} (得分: {ev['score']}分)")
            lines.append("")
        
        # 3. 互动平台证据
        if evidence.get('interaction'):
            lines.append("### 3. 互动平台证据")
            for ev in evidence['interaction']:
                if ev.get('negative'):
                    lines.append(f"- **{ev['source']}** [{ev['date']}]: {ev['content']} (否定证据)")
                else:
                    lines.append(f"- **{ev['source']}** [{ev['date']}]: {ev['content']} (得分: {ev['score']}分)")
            lines.append("")
        
        # 4. 公告证据
        if evidence.get('announcement'):
            lines.append("### 4. 公告证据")
            for ev in evidence['announcement']:
                lines.append(f"- **{ev['source']}**: {ev['content']} (得分: {ev['score']}分)")
            lines.append("")
        
        # 得分明细
        scores = stock.get('evidence_scores', {})
        lines.append("### 得分明细")
        lines.append(f"- 软件收录: {scores.get('software', 0)}/40分")
        lines.append(f"- 财报证据: {scores.get('report', 0)}/30分")
        lines.append(f"- 互动平台: {scores.get('interaction', 0)}/20分")
        lines.append(f"- 公告证据: {scores.get('announcement', 0)}/10分")
        lines.append(f"- **总分**: {scores.get('total', 0)}/100分")
        
        return '\n'.join(lines)
    
    def filter_by_relevance(
        self,
        scored_stocks: List[Dict[str, Any]],
        min_level: str = "边缘概念股"
    ) -> List[Dict[str, Any]]:
        """
        根据关联强度过滤股票
        
        Args:
            scored_stocks: 已评分的股票列表
            min_level: 最低关联强度要求
            
        Returns:
            符合条件的股票列表
        """
        level_scores = {
            "无关股票": 0,
            "边缘概念股": 20,
            "相关概念股": 40,
            "重要概念股": 60,
            "核心概念股": 80
        }
        
        min_score = level_scores.get(min_level, 20)
        
        return [
            stock for stock in scored_stocks
            if stock['concept_score'] >= min_score
        ]
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'evidence_collector'):
            del self.evidence_collector


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scorer = ConceptScorerV2()
    
    # 测试股票
    test_stocks = [
        {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒', '消费'],
            'data_source': ['THS', 'DC']
        }
    ]
    
    # 评分
    scored = scorer.calculate_scores_with_evidence(
        test_stocks,
        technical_data={},
        money_flow_data={}
    )
    
    # 打印结果
    for stock in scored:
        print(scorer.format_evidence_report(stock))