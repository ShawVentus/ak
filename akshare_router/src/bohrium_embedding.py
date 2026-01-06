"""
Bohrium API Embedding 模型（独立版本）

模块功能：
    使用 Bohrium API 的 text-embedding-v4 模型生成文本向量。
    此版本移除了 lmi 依赖，可独立使用。

特性：
    1. 批量请求 (Batching)
    2. 智能重试 (Retrying)
    3. 输入长度检查
    4. 异步执行

使用示例：
    ```python
    embedding = BohriumEmbedding()
    vectors = await embedding.embed_documents(["文本1", "文本2"])
    ```
"""

import os
import logging
import asyncio
from typing import List, Optional

import httpx
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# 配置日志
logger = logging.getLogger(__name__)


class BohriumEmbedding(BaseModel):
    """
    Bohrium API Embedding 模型
    
    功能说明：
        使用 Bohrium 的 text-embedding-v4 模型将文本转换为 1024 维向量。
    
    配置参数：
        name (str): 模型名称，默认 "text-embedding-v4"
        ndim (int): 向量维度，固定 1024
        api_key (str): API 密钥，从环境变量 OPENAI_API_KEY 读取
        api_base (str): API 端点 URL
        timeout (float): HTTP 请求超时时间（秒）
        batch_size (int): 批量处理大小
        max_retries (int): 最大重试次数
        verbose (bool): 是否打印进度日志
    """
    
    # 模型配置
    name: str = Field(
        default="text-embedding-v4",
        description="Bohrium embedding 模型名称"
    )
    
    ndim: int = Field(
        default=1024,
        description="Embedding 向量维度"
    )
    
    # API 配置
    api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="Bohrium API 密钥"
    )
    
    api_base: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://openapi.dp.tech/openapi/v1"),
        description="Bohrium API 端点"
    )
    
    timeout: float = Field(
        default=60.0,
        description="HTTP 请求超时时间（秒）"
    )
    
    # 性能配置
    batch_size: int = Field(
        default=8,
        ge=1,
        le=10,
        description="批量请求大小"
    )
    
    max_retries: int = Field(
        default=3,
        description="最大重试次数"
    )
    
    verbose: bool = Field(
        default=True,
        description="是否显示进度日志"
    )
    
    class Config:
        """Pydantic 配置"""
        arbitrary_types_allowed = True

    def _check_input_length(self, text: str, max_len: int = 8192) -> str:
        """
        检查并截断过长的输入文本
        
        Args:
            text: 输入文本
            max_len: 最大允许长度
        
        Returns:
            处理后的文本
        """
        if len(text) > max_len:
            if self.verbose:
                logger.warning(f"⚠️ 文本过长 ({len(text)} 字符)，将截断至 {max_len}")
            return text[:max_len]
        return text

    async def _embed_batch_with_retry(
        self,
        client: httpx.AsyncClient,
        texts: List[str]
    ) -> List[List[float]]:
        """
        带重试的批量嵌入请求
        
        Args:
            client: HTTP 客户端
            texts: 文本列表
        
        Returns:
            向量列表
        """
        def log_retry(retry_state):
            if self.verbose:
                logger.warning(
                    f"🔄 请求失败，重试 ({retry_state.attempt_number}/{self.max_retries})..."
                )
        
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
            before_sleep=log_retry,
            reraise=True
        ):
            with attempt:
                payload = {
                    "model": self.name,
                    "input": texts
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
                
                if response.status_code >= 500:
                    response.raise_for_status()
                elif response.status_code >= 400:
                    try:
                        err_msg = response.json()
                    except:
                        err_msg = response.text
                    raise ValueError(f"API 错误 (HTTP {response.status_code}): {err_msg}")
                
                data = response.json()
                
                if "data" not in data:
                    raise ValueError(f"响应格式错误: {data}")
                
                # 按 index 排序确保顺序一致
                items = sorted(data["data"], key=lambda x: x.get("index", 0))
                embeddings = [item["embedding"] for item in items]
                
                if len(embeddings) != len(texts):
                    raise ValueError(f"返回数量 ({len(embeddings)}) != 输入数量 ({len(texts)})")
                
                return embeddings

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        异步批量嵌入文本
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表（每个向量 1024 维）
        """
        if not texts:
            return []
        
        if not self.api_key:
            raise ValueError("未配置 API Key，请设置 OPENAI_API_KEY")
        
        # 预处理
        processed = [self._check_input_length(t) for t in texts]
        total = len(processed)
        
        if self.verbose:
            print(f"[BohriumEmbedding] 处理 {total} 条文本 (Batch: {self.batch_size})")
        
        embeddings: List[List[float]] = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            total_batches = (total + self.batch_size - 1) // self.batch_size
            
            for i in range(0, total, self.batch_size):
                batch = processed[i:i + self.batch_size]
                batch_idx = i // self.batch_size + 1
                
                if self.verbose and total_batches > 1:
                    print(f"  > 批次 {batch_idx}/{total_batches} ({len(batch)} 条)")
                
                try:
                    result = await self._embed_batch_with_retry(client, batch)
                    embeddings.extend(result)
                except Exception as e:
                    logger.error(f"❌ 批次 {batch_idx} 失败: {e}")
                    raise
        
        if self.verbose:
            print(f"[BohriumEmbedding] 完成，生成 {len(embeddings)} 个向量")
        
        return embeddings


# ========== 测试代码 ==========
if __name__ == "__main__":
    async def test():
        embedding = BohriumEmbedding(verbose=True)
        texts = ["测试文本1", "测试文本2"]
        
        try:
            vectors = await embedding.embed_documents(texts)
            print(f"成功生成 {len(vectors)} 个向量")
            print(f"维度: {len(vectors[0])}")
        except Exception as e:
            print(f"测试失败: {e}")
    
    asyncio.run(test())
