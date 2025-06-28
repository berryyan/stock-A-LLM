#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
灵活的输出解析器
处理LLM输出格式不一致的问题
"""

from typing import Union, Dict, Any
from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re
import logging

logger = logging.getLogger(__name__)


class FlexibleSQLOutputParser(AgentOutputParser):
    """
    更灵活的SQL Agent输出解析器
    能够处理多种输出格式，减少解析错误
    """
    
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """解析LLM输出"""
        # 清理文本
        text = text.strip()
        
        # 1. 尝试标准格式 (Final Answer:)
        if "Final Answer:" in text:
            # 提取Final Answer后的内容
            answer_start = text.find("Final Answer:") + len("Final Answer:")
            answer = text[answer_start:].strip()
            return AgentFinish({"output": answer}, text)
        
        # 2. 尝试中文格式（最终答案：）
        if "最终答案：" in text or "最终答案:" in text:
            pattern = r"最终答案[：:](.+)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                answer = match.group(1).strip()
                return AgentFinish({"output": answer}, text)
        
        # 3. 检查是否是Action格式
        if "Action:" in text and "Action Input:" in text:
            # 标准的ReAct格式
            regex = r"Action:\s*(.+?)\nAction Input:\s*(.+)"
            match = re.search(regex, text, re.DOTALL)
            if match:
                action = match.group(1).strip()
                action_input = match.group(2).strip()
                return AgentAction(tool=action, tool_input=action_input, log=text)
        
        # 4. 检查是否包含SQL查询结果的特征
        sql_result_patterns = [
            r"查询结果[：:]",
            r"数据如下[：:]",
            r"股价为[：:]",
            r"成交量为[：:]",
            r"\d{4}年\d{1,2}月\d{1,2}日",  # 日期格式
            r"开盘价.*元.*收盘价.*元",  # 股价格式
        ]
        
        for pattern in sql_result_patterns:
            if re.search(pattern, text):
                # 看起来是查询结果，直接返回
                logger.info("检测到查询结果特征，直接返回")
                return AgentFinish({"output": text}, text)
        
        # 5. 如果文本看起来像是完整的回答（包含中文句号或具体数据）
        if "。" in text or re.search(r'\d+\.?\d*[元手亿万]', text):
            # 可能是直接的答案
            logger.info("检测到可能的直接答案，返回整个文本")
            return AgentFinish({"output": text}, text)
        
        # 6. 最后的降级处理
        # 如果实在无法解析，但文本不为空，就当作答案返回
        if len(text) > 10:  # 至少有一些内容
            logger.warning(f"无法解析输出格式，降级处理: {text[:100]}...")
            return AgentFinish({"output": text}, text)
        
        # 如果都失败了，抛出异常
        raise OutputParserException(
            f"无法解析LLM输出。请确保输出包含'Final Answer:'或明确的查询结果。\n收到的文本: {text}"
        )
    
    def get_format_instructions(self) -> str:
        """返回格式说明"""
        return """请按以下格式输出：

当你需要使用工具时：
```
Action: 工具名称
Action Input: 工具输入
```

当你得到最终答案时：
```
Final Answer: 你的中文答案
```

示例：
- 查询股价: Final Answer: 贵州茅台（600519.SH）在2025年6月27日的股价为：开盘价1420元，收盘价1403元
- 查询财务: Final Answer: 贵州茅台2024年营业收入为1708.99亿元，净利润为862.28亿元
"""


def extract_result_from_error(error_str: str) -> str:
    """
    从解析错误信息中提取实际的查询结果
    """
    # 查找被反引号包围的内容
    pattern = r"`([^`]+)`"
    matches = re.findall(pattern, error_str)
    
    if matches:
        # 返回最后一个匹配（通常是实际的LLM输出）
        result = matches[-1]
        
        # 清理一些常见的前缀
        prefixes_to_remove = [
            "Could not parse LLM output:",
            "An output parsing error occurred:",
        ]
        
        for prefix in prefixes_to_remove:
            if result.startswith(prefix):
                result = result[len(prefix):].strip()
        
        return result
    
    return error_str


def test_parser():
    """测试解析器"""
    parser = FlexibleSQLOutputParser()
    
    test_cases = [
        # 标准格式
        "Final Answer: 贵州茅台（600519.SH）在2025年6月27日的股价为：开盘价1420.01元",
        
        # 中文格式
        "最终答案：比亚迪（002594.SZ）在2025年6月27日的成交量为138,617手",
        
        # 直接结果
        "贵州茅台(600519.SH)最近5期的营业收入和净利润数据如下：\n1. 2025年一季度：营业收入506.01亿元",
        
        # Action格式
        "Action: sql_db_query\nAction Input: SELECT * FROM tu_daily_detail",
        
        # 包含日期的结果
        "查询结果：2025年6月27日，平安银行收盘价为12.5元。"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {test_case[:50]}...")
        try:
            result = parser.parse(test_case)
            if isinstance(result, AgentFinish):
                print(f"✓ 解析成功 (AgentFinish): {result.return_values['output'][:50]}...")
            else:
                print(f"✓ 解析成功 (AgentAction): {result.tool}")
        except Exception as e:
            print(f"✗ 解析失败: {e}")


if __name__ == "__main__":
    test_parser()