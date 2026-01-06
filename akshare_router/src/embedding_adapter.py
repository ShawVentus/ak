"""
Embedding 适配层模块

模块功能：
    将 BohriumEmbedding（异步）适配为 ChromaDB 的 EmbeddingFunction（同步）。
    
核心问题：
    1. BohriumEmbedding.embed_documents 是异步方法
    2. ChromaDB 的 EmbeddingFunction 必须是同步的
    3. Gradio 可能已有 event loop，直接 asyncio.run 会报错

解决方案：
    检测是否已有 running loop，如有则使用线程池执行
"""

import asyncio
import concurrent.futures
from typing import List

from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

from .bohrium_embedding import BohriumEmbedding


class ChromaEmbeddingAdapter(EmbeddingFunction):
    """
    ChromaDB Embedding 适配器
    
    功能说明：
        将异步的 BohriumEmbedding 包装为同步的 EmbeddingFunction，
        供 ChromaDB 在构建索引和查询时调用。
    
    使用示例：
        ```python
        from src.bohrium_embedding import BohriumEmbedding
        from src.embedding_adapter import ChromaEmbeddingAdapter
        
        bohrium = BohriumEmbedding()
        adapter = ChromaEmbeddingAdapter(bohrium)
        
        # ChromaDB 会自动调用
        vectors = adapter(["文本1", "文本2"])
        ```
    """
    
    def __init__(self, bohrium_embedding: BohriumEmbedding):
        """
        初始化适配器
        
        Args:
            bohrium_embedding: BohriumEmbedding 实例
        """
        self.bohrium_embedding = bohrium_embedding
    
    def __call__(self, input: Documents) -> Embeddings:
        """
        生成 Embedding（供 ChromaDB 调用）
        
        Args:
            input: 文本列表
        
        Returns:
            向量列表（每个向量为 1024 维）
        
        技术说明：
            1. 检测是否已有 running event loop
            2. 如果有，使用线程池执行异步方法
            3. 如果没有，直接使用 asyncio.run
        """
        try:
            # 尝试获取正在运行的 event loop
            loop = asyncio.get_running_loop()
            
            # 如果已有 loop（如在 Gradio 中），使用线程池执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self._run_async_in_new_loop,
                    input
                )
                return future.result()
                
        except RuntimeError:
            # 没有 running loop，直接运行
            return asyncio.run(
                self.bohrium_embedding.embed_documents(list(input))
            )
    
    def _run_async_in_new_loop(self, texts: Documents) -> Embeddings:
        """
        在新的 event loop 中运行异步方法
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表
        """
        # 创建新的 event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.bohrium_embedding.embed_documents(list(texts))
            )
        finally:
            loop.close()


def create_embedding_adapter() -> ChromaEmbeddingAdapter:
    """
    创建 Embedding 适配器（工厂函数）
    
    Returns:
        ChromaEmbeddingAdapter 实例
    
    使用示例：
        ```python
        adapter = create_embedding_adapter()
        vectors = adapter(["测试文本"])
        ```
    """
    # 加载 .env 确保环境变量可用
    from dotenv import load_dotenv
    import os
    
    # 尝试从当前目录和上级目录加载 .env
    load_dotenv()
    
    # 获取配置
    api_key = os.getenv("OPENAI_API_KEY", "")
    # Bohrium Embedding API 端点（注意：与 chat 端点不同）
    api_base = os.getenv("EMBEDDING_API_BASE", "https://openapi.dp.tech/openapi/v1/chat/completions")
    
    if not api_key:
        print("[embedding_adapter] 警告: 未找到 OPENAI_API_KEY 环境变量")
    
    bohrium = BohriumEmbedding(
        api_key=api_key,
        api_base=api_base,
        batch_size=8,
        max_retries=3,
        verbose=True
    )
    return ChromaEmbeddingAdapter(bohrium)


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("测试 Embedding 适配器...")
    
    adapter = create_embedding_adapter()
    
    test_texts = ["港股的历史行情数据", "A股分时数据"]
    
    try:
        vectors = adapter(test_texts)
        print(f"成功生成 {len(vectors)} 个向量")
        print(f"向量维度: {len(vectors[0])}")
    except Exception as e:
        print(f"测试失败: {e}")
