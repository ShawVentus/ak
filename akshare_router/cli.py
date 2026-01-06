#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行工具

模块功能：
    提供命令行界面测试 AkShare API 路由功能。
    支持单次查询和交互式对话模式。

使用方法：
    # 单次查询
    python cli.py "平安银行的K线数据"
    
    # 交互模式
    python cli.py --interactive
    
    # 指定 Top-K
    python cli.py "港股行情" --top-k 10
"""

import argparse
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI

from src.config import Config
from src.api_loader import load_enriched_csv
from src.embedding_adapter import create_embedding_adapter
from src.vector_store import VectorStore
from src.router import Router
from src.conversation import ConversationManager


def initialize_system(config: Config, csv_path: str):
    """
    初始化系统组件
    
    Args:
        config: 配置对象
        csv_path: enriched CSV 文件路径
    
    Returns:
        tuple: (vector_store, router, apis)
    """
    print("[cli] 正在初始化系统...")
    
    # 1. 加载接口数据
    print(f"[cli] 加载接口数据: {csv_path}")
    apis = load_enriched_csv(csv_path)
    
    # 2. 创建 Embedding 适配器
    print("[cli] 创建 Embedding 适配器...")
    embedding_fn = create_embedding_adapter()
    
    # 3. 初始化向量库
    chroma_dir = config.get_absolute_chroma_dir(
        os.path.dirname(os.path.abspath(__file__))
    )
    print(f"[cli] 初始化向量库: {chroma_dir}")
    vector_store = VectorStore(embedding_fn, chroma_dir)
    
    # 4. 构建索引
    print("[cli] 构建向量索引...")
    vector_store.build_index(apis)
    
    # 5. 加载缓存（确保内存中有完整数据）
    vector_store.reload_cache(apis)
    
    # 6. 创建 LLM 客户端和路由器
    print("[cli] 创建 LLM 路由器...")
    llm_client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL
    )
    router = Router(llm_client, config)
    
    print("[cli] 初始化完成！")
    return vector_store, router, apis


def run_single_query(query: str, conversation: ConversationManager):
    """
    执行单次查询
    
    Args:
        query: 用户查询
        conversation: 对话管理器
    """
    print(f"\n{'='*60}")
    print(f"查询: {query}")
    print('='*60)
    
    response = conversation.handle_message(query)
    
    print(f"\n响应:\n{response}")
    print('='*60)


def run_interactive_mode(conversation: ConversationManager):
    """
    交互式对话模式
    
    Args:
        conversation: 对话管理器
    """
    print("\n" + "="*60)
    print("AkShare API 路由系统 - 交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'reset' 重置对话")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见！")
                break
            
            if user_input.lower() == 'reset':
                conversation.reset()
                print("[系统] 对话已重置")
                continue
            
            response = conversation.handle_message(user_input)
            print(f"\n助手: {response}\n")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="AkShare API 路由系统命令行工具"
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="查询文本（如果不提供则进入交互模式）"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="进入交互模式"
    )
    
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="检索返回的候选数量（默认 5）"
    )
    
    parser.add_argument(
        "--csv-path",
        type=str,
        default="../api/1_stock_enriched.csv",
        help="enriched CSV 文件路径"
    )
    
    parser.add_argument(
        "--env-path",
        type=str,
        default=None,
        help=".env 文件路径（默认自动查找）"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config.load(args.env_path)
    config.TOP_K = args.top_k
    
    # 验证 API Key
    if not config.validate_api_key():
        print("错误: 请先配置 OPENAI_API_KEY")
        print("提示: 复制 .env.example 为 .env 并填入 API Key")
        sys.exit(1)
    
    # 解析 CSV 路径
    csv_path = args.csv_path
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            csv_path
        )
    
    if not os.path.exists(csv_path):
        print(f"错误: CSV 文件不存在: {csv_path}")
        sys.exit(1)
    
    # 初始化系统
    vector_store, router, apis = initialize_system(config, csv_path)
    
    # 创建对话管理器
    conversation = ConversationManager(vector_store, router, config)
    
    # 运行
    if args.interactive or args.query is None:
        run_interactive_mode(conversation)
    else:
        run_single_query(args.query, conversation)


if __name__ == "__main__":
    main()
