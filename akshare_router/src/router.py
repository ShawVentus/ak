"""
LLM 路由逻辑模块

模块功能：
    调用 LLM 从候选接口中选择最合适的一个，并提取参数。
    支持参数缺失检测和追问生成。

核心功能：
    1. 构建包含完整使用指南的 Prompt
    2. 调用 LLM 进行路由决策
    3. 解析 LLM 返回的 Function Call JSON
    4. 检测缺失参数并生成追问
"""

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import Config


class Router:
    """
    LLM 路由器
    
    功能说明：
        从候选接口中选择最合适的一个，并提取用户查询中的参数。
        支持参数缺失检测，可生成追问引导用户补充信息。
    
    使用示例：
        ```python
        from openai import OpenAI
        from src.router import Router
        from src.config import Config
        
        config = Config.load()
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)
        router = Router(client, config)
        
        result = router.route("平安银行的K线数据", candidates)
        print(result['name'])  # stock_zh_a_daily
        ```
    """
    
    def __init__(self, llm_client: OpenAI, config: Config):
        """
        初始化路由器
        
        Args:
            llm_client: OpenAI 客户端（支持兼容接口）
            config: 配置对象
        """
        self.llm_client = llm_client
        self.config = config
    
    def route(self, query: str, candidates: List[Dict]) -> Dict[str, Any]:
        """
        路由：从候选中选择接口并提取参数
        
        Args:
            query: 用户查询
            candidates: 候选接口列表（需包含 full_guide 字段）
        
        Returns:
            路由结果，格式：
            {
                "name": "接口名",
                "arguments": {"param1": "value1", ...},
                "missing_params": ["param1", ...]  # 缺失的必需参数
            }
            或
            {
                "name": None,
                "reason": "未找到合适接口"
            }
        """
        if not candidates:
            return {"name": None, "reason": "候选列表为空"}
        
        # 构建 Prompt
        prompt = self._build_prompt_with_full_guide(query, candidates)
        
        try:
            # 调用 LLM
            response = self.llm_client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            # 解析结果
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # 验证结果
            result = self._validate_response(result, candidates)
            
            # 检查参数完整性
            if result.get('name'):
                result = self._check_missing_params(result, candidates)
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"[router] JSON 解析失败: {e}")
            return {"name": None, "reason": f"LLM 返回格式错误: {e}"}
        except Exception as e:
            print(f"[router] 路由失败: {e}")
            return {"name": None, "reason": f"路由失败: {e}"}
    
    def _get_system_prompt(self) -> str:
        """
        获取系统 Prompt
        
        Returns:
            系统 Prompt 文本
        """
        return """你是一个金融数据接口路由助手。

用户会提出数据查询需求，你需要从候选接口列表中选择最合适的一个，并提取参数。

输出格式（JSON）：
{
  "name": "接口名",
  "arguments": {
    "参数名": "参数值"
  },
  "missing_params": ["参数1", "参数2"]
}

规则：
1. 仅从候选列表中选择接口，不要编造
2. 根据输入参数表判断哪些参数是必需的
3. 从用户查询中提取参数值，如果用户未提供某个参数，将其值设为 null，并加入 missing_params 列表
4. 如果所有候选都不合适，返回：{"name": null, "reason": "说明原因"}

示例输入：
用户需求：平安银行的K线数据

候选接口 1：
接口名: stock_zh_a_daily
说明: A 股历史行情数据
输入参数:
  - symbol (str): 股票代码
  - start_date (str): 开始日期
  - end_date (str): 结束日期

示例输出：
{
  "name": "stock_zh_a_daily",
  "arguments": {
    "symbol": "000001",
    "start_date": null,
    "end_date": null
  },
  "missing_params": ["start_date", "end_date"]
}
"""
    
    def _build_prompt_with_full_guide(self, query: str, candidates: List[Dict]) -> str:
        """
        使用完整使用指南构建 Prompt
        
        Args:
            query: 用户查询
            candidates: 候选接口列表（包含 full_guide 字段）
        
        Returns:
            格式化后的 Prompt
        """
        prompt = f"用户需求：{query}\n\n候选接口：\n\n"
        
        for i, api in enumerate(candidates, 1):
            prompt += f"### 候选 {i}\n"
            prompt += f"{api.get('full_guide', api.get('description', ''))}\n\n"
        
        prompt += "请选择最合适的接口并输出 JSON。"
        return prompt
    
    def _validate_response(self, result: Dict, candidates: List[Dict]) -> Dict:
        """
        验证 LLM 返回的结果
        
        检查：
            1. name 是否在候选列表中
            2. 格式是否正确
        
        Args:
            result: LLM 返回的结果
            candidates: 候选列表
        
        Returns:
            验证后的结果
        """
        if result.get('name') is None:
            return result
        
        # 检查 name 是否在候选列表中
        candidate_names = {api['name'] for api in candidates}
        
        if result['name'] not in candidate_names:
            print(f"[router] 警告: LLM 返回的接口 {result['name']} 不在候选列表中")
            return {
                "name": None,
                "reason": f"LLM 返回的接口 {result['name']} 不在候选列表中"
            }
        
        # 确保有 arguments 字段
        if 'arguments' not in result:
            result['arguments'] = {}
        
        return result
    
    def _check_missing_params(self, result: Dict, candidates: List[Dict]) -> Dict:
        """
        检查参数完整性
        
        Args:
            result: LLM 返回的结果
            candidates: 候选列表
        
        Returns:
            添加/更新 missing_params 字段的结果
        """
        # 如果 LLM 已经返回了 missing_params，直接使用
        if 'missing_params' not in result:
            result['missing_params'] = []
        
        # 检查哪些参数值为 null
        arguments = result.get('arguments', {})
        for param_name, param_value in arguments.items():
            if param_value is None and param_name not in result['missing_params']:
                result['missing_params'].append(param_name)
        
        return result
    
    def generate_clarification_for_missing_params(
        self,
        query: str,
        api_name: str,
        missing_params: List[str],
        input_params_info: str
    ) -> str:
        """
        为缺失参数生成追问
        
        Args:
            query: 用户原始查询
            api_name: 选中的接口名
            missing_params: 缺失的参数名列表
            input_params_info: 参数定义文本（从 full_guide 中提取）
        
        Returns:
            追问文本
        """
        prompt = f"""用户查询：{query}
选中接口：{api_name}

缺失的参数：
{', '.join(missing_params)}

参数定义：
{input_params_info}

请生成一个友好的追问，引导用户补充这些参数。"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个友好的数据查询助手。请用简洁的中文生成追问，引导用户提供缺失的参数。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[router] 生成追问失败: {e}")
            # 返回默认追问
            return f"我找到了接口 {api_name}，但还需要您提供以下参数：{', '.join(missing_params)}。请问您能补充一下吗？"
    
    def generate_clarification(self, query: str) -> str:
        """
        生成通用追问（用于无法匹配时）
        
        Args:
            query: 用户查询
        
        Returns:
            追问文本
        """
        prompt = f"""用户问题：{query}

我无法确定用户想要查询什么数据。请生成一个友好的澄清问题，帮助理解用户的具体需求。"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个金融数据助手。请用简洁的中文生成澄清问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[router] 生成追问失败: {e}")
            return "抱歉，我没有完全理解您的需求。您能更具体地描述一下想要查询的数据吗？"
    
    def extract_params_from_supplement(
        self,
        original_query: str,
        supplement: str,
        missing_params: List[str]
    ) -> Dict[str, Any]:
        """
        从用户补充的信息中提取参数
        
        Args:
            original_query: 原始查询
            supplement: 用户补充的信息
            missing_params: 缺失的参数列表
        
        Returns:
            提取的参数字典
        """
        prompt = f"""原始查询：{original_query}
用户补充：{supplement}
需要提取的参数：{', '.join(missing_params)}

请从用户补充的信息中提取上述参数的值，返回 JSON 格式。
如果无法提取某个参数，将其值设为 null。"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是参数提取助手。返回 JSON 格式的提取结果。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"[router] 参数提取失败: {e}")
            return {}


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("测试路由器...")
    
    from src.config import Config
    
    config = Config.load()
    
    if not config.validate_api_key():
        print("请先配置 OPENAI_API_KEY")
    else:
        client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        
        router = Router(client, config)
        
        # 模拟候选
        candidates = [
            {
                "name": "stock_zh_a_daily",
                "full_guide": """接口名: stock_zh_a_daily
说明: A 股历史行情数据(日频)
限量: 单次返回指定沪深京 A 股上市公司指定日期间的历史行情日频率数据
输入参数:
  - symbol (str): 股票代码，如 sh600000
  - start_date (str): 开始查询的日期，如 20201103
  - end_date (str): 结束查询的日期，如 20201116
  - adjust (str): 默认返回不复权的数据"""
            }
        ]
        
        result = router.route("平安银行的K线数据", candidates)
        print(f"路由结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
