"""
Hybrid Agent 模块化版本
暂时作为原版本的包装器，确保测试能正常运行
"""

from agents.hybrid_agent import HybridAgent


class HybridAgentModular(HybridAgent):
    """
    Hybrid Agent 模块化版本
    继承自原版本，保持接口兼容
    """
    
    def __init__(self):
        """初始化模块化Hybrid Agent"""
        super().__init__()
        self.logger.info("使用模块化Hybrid Agent（包装器模式）")
    
    def query(self, question: str, context=None):
        """
        执行查询
        完全使用父类的实现
        """
        self.logger.info(f"模块化Hybrid Agent处理查询: {question}")
        return super().query(question, context)