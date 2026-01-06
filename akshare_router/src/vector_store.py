"""
向量库管理模块

模块功能：
    封装 ChromaDB，提供向量索引构建、检索、混合搜索等功能。
    
核心功能：
    1. 构建向量索引（支持增量更新）
    2. 向量检索（基于语义相似度）
    3. 关键词检索（基于子串匹配）
    4. 混合检索 + 去重
"""

import os
from typing import Dict, List, Optional, Set
import chromadb
from chromadb.config import Settings
from chromadb.api.types import EmbeddingFunction

from .api_loader import normalize_text


class VectorStore:
    """
    向量库管理器
    
    功能说明：
        封装 ChromaDB，提供接口向量的存储和检索功能。
        支持增量更新（基于 MD5 判断是否需要重新生成 Embedding）。
    
    使用示例：
        ```python
        from src.embedding_adapter import create_embedding_adapter
        from src.vector_store import VectorStore
        
        adapter = create_embedding_adapter()
        store = VectorStore(adapter, "./data/chroma_db")
        
        # 构建索引
        store.build_index(apis)
        
        # 检索
        results = store.hybrid_search("平安银行K线", keywords=["平安", "银行"], top_k=5)
        ```
    """
    
    COLLECTION_NAME = "akshare_apis"
    
    def __init__(self, embedding_fn: EmbeddingFunction, persist_dir: str):
        """
        初始化向量库
        
        Args:
            embedding_fn: Embedding 函数（ChromaDB 格式）
            persist_dir: 持久化目录路径
        """
        self.embedding_fn = embedding_fn
        self.persist_dir = persist_dir
        
        # 确保目录存在
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False, # 禁用 Telemetry，消除报错
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"description": "AkShare API 接口向量库"}
        )
        
        # 内存缓存：id -> api_dict
        self._cache: Dict[str, Dict] = {}
        # MD5 版本缓存：id -> md5
        self._version_cache: Dict[str, str] = {}
        
        # 关键优化：启动时从 DB 加载已有的 MD5 状态
        try:
            existing_data = self.collection.get(include=["metadatas"])
            if existing_data and existing_data["ids"]:
                for api_id, metadata in zip(existing_data["ids"], existing_data["metadatas"]):
                    if metadata and "md5" in metadata:
                        self._version_cache[api_id] = metadata["md5"]
                print(f"[vector_store] 已从 DB 加载 {len(self._version_cache)} 条接口的版本信息")
        except Exception as e:
            print(f"[vector_store] 警告: 加载版本缓存失败: {e}")
        
        print(f"[vector_store] 初始化完成，持久化目录: {persist_dir}")
        print(f"[vector_store] 当前集合中有 {self.collection.count()} 条记录")
    
    def build_index(self, apis: List[Dict]) -> None:
        """
        构建向量索引（增量更新）
        
        增量更新逻辑：
            1. 对比 MD5，只更新发生变化的接口
            2. 删除不再存在的接口
        
        Args:
            apis: 接口信息列表（来自 api_loader.load_enriched_csv）
        """
        print(f"[vector_store] 开始构建索引，共 {len(apis)} 个接口...")
        
        # 需要更新的接口
        ids_to_update: List[str] = []
        docs_to_update: List[str] = []
        metadatas_to_update: List[Dict] = []
        
        # 当前所有接口 ID
        current_ids: Set[str] = set()
        
        for api in apis:
            api_id = api['id']
            current_md5 = api['md5']
            current_ids.add(api_id)
            
            # 检查是否需要更新
            cached_md5 = self._version_cache.get(api_id, '')
            
            if current_md5 != cached_md5:
                ids_to_update.append(api_id)
                docs_to_update.append(api['embedding_text'])
                metadatas_to_update.append({
                    "name": api['name'],
                    "category": api['category'],
                    "description": api['description'],
                    "md5": api['md5']  # 保存 MD5 以支持增量更新检查
                })
        
        # 批量更新
        if ids_to_update:
            print(f"[vector_store] 需要更新 {len(ids_to_update)} 个接口的向量...")
            self.collection.upsert(
                ids=ids_to_update,
                documents=docs_to_update,
                metadatas=metadatas_to_update
            )
        else:
            print("[vector_store] 所有接口均为最新，无需更新")
        
        # 删除不存在的接口
        existing_ids = set(self.collection.get()['ids'])
        ids_to_delete = existing_ids - current_ids
        
        if ids_to_delete:
            print(f"[vector_store] 删除 {len(ids_to_delete)} 个过期接口...")
            self.collection.delete(ids=list(ids_to_delete))
        
        # 更新缓存
        for api in apis:
            self._cache[api['id']] = api
            self._version_cache[api['id']] = api['md5']
        
        print(f"[vector_store] 索引构建完成，当前共 {self.collection.count()} 条记录")
    
    def vector_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        向量检索
        
        基于语义相似度检索最相关的接口。
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            按相似度排序的接口列表
        """
        result = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # 从缓存获取完整信息
        apis = []
        if result['ids'] and result['ids'][0]:
            for api_id in result['ids'][0]:
                if api_id in self._cache:
                    apis.append(self._cache[api_id])
        
        return apis
    
    def keyword_search(self, keyword: str) -> List[Dict]:
        """
        关键词检索
        
        基于标准化后的子串匹配进行检索。
        
        Args:
            keyword: 关键词
        
        Returns:
            匹配的接口列表
        """
        normalized_keyword = normalize_text(keyword)
        matches = []
        
        for api in self._cache.values():
            # 检索 embedding_text（包含说明、详细描述、限量）
            normalized_text = normalize_text(api['embedding_text'])
            
            if normalized_keyword in normalized_text:
                matches.append(api)
        
        return matches
    
    def hybrid_search(
        self, 
        query: str, 
        keywords: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        混合检索 + 去重
        
        策略：
            1. 先关键词检索
            2. 用向量检索补足到 top_k
            3. 结果去重（按 id）
        
        Args:
            query: 查询文本
            keywords: 关键词列表（可选）
            top_k: 返回结果数量
        
        Returns:
            去重后的接口列表
        """
        seen_ids: Set[str] = set()
        results: List[Dict] = []
        
        # 1. 关键词检索
        if keywords:
            for kw in keywords:
                matches = self.keyword_search(kw)
                for api in matches:
                    if api['id'] not in seen_ids:
                        results.append(api)
                        seen_ids.add(api['id'])
        
        # 2. 向量检索补足（请求 top_k 个以应对去重）
        if len(results) < top_k:
            vector_results = self.vector_search(query, top_k)
            for api in vector_results:
                if api['id'] not in seen_ids:
                    results.append(api)
                    seen_ids.add(api['id'])
                    if len(results) >= top_k:
                        break
        
        return results[:top_k]
    
    def get_api(self, api_id: str) -> Optional[Dict]:
        """
        根据 ID 获取接口信息
        
        Args:
            api_id: 接口 ID
        
        Returns:
            接口信息字典，不存在则返回 None
        """
        return self._cache.get(api_id)
    
    def get_all_apis(self) -> List[Dict]:
        """
        获取所有接口信息
        
        Returns:
            所有接口的列表
        """
        return list(self._cache.values())
    
    def count(self) -> int:
        """
        获取接口数量
        
        Returns:
            接口数量
        """
        return self.collection.count()
    
    def reload_cache(self, apis: List[Dict]) -> None:
        """
        重新加载缓存（不重建索引）
        
        用于启动时从 CSV 恢复内存缓存。
        
        Args:
            apis: 接口信息列表
        """
        self._cache.clear()
        self._version_cache.clear()
        
        for api in apis:
            self._cache[api['id']] = api
            self._version_cache[api['id']] = api['md5']
        
        print(f"[vector_store] 已加载 {len(apis)} 个接口到缓存")


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("测试向量库...")
    
    from src.embedding_adapter import create_embedding_adapter
    from src.api_loader import load_enriched_csv
    
    # 加载数据
    csv_path = "../api/1_stock_enriched.csv"
    apis = load_enriched_csv(csv_path)
    
    # 创建向量库
    adapter = create_embedding_adapter()
    store = VectorStore(adapter, "./data/chroma_db")
    
    # 构建索引（只用前 5 个测试）
    store.build_index(apis[:5])
    
    # 测试检索
    results = store.vector_search("港股行情", top_k=3)
    print(f"\n向量检索结果: {[r['name'] for r in results]}")
