"""
对话管理模块

模块功能：
    管理多轮对话，协调向量检索和 LLM 路由，处理参数缺失追问。

核心功能：
    1. 处理用户消息（主入口）
    2. 管理对话状态（待补充参数等）
    3. 实现降级策略（扩大检索、追问、告知边界）
    4. 提取关键词（用于混合检索）
"""

import json
import os
from typing import Any, Dict, List, Optional

import jieba
import jieba.analyse

from .config import Config
from .router import Router
from .vector_store import VectorStore


class ConversationManager:
    """
    对话管理器
    
    功能说明：
        协调向量检索和 LLM 路由，管理多轮对话状态，
        处理参数缺失的追问流程。
    
    使用示例：
        ```python
        manager = ConversationManager(vector_store, router, config)
        response = manager.handle_message("平安银行的K线数据")
        print(response)
        ```
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        router: Router,
        config: Config
    ):
        """
        初始化对话管理器
        
        Args:
            vector_store: 向量库管理器
            router: LLM 路由器
            config: 配置对象
        """
        self.vector_store = vector_store
        self.router = router
        self.config = config
        
        # 初始化状态
        self.reset()
    
    def handle_message(self, user_input: str) -> str:
        """
        处理用户消息（主入口）
        
        流程：
            1. 如果有待补充参数，尝试提取
            2. 否则，进行正常的检索和路由流程
        
        Args:
            user_input: 用户输入
        
        Returns:
            系统响应文本
        """
        # 记录对话
        self.history.append({"role": "user", "content": user_input})
        
        # 1. 检查是否在补充参数
        if self.pending_api_call:
            response = self._handle_param_supplement(user_input)
            self.history.append({"role": "assistant", "content": response})
            return response
        
        # 2. 提取关键词
        keywords = self._extract_keywords(user_input)
        print(f"[conversation] 提取的关键词: {keywords}")
        
        # 3. 混合检索候选
        candidates = self.vector_store.hybrid_search(
            query=user_input,
            keywords=keywords,
            top_k=self.config.TOP_K
        )
        
        print(f"[conversation] 检索到 {len(candidates)} 个候选接口")
        # 调试信息：打印候选接口
        for i, cand in enumerate(candidates):
            print(f"  {i+1}. {cand['name']} ({cand['description'][:30]}...) [Score: {cand.get('score', 'N/A')}]")
        
        if not candidates:
            response = self._handle_no_match(user_input)
            self.history.append({"role": "assistant", "content": response})
            return response
        
        # 4. LLM 路由
        result = self.router.route(user_input, candidates)
        # 调试信息：打印路由结果
        print(f"[conversation] LLM 路由结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 5. 处理路由结果
        if result.get('name') is None:
            # 无匹配 → 降级策略
            response = self._handle_no_match(user_input)
        elif result.get('missing_params'):
            # 参数缺失 → 追问
            response = self._handle_missing_params(user_input, result, candidates)
        else:
            # 成功 → 返回结果
            response = self._format_success_response(result)
        
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def _handle_missing_params(
        self,
        user_query: str,
        result: Dict,
        candidates: List[Dict]
    ) -> str:
        """
        处理参数缺失
        
        Args:
            user_query: 用户查询
            result: LLM 路由结果
            candidates: 候选列表
        
        Returns:
            追问文本
        """
        # 保存待执行的调用
        self.pending_api_call = {
            "name": result['name'],
            "arguments": result['arguments'],
            "missing_params": result['missing_params'],
            "original_query": user_query,
            "supplement_count": 0  # 追问次数计数
        }
        
        # 获取接口的参数信息
        api = next((c for c in candidates if c['name'] == result['name']), None)
        input_params_info = api.get('full_guide', '') if api else ''
        
        # 生成追问
        question = self.router.generate_clarification_for_missing_params(
            query=user_query,
            api_name=result['name'],
            missing_params=result['missing_params'],
            input_params_info=input_params_info
        )
        
        return question
    
    def _handle_param_supplement(self, user_input: str) -> str:
        """
        处理用户补充参数
        
        Args:
            user_input: 用户补充的信息
        
        Returns:
            更新后的结果或继续追问
        """
        # 增加补充次数计数
        self.pending_api_call['supplement_count'] = self.pending_api_call.get('supplement_count', 0) + 1
        
        # 检查是否超过最大补充次数（3次）
        if self.pending_api_call['supplement_count'] > 3:
            self.pending_api_call = None
            return "抱歉，我无法获取完整的参数信息。请重新描述您的需求。"
        
        # 从用户补充中提取参数
        new_params = self.router.extract_params_from_supplement(
            original_query=self.pending_api_call['original_query'],
            supplement=user_input,
            missing_params=self.pending_api_call['missing_params']
        )
        
        # 合并参数
        for key, value in new_params.items():
            if value is not None:
                self.pending_api_call['arguments'][key] = value
        
        # 检查是否还有缺失
        still_missing = []
        for param in self.pending_api_call['missing_params']:
            if self.pending_api_call['arguments'].get(param) is None:
                still_missing.append(param)
        
        if still_missing:
            # 仍有缺失 → 继续追问
            self.pending_api_call['missing_params'] = still_missing
            return f"好的，我已记录。但还需要您提供：{', '.join(still_missing)}"
        else:
            # 参数完整 → 返回结果
            result = self.pending_api_call
            self.pending_api_call = None  # 清空状态
            return self._format_success_response(result)
    
    def _handle_no_match(self, user_input: str) -> str:
        """
        降级策略：处理无法匹配的情况
        
        策略：
            1. 扩大检索 Top-K
            2. 追问用户
            3. 告知能力边界
        
        Args:
            user_input: 用户查询
        
        Returns:
            响应文本
        """
        self.clarify_count += 1
        
        # 1. 尝试扩大检索
        if self.clarify_count == 1:
            print("[conversation] 降级: 扩大检索范围")
            
            keywords = self._extract_keywords(user_input)
            candidates = self.vector_store.hybrid_search(
                query=user_input,
                keywords=keywords,
                top_k=self.config.TOP_K_EXTENDED
            )
            
            if candidates:
                result = self.router.route(user_input, candidates)
                if result.get('name'):
                    self.clarify_count = 0  # 重置计数
                    if result.get('missing_params'):
                        return self._handle_missing_params(user_input, result, candidates)
                    else:
                        return self._format_success_response(result)
        
        # 2. 追问用户
        if self.clarify_count < self.config.MAX_CLARIFY_ROUNDS:
            return self.router.generate_clarification(user_input)
        
        # 3. 告知能力边界
        self.clarify_count = 0  # 重置
        return self._get_capability_description()
    
    def _get_capability_description(self) -> str:
        """
        告知系统能力范围
        
        Returns:
            能力说明文本
        """
        return """抱歉，我无法理解您的需求。

我目前支持的查询类型：
- 股票行情数据（A股、港股、美股、科创板、创业板）
- 财务报表查询（资产负债表、利润表、现金流量表）
- 板块行情数据（行业板块、概念板块）
- 融资融券数据
- 沪深港通数据
- 股权质押、商誉等特色数据

请尝试更具体的描述，例如："平安银行2023年的日K线数据"。
"""
    
    def _format_success_response(self, result: Dict) -> str:
        """
        格式化成功响应
        
        Args:
            result: 路由结果
        
        Returns:
            格式化后的响应文本
        """
        response = f"✅ 已找到接口：**{result['name']}**\n\n"
        response += f"**参数：**\n```json\n{json.dumps(result['arguments'], ensure_ascii=False, indent=2)}\n```\n\n"
        response += "（Phase 1a 阶段，仅展示结果，不执行实际调用）"
        
        return response
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        从查询中提取关键词
        
        策略：
        1. 使用 jieba TF-IDF 提取
        2. 强制保留 user_dict 中的专业术语
        """
        # 1. TF-IDF 提取 Top 5
        keywords = jieba.analyse.extract_tags(query, topK=5)
        
        # 2. 强制保留自定义词典中的词
        # 检查 self.user_dict_words (在 init 中加载)
        if hasattr(self, 'user_dict_words'):
            # 简单分词用于匹配（或直接字符串匹配）
            # 直接字符串匹配更稳妥，可以捕获未被分词切出的长词
            for word in self.user_dict_words:
                if word in query and word not in keywords:
                    keywords.append(word)
        
        # 去重并返回
        return list(set(keywords))
    
    def reset(self) -> None:
        """
        重置对话状态
        """
        self.history = []  # 直接初始化，支持 __init__ 调用
        self.clarify_count = 0
        self.pending_api_call = None  # 待执行的 API 调用（缺少参数）
        
        # 加载自定义词典
        self.user_dict_words = set()
        user_dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_dict.txt")
        if os.path.exists(user_dict_path):
            jieba.load_userdict(user_dict_path)
            # 同时读取到 set 中用于强制匹配
            with open(user_dict_path, 'r') as f:
                for line in f:
                    word = line.split()[0]
                    self.user_dict_words.add(word)
            print(f"[conversation] 加载自定义词典: {len(self.user_dict_words)} 个词条")
        print("[conversation] 对话状态已重置")


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("测试对话管理器...")
    
    # 这里需要完整的初始化流程
    print("请运行 cli.py 或 app.py 进行完整测试")
