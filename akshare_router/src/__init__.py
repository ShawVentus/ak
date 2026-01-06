"""
AkShare API 路由系统 - 源代码包

模块功能：
    包含路由系统的所有核心模块。

核心模块：
    - config: 配置管理
    - api_loader: 接口数据加载
    - embedding_adapter: Embedding 适配层
    - vector_store: ChromaDB 向量库管理
    - router: LLM 路由逻辑
    - conversation: 对话管理
"""

from .config import Config, get_config

__all__ = [
    "Config",
    "get_config",
]
