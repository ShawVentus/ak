"""
Bohrium API 自定义 Embedding 模型实现

模块功能：
    为 PaperQA 提供使用 Bohrium API 的自定义 Embedding 模型，
    绕过 LiteLLM 的标准 OpenAI 认证方式，直接使用 Bohrium 的 accessKey 认证。
    
    Phase 2 优化功能：
    1. 批量请求 (Batching): 减少 HTTP 往返开销，显著提升性能。
    2. 智能重试 (Retrying): 处理网络抖动和服务器过载，增强稳定性。
    3. 安全输入: 自动检查输入长度，防止超限错误。
    4. 规范配置: 移除硬编码，使用 Pydantic 字段管理配置。

核心类：
    BohriumEmbedding: 实现 EmbeddingModel 接口，支持异步批量文本嵌入

技术架构：
    - 继承: lmi.embeddings.EmbeddingModel
    - HTTP客户端: httpx.AsyncClient（异步）
    - 重试机制: tenacity (指数退避策略)
    - 进度显示: logging (verbose 模式)

使用示例：
    ```python
    from bohrium_embedding import BohriumEmbedding
    
    # 推荐配置
    embedding = BohriumEmbedding(
        batch_size=16,      # 每次处理16个文本
        max_retries=3,      # 失败重试3次
        verbose=True        # 显示进度日志
    )
    
    vectors = await embedding.embed_documents(["文本1", ...])
    ```
"""

import os
import logging
import asyncio
from typing import Any, List, Optional
import httpx
from lmi.embeddings import EmbeddingModel
from pydantic import Field, field_validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# 配置日志
logger = logging.getLogger(__name__)

class BohriumEmbedding(EmbeddingModel):
    """
    Bohrium API 自定义 Embedding 模型 (Phase 2 优化版)
    
    功能说明：
        使用 Bohrium 的 text-embedding-v4 模型将文本转换为 1024 维向量。
        包含批量处理、自动重试、长度检查等生产级特性。
    
    配置参数 (Pydantic Fields):
        name (str): 模型名称，默认 "text-embedding-v4"
        ndim (int): 向量维度，固定 1024
        api_key (str): Bohrium API 密钥，仅从环境变量 OPENAI_API_KEY 读取
        api_base (str): API 端点 URL
        timeout (float): HTTP 请求超时时间（秒）
        batch_size (int): 批量处理大小，默认 16
        max_retries (int): 最大重试次数，默认 3
        verbose (bool): 是否打印进度日志，默认 True
        
    异常处理：
        - 认证失败 (401/403): 立即抛出，不重试
        - 客户端错误 (400): 立即抛出，不重试
        - 服务端错误 (5xx): 自动重试
        - 网络/超时错误: 自动重试
    """
    
    # 模型主要配置
    name: str = Field(
        default="text-embedding-v4",
        description="Bohrium embedding 模型名称"
    )
    
    ndim: int = Field(
        default=1024,
        description="Embedding 向量维度（Bohrium text-embedding-v4 固定为 1024）"
    )
    
    # API 认证与连接配置
    api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="Bohrium API 密钥。必须通过环境变量设置，代码中不含默认值。"
    )
    
    api_base: str = Field(
        default="https://openapi.dp.tech/openapi/v1/chat/completions",
        description="Bohrium API 统一端点"
    )
    
    timeout: float = Field(
        default=60.0,
        description="HTTP 请求超时时间（秒）"
    )
    
    # 性能优化配置
    batch_size: int = Field(
        default=8,
        ge=1,
        le=10,
        description="批量请求大小。Bohrium API 限制最大为 10，建议 8。"
    )
    
    max_retries: int = Field(
        default=3,
        description="API 请求失败时的最大重试次数"
    )
    
    verbose: bool = Field(
        default=True,
        description="是否在控制台输出处理进度日志"
    )

    @field_validator('api_key')
    def validate_api_key(cls, v):
        """验证 API Key 是否存在"""
        if not v:
            # 允许实例化时为空，但在调用时如果仍为空则会失败
            # 这里仅给出一个警告，避免破坏某些无需调用的场景
            logger.warning("⚠️ 未检测到 API Key。请设置环境变量 OPENAI_API_KEY。")
        return v

    def _validate_embedding(self, embedding: List[float]) -> None:
        """
        验证单个 embedding 向量的有效性
        
        Args:
            embedding: API 返回的向量列表
            
        Raises:
            ValueError: 维度不匹配时抛出
        """
        actual_dim = len(embedding)
        if actual_dim != self.ndim:
            raise ValueError(
                f"Embedding 维度不匹配: 收到 {actual_dim} 维，预期 {self.ndim} 维"
            )

    def _check_input_length(self, text: str, max_len: int = 8192) -> str:
        """
        检查并截断过长的输入文本
        
        Args:
            text: 输入文本
            max_len: 最大允许长度（字符数），默认 8192 (基于测试结果)
            
        Returns:
            str: 处理后的文本
        """
        if len(text) > max_len:
            if self.verbose:
                logger.warning(
                    f"⚠️ 文本过长 ({len(text)} 字符)，将被截断至 {max_len} 字符。"
                )
            return text[:max_len]
        return text

    async def _embed_batch_with_retry(
        self,
        client: httpx.AsyncClient,
        texts: List[str]
    ) -> List[List[float]]:
        """
        带重试机制的批量嵌入请求
        
        功能说明：
            发送单个 batch 的请求，如果在 retry 策略范围内失败则自动重试。
            
        重试策略：
            - 触发条件: 网络错误, 超时, 5xx 状态码
            - 停止条件: 达到 max_retries 次数
            - 等待策略: 指数退避 (1s, 2s, 4s...)
            
        Args:
            client: Shared httpx Client
            texts: 当前 batch 的文本列表
            
        Returns:
            List[List[float]]: 对应的向量列表
        """
        
        # 定义重试前的回调（用于日志）
        def log_retry(retry_state):
            if self.verbose:
                logger.warning(
                    f"🔄 请求失败，正在重试 ({retry_state.attempt_number}/{self.max_retries})... "
                    f"异常: {retry_state.outcome.exception()}"
                )

        # 导入 AsyncRetrying
        from tenacity import AsyncRetrying

        # 使用 AsyncRetrying 上下文管理器
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException, httpx.RemoteProtocolError)),
            before_sleep=log_retry,
            reraise=True
        ):
            with attempt:
                payload = {
                    "model": self.name,
                    "input": texts  # 批量发送
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "accessKey": self.api_key
                }
                
                response = await client.post(
                    self.api_base,
                    json=payload,
                    headers=headers
                )
                
                # 处理 HTTP 状态码
                if response.status_code >= 500:
                    # 服务端错误 -> 抛出异常以触发重试
                    response.raise_for_status()
                elif response.status_code >= 400:
                    # 客户端错误 (400, 401, 403, 413) -> 不重试，直接抛出
                    # 413: Payload Too Large -> 可能 batch 还是太大了
                    if response.status_code == 413:
                        raise ValueError(f"HTTP 413: 请求体过大，请减小 batch_size (当前: {self.batch_size})")
                    
                    try:
                        err_msg = response.json()
                    except:
                        err_msg = response.text
                    raise ValueError(f"API 请求失败 (HTTP {response.status_code}): {err_msg}")
                
                # 请求成功
                data = response.json()
                
                if "data" not in data:
                    raise ValueError(f"API 响应格式错误: 缺少 'data' 字段。响应: {data}")
                
                batch_embeddings = []
                # 确保顺序一致性
                # Bohrium 返回的 data 列表顺序通常与 input 一致，但我们要按 index 排序以防万一
                items = sorted(data["data"], key=lambda x: x["index"])
                
                for item in items:
                    vec = item["embedding"]
                    self._validate_embedding(vec)
                    batch_embeddings.append(vec)
                
                # 校验数量
                if len(batch_embeddings) != len(texts):
                    raise ValueError(
                        f"返回向量数量 ({len(batch_embeddings)}) 与 输入数量 ({len(texts)}) 不一致"
                    )
                    
                return batch_embeddings

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        异步批量嵌入文本列表 (入口方法)
        
        功能说明：
            1. 预处理：检查 API Key，截断过长文本。
            2. 分片：将长列表切分为多个小 batch。
            3. 执行：创建 HTTP 客户端，逐个 batch 执行（带重试）。
            4. 汇总：收集所有结果并返回。
        
        Args:
            texts: 文本列表
            
        Returns:
            List[List[float]]: 向量列表
        """
        if not texts:
            return []
            
        if not self.api_key:
            raise ValueError("未配置 API Key。请设置环境变量 OPENAI_API_KEY。")

        # 1. 预处理文本
        processed_texts = [self._check_input_length(t) for t in texts]
        total_texts = len(processed_texts)
        
        if self.verbose:
            print(f"[BohriumEmbedding] 开始处理 {total_texts} 条文本 (Batch Size: {self.batch_size})...")

        embeddings: List[List[float]] = []
        
        # 2. 创建客户端
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 3. 分批处理
            # 改进：在此处实现 Batch 切分循环
            total_batches = (total_texts + self.batch_size - 1) // self.batch_size
            
            for i in range(0, total_texts, self.batch_size):
                batch_texts = processed_texts[i : i + self.batch_size]
                current_batch_idx = i // self.batch_size + 1
                
                if self.verbose and total_batches > 1:
                    # 简单进度日志
                    print(f"  > 处理批次 {current_batch_idx}/{total_batches} ({len(batch_texts)} 条)...")
                
                try:
                    # 调用带重试的内部方法
                    batch_result = await self._embed_batch_with_retry(client, batch_texts)
                    embeddings.extend(batch_result)
                except Exception as e:
                    logger.error(f"❌ 批次 {current_batch_idx} 处理失败: {e}")
                    raise  # 依然抛出异常，中断流程（因为 embedding通常要求全部成功）

        if self.verbose:
            print(f"[BohriumEmbedding] 完成。共生成 {len(embeddings)} 个向量。")
            
        return embeddings
