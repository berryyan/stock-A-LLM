#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念股评分配置模块
提供灵活的评分权重和规则配置
"""

from typing import Dict, Any
import json
import os


class ScoringConfig:
    """评分配置管理器"""
    
    # 默认评分权重
    DEFAULT_WEIGHTS = {
        "concept_relevance": 0.4,  # 概念关联度 40%
        "money_flow": 0.3,         # 资金流向 30%
        "technical": 0.3           # 技术形态 30%
    }
    
    # 概念关联度评分细则（总分40）
    CONCEPT_SCORING = {
        "is_member": 10,           # 在成分股表中
        "first_limit_up": 10,      # 板块率先涨停（最近5天前3个）
        "financial_report": 5,     # 财报提及
        "interaction": 5,          # 互动平台提及
        "announcement": 5,         # 公告提及
        "sector_active": 5         # 板块活跃度（涨幅前20%）
    }
    
    # 资金流向评分细则（总分30）
    MONEY_FLOW_SCORING = {
        "daily_weekly_inflow": {   # 日周双净流入（10分）
            "daily_inflow": 5,
            "weekly_inflow": 5
        },
        "rank_in_concept": {       # 概念内排名（10分）
            "top_10_percent": 10,
            "top_30_percent": 7,
            "top_50_percent": 5
        },
        "sector_performance": 5,   # 板块资金表现
        "continuous_inflow": {     # 连续净流入（5分）
            "5_days": 5,
            "3_days": 3
        }
    }
    
    # 技术形态评分细则（总分30）
    TECHNICAL_SCORING = {
        "macd": {                  # MACD状态（15分）
            "above_water": 10,     # MACD>0 AND DIF>0
            "first_above": 5       # 板块内率先水上（最近2天）
        },
        "ma_arrangement": {        # 均线排列（15分）
            "ma5_gt_ma10": 15,    # MA5>MA10
            "ma5_gt_ma10_gt_ma20": 0  # 可选：完美多头排列（暂不使用）
        }
    }
    
    def __init__(self, config_file: str = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径，如果提供则从文件加载配置
        """
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self.concept_scoring = self.CONCEPT_SCORING.copy()
        self.money_flow_scoring = self.MONEY_FLOW_SCORING.copy()
        self.technical_scoring = self.TECHNICAL_SCORING.copy()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        """从文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新权重
            if 'weights' in config:
                self.weights.update(config['weights'])
            
            # 更新各项评分规则
            if 'concept_scoring' in config:
                self.concept_scoring.update(config['concept_scoring'])
            
            if 'money_flow_scoring' in config:
                self._update_nested_dict(self.money_flow_scoring, config['money_flow_scoring'])
            
            if 'technical_scoring' in config:
                self._update_nested_dict(self.technical_scoring, config['technical_scoring'])
                
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}, 使用默认配置")
    
    def _update_nested_dict(self, target: dict, source: dict):
        """递归更新嵌套字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_nested_dict(target[key], value)
            else:
                target[key] = value
    
    def get_weights(self) -> Dict[str, float]:
        """获取评分权重"""
        return self.weights.copy()
    
    def get_concept_rules(self) -> Dict[str, Any]:
        """获取概念关联度评分规则"""
        return self.concept_scoring.copy()
    
    def get_money_flow_rules(self) -> Dict[str, Any]:
        """获取资金流向评分规则"""
        return self.money_flow_scoring.copy()
    
    def get_technical_rules(self) -> Dict[str, Any]:
        """获取技术形态评分规则"""
        return self.technical_scoring.copy()
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        更新评分权重
        
        Args:
            new_weights: 新的权重配置
        """
        # 验证权重和为1
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"权重总和必须为1，当前为{total}")
        
        self.weights.update(new_weights)
    
    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        config = {
            "weights": self.weights,
            "concept_scoring": self.concept_scoring,
            "money_flow_scoring": self.money_flow_scoring,
            "technical_scoring": self.technical_scoring
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def validate_config(self) -> bool:
        """验证配置的合理性"""
        # 验证权重
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.001:
            return False
        
        # 验证概念关联度总分
        concept_total = sum(self.concept_scoring.values())
        if concept_total != 40:
            return False
        
        # 验证资金流向总分
        money_total = (
            sum(self.money_flow_scoring["daily_weekly_inflow"].values()) +
            max(self.money_flow_scoring["rank_in_concept"].values()) +
            self.money_flow_scoring["sector_performance"] +
            max(self.money_flow_scoring["continuous_inflow"].values())
        )
        if money_total != 30:
            return False
        
        # 验证技术形态总分
        tech_total = (
            sum(self.technical_scoring["macd"].values()) +
            self.technical_scoring["ma_arrangement"]["ma5_gt_ma10"]
        )
        if tech_total != 30:
            return False
        
        return True


# 测试
if __name__ == "__main__":
    # 创建默认配置
    config = ScoringConfig()
    
    # 验证配置
    print(f"配置验证: {config.validate_config()}")
    
    # 打印默认权重
    print("\n默认权重:")
    for key, value in config.get_weights().items():
        print(f"  {key}: {value}")
    
    # 打印概念关联度规则
    print("\n概念关联度评分规则:")
    for key, value in config.get_concept_rules().items():
        print(f"  {key}: {value}分")
    
    # 保存配置到文件
    config.save_to_file("concept_scoring_config.json")
    print("\n配置已保存到 concept_scoring_config.json")