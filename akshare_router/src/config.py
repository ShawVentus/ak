"""
配置管理模块

模块功能：
    集中管理所有配置参数，从环境变量加载配置。
    使用 pydantic-settings 自动验证类型。

核心类：
    Config: 全局配置对象
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """
    全局配置对象
    
    功能说明：
        从 .env 文件或环境变量加载配置，自动验证类型。
        所有配置项都有合理的默认值，除了 API Key 必须手动配置。
    
    使用示例：
        ```python
        config = Config.load()
        print(config.LLM_MODEL)  # qwen-plus
        ```
    """
    
    # ========== API 配置 ==========
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI 兼容接口的 API Key"
    )
    
    # 支持 OPENAI_API_BASE 或 OPENAI_BASE_URL
    OPENAI_BASE_URL: str = Field(
        default="https://openapi.dp.tech/openapi/v1",
        alias="OPENAI_API_BASE",
        description="API 端点地址"
    )
    
    # ========== 模型配置 ==========
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-v4",
        description="Embedding 模型名称"
    )
    
    # 支持 OPENAI_MODEL 或 LLM_MODEL
    LLM_MODEL: str = Field(
        default="qwen-plus",
        alias="OPENAI_MODEL",
        description="LLM 模型名称"
    )
    
    # ========== 路由配置 ==========
    TOP_K: int = Field(
        default=5,
        description="向量检索返回的候选数量"
    )
    
    TOP_K_EXTENDED: int = Field(
        default=15,
        description="降级时扩大检索的候选数量"
    )
    
    MAX_CLARIFY_ROUNDS: int = Field(
        default=5,
        description="最大追问轮数"
    )
    
    MAX_RETRY_TIMES: int = Field(
        default=2,
        description="Phase 2: LLM 自我修正最大重试次数"
    )
    
    # ========== 路径配置 ==========
    CHROMA_PERSIST_DIR: str = Field(
        default="./data/chroma_db",
        description="ChromaDB 持久化目录"
    )
    
    RESULTS_DIR: str = Field(
        default="./results",
        description="CSV 结果输出目录（Phase 2）"
    )
    
    # ========== Gradio 配置 ==========
    GRADIO_SERVER_PORT: int = Field(
        default=7860,
        description="Gradio 服务端口"
    )
    
    GRADIO_SHARE: bool = Field(
        default=False,
        description="是否生成公开分享链接"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # 忽略额外字段
        "populate_by_name": True  # 支持 alias
    }
    
    @classmethod
    def load(cls, env_path: Optional[str] = None) -> "Config":
        """
        加载配置
        
        Args:
            env_path: .env 文件路径，默认为当前目录下的 .env
        
        Returns:
            Config: 配置对象
        
        使用示例：
            ```python
            config = Config.load()
            # 或指定 .env 路径
            config = Config.load("/path/to/.env")
            ```
        """
        if env_path:
            # 加载指定的 .env 文件
            from dotenv import load_dotenv
            load_dotenv(env_path)
        
        return cls()
    
    def validate_api_key(self) -> bool:
        """
        验证 API Key 是否已配置
        
        Returns:
            bool: True 表示已配置，False 表示未配置
        """
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_api_key_here")
    
    def get_absolute_chroma_dir(self, base_dir: Optional[str] = None) -> str:
        """
        获取 ChromaDB 持久化目录的绝对路径
        
        Args:
            base_dir: 基础目录，默认为当前工作目录
        
        Returns:
            str: 绝对路径
        """
        if os.path.isabs(self.CHROMA_PERSIST_DIR):
            return self.CHROMA_PERSIST_DIR
        
        base = base_dir or os.getcwd()
        return os.path.join(base, self.CHROMA_PERSIST_DIR)


# 全局配置实例（延迟加载）
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        Config: 全局配置对象
    
    使用示例：
        ```python
        from src.config import get_config
        config = get_config()
        print(config.LLM_MODEL)
        ```
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance
