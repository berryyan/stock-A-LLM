"""
Hybrid Agent 模块化版本
包含复合查询路由修复
"""

from agents.hybrid_agent_fixed import HybridAgentFixed


class HybridAgentModular(HybridAgentFixed):
    """
    Hybrid Agent 模块化版本
    继承自修复版本，包含复合查询路由修复
    """
    
    def __init__(self):
        """初始化模块化Hybrid Agent"""
        super().__init__()
        self.logger.info("使用模块化Hybrid Agent（包含路由修复）")
    
    def query(self, question: str, context=None):
        """
        执行查询
        使用修复后的路由逻辑
        """
        self.logger.info(f"模块化Hybrid Agent处理查询: {question}")
        return super().query(question, context)