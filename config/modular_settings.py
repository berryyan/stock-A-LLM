"""
模块化系统配置
"""

# 是否使用模块化Agent
USE_MODULAR_AGENTS = True

# 模块化Agent配置
MODULAR_AGENT_CONFIG = {
    "enable_cache": True,
    "cache_ttl": 300,  # 5分钟
    "enable_parallel_processing": True,
    "max_workers": 4
}