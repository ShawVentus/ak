"""
接口数据加载模块

模块功能：
    从 CSV 文件加载 AkShare 接口信息，并生成用于 Embedding 和 LLM 上下文的文本。
    
核心功能：
    1. 加载 enriched CSV 文件
    2. 拼接字段生成 embedding_text（说明+详细描述+限量）
    3. 生成完整使用指南（用于 LLM 上下文）
    4. 生成 MD5 签名（用于增量更新）
"""

import csv
import hashlib
import os
import re
from typing import Dict, List, Optional


def load_enriched_csv(csv_path: str) -> List[Dict]:
    """
    加载增强后的 CSV 文件
    
    Args:
        csv_path: CSV 文件路径（如 api/1_stock_enriched.csv）
    
    Returns:
        接口信息列表，每个元素包含：
        - id: 接口名（唯一标识）
        - name: 接口名
        - category: 子分类
        - description: 说明 (Description)
        - detail: 详细描述
        - limit: 限量
        - input_params: 输入参数（原始文本）
        - embedding_text: 用于 Embedding 的拼接文本
        - full_guide: 完整使用指南（用于 LLM 上下文）
        - md5: embedding_text 的 MD5 签名
    
    使用示例：
        ```python
        apis = load_enriched_csv("api/1_stock_enriched.csv")
        print(apis[0]['embedding_text'])
        ```
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")
    
    apis = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        current_category = ""
        
        for row in reader:
            # 处理子分类（可能为空，继承上一行）
            if row.get('子分类'):
                current_category = row['子分类']
            
            # 获取接口名
            func_name = row.get('接口名称 (Function)', '').strip()
            if not func_name:
                continue  # 跳过空行
            
            # 获取各字段
            description = row.get('说明 (Description)', '').strip()
            detail = row.get('详细描述', '').strip()
            limit = row.get('限量', '').strip()
            input_params = row.get('输入参数', '').strip()
            
            # 生成 embedding_text（拼接：说明 + 详细描述 + 限量）
            embedding_text = build_embedding_text(description, detail, limit)
            
            # 生成完整使用指南（用于 LLM 上下文）
            full_guide = build_full_guide(
                func_name=func_name,
                description=description,
                detail=detail,
                limit=limit,
                input_params=input_params
            )
            
            # 生成 MD5
            md5 = generate_md5(embedding_text)
            
            api_dict = {
                "id": func_name,
                "name": func_name,
                "category": current_category,
                "description": description,
                "detail": detail,
                "limit": limit,
                "input_params": input_params,
                "embedding_text": embedding_text,
                "full_guide": full_guide,
                "md5": md5
            }
            
            apis.append(api_dict)
    
    # 去重：保留首次出现的接口
    seen_ids = set()
    unique_apis = []
    for api in apis:
        if api['id'] not in seen_ids:
            unique_apis.append(api)
            seen_ids.add(api['id'])
        else:
            print(f"[api_loader] 警告: 发现重复接口 {api['id']}，已跳过")
    
    print(f"[api_loader] 成功加载 {len(unique_apis)} 个接口（原始 {len(apis)} 条，去重 {len(apis) - len(unique_apis)} 条）")
    return unique_apis


def build_embedding_text(description: str, detail: str, limit: str) -> str:
    """
    构建用于 Embedding 的文本
    
    规则：
        拼接顺序：说明 + 详细描述 + 限量
        使用句号分隔
    
    Args:
        description: 说明
        detail: 详细描述
        limit: 限量
    
    Returns:
        拼接后的文本
    
    使用示例：
        ```python
        text = build_embedding_text(
            "港股的历史行情数据",
            "获取所有港股的实时行情数据 15 分钟延时",
            "单次返回当前时间戳的所有港股的数据"
        )
        # 输出: "港股的历史行情数据。获取所有港股的实时行情数据 15 分钟延时。单次返回当前时间戳的所有港股的数据"
        ```
    """
    parts = []
    
    if description:
        parts.append(description)
    if detail:
        parts.append(detail)
    if limit:
        parts.append(limit)
    
    result = "。".join(parts)
    return result if result else "无描述"


def build_full_guide(
    func_name: str,
    description: str,
    detail: str,
    limit: str,
    input_params: str
) -> str:
    """
    构建完整使用指南（用于 LLM 上下文）
    
    包含：描述、限量、输入参数表
    不包含：输出参数表、示例代码、数据示例
    
    Args:
        func_name: 接口名
        description: 说明
        detail: 详细描述
        limit: 限量
        input_params: 输入参数（Markdown 表格格式）
    
    Returns:
        格式化后的完整使用指南
    
    使用示例：
        ```python
        guide = build_full_guide(
            func_name="stock_hk_spot",
            description="港股的历史行情数据",
            detail="获取所有港股的实时行情数据",
            limit="单次返回所有港股的数据",
            input_params="| 名称 | 类型 | 描述 |..."
        )
        ```
    """
    lines = []
    
    # 接口名
    lines.append(f"接口名: {func_name}")
    
    # 描述
    if description:
        lines.append(f"说明: {description}")
    
    # 详细描述
    if detail:
        lines.append(f"详细: {detail}")
    
    # 限量
    if limit:
        lines.append(f"限量: {limit}")
    
    # 输入参数
    if input_params and input_params.strip() != '-':
        lines.append("输入参数:")
        # 解析参数表格为更简洁的格式
        parsed_params = parse_input_params(input_params)
        if parsed_params:
            for param in parsed_params:
                lines.append(f"  - {param['name']} ({param['type']}): {param['description']}")
        else:
            lines.append("  无")
    else:
        lines.append("输入参数: 无")
    
    return "\n".join(lines)


def parse_input_params(params_text: str) -> List[Dict]:
    """
    解析输入参数表格
    
    Args:
        params_text: Markdown 表格格式的参数文本
    
    Returns:
        参数列表，每个元素包含 name, type, description
    
    使用示例：
        ```python
        params = parse_input_params("| symbol | str | symbol=\"sh600000\" |")
        # 输出: [{"name": "symbol", "type": "str", "description": "symbol=\"sh600000\""}]
        ```
    """
    if not params_text:
        return []
    
    params = []
    
    # 按行分割
    lines = params_text.strip().split('\n')
    
    for line in lines:
        # 跳过表头分隔符行
        if re.match(r'^[\s|:-]+$', line):
            continue
        
        # 解析表格行
        if '|' in line:
            cells = [cell.strip() for cell in line.split('|')]
            # 过滤空单元格
            cells = [c for c in cells if c]
            
            if len(cells) >= 3:
                name = cells[0]
                param_type = cells[1]
                description = cells[2] if len(cells) > 2 else ""
                
                # 跳过标题行和占位符行
                if name in ('名称', '-', '名'):
                    continue
                if param_type in ('类型', '-'):
                    continue
                
                params.append({
                    "name": name,
                    "type": param_type,
                    "description": description
                })
    
    return params


def generate_md5(text: str) -> str:
    """
    生成文本的 MD5 签名
    
    用于增量更新判断：只有当描述发生变化时才重新生成 Embedding
    
    Args:
        text: 输入文本
    
    Returns:
        MD5 哈希值（32位十六进制字符串）
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def save_embedding_texts(apis: List[Dict], output_path: str) -> None:
    """
    保存 embedding_text 到新文件
    
    每行一个接口：接口名\t embedding_text
    
    Args:
        apis: 接口列表
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for api in apis:
            f.write(f"{api['name']}\t{api['embedding_text']}\n")
    
    print(f"[api_loader] 已保存 {len(apis)} 条 embedding_text 到 {output_path}")


def normalize_text(text: str) -> str:
    """
    标准化中文文本（用于关键词匹配）
    
    处理步骤：
        1. 移除多余空格
        2. 全角转半角
        3. 转小写
    
    Args:
        text: 输入文本
    
    Returns:
        标准化后的文本
    
    参考：nacos-mcp-router/mcp_manager.py:205-223
    """
    import unicodedata
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 全角转半角
    text = unicodedata.normalize('NFKC', text)
    
    # 移除所有空格
    text = text.replace(' ', '').replace('　', '')
    
    # 转小写
    return text.lower()


# ========== 测试代码 ==========
if __name__ == "__main__":
    # 测试加载
    csv_path = "../api/1_stock_enriched.csv"
    
    if os.path.exists(csv_path):
        apis = load_enriched_csv(csv_path)
        
        # 打印前 3 个接口的信息
        print("\n===== 前 3 个接口 =====")
        for api in apis[:3]:
            print(f"\n接口: {api['name']}")
            print(f"分类: {api['category']}")
            print(f"Embedding 文本: {api['embedding_text'][:100]}...")
            print(f"MD5: {api['md5']}")
            print("-" * 50)
    else:
        print(f"测试文件不存在: {csv_path}")
