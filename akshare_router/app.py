#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gradio Web 界面

模块功能：
    提供 Web 界面测试 AkShare API 路由功能。
    支持多用户会话隔离。

使用方法：
    python app.py
    
    # 指定端口
    python app.py --port 7861
"""

import argparse
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from openai import OpenAI

from src.config import Config
from src.api_loader import load_enriched_csv
from src.embedding_adapter import create_embedding_adapter
from src.vector_store import VectorStore
from src.router import Router
from src.conversation import ConversationManager


# 全局变量（所有用户共享）
_vector_store = None
_router = None
_config = None


def initialize_globals(config: Config, csv_path: str):
    """
    初始化全局组件（应用启动时调用一次）
    
    Args:
        config: 配置对象
        csv_path: enriched CSV 文件路径
    """
    global _vector_store, _router, _config
    
    print("[app] 正在初始化系统...")
    
    # 1. 保存配置
    _config = config
    
    # 2. 加载接口数据
    print(f"[app] 加载接口数据: {csv_path}")
    apis = load_enriched_csv(csv_path)
    
    # 3. 创建 Embedding 适配器
    print("[app] 创建 Embedding 适配器...")
    embedding_fn = create_embedding_adapter()
    
    # 4. 初始化向量库
    chroma_dir = config.get_absolute_chroma_dir(
        os.path.dirname(os.path.abspath(__file__))
    )
    print(f"[app] 初始化向量库: {chroma_dir}")
    _vector_store = VectorStore(embedding_fn, chroma_dir)
    
    # 5. 构建索引
    print("[app] 构建向量索引...")
    _vector_store.build_index(apis)
    
    # 6. 加载缓存
    _vector_store.reload_cache(apis)
    
    # 7. 创建 LLM 客户端和路由器
    print("[app] 创建 LLM 路由器...")
    llm_client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL
    )
    _router = Router(llm_client, config)
    
    print("[app] 初始化完成！")


def create_conversation() -> ConversationManager:
    """
    创建新的对话管理器（每个用户会话独立）
    
    Returns:
        ConversationManager 实例
    """
    return ConversationManager(_vector_store, _router, _config)


def create_app() -> gr.Blocks:
    """
    创建 Gradio 应用
    
    Returns:
        gr.Blocks 应用对象
    """
    with gr.Blocks(
        title="AkShare API 路由系统",
        theme=gr.themes.Soft()
    ) as app:
        
        # 标题
        gr.Markdown("""
# 🎯 AkShare API 路由系统 (Phase 1a)

输入自然语言查询，系统会自动匹配最合适的 AkShare 接口并提取参数。

**示例查询：**
- "平安银行的日K线数据"
- "港股实时行情"
- "融资融券汇总数据"
        """)
        
        # 会话状态（每个用户独立）
        conversation_state = gr.State(None)
        
        # 聊天界面
        chatbot = gr.Chatbot(
            label="对话历史",
            height=400,
            show_label=True
        )
        
        # 输入区域
        with gr.Row():
            msg = gr.Textbox(
                label="输入查询",
                placeholder="例如：平安银行2023年的K线数据",
                scale=4,
                show_label=False
            )
            submit_btn = gr.Button("发送", variant="primary", scale=1)
        
        # 功能按钮
        with gr.Row():
            clear_btn = gr.Button("清空对话")
            example_btn = gr.Button("加载示例")
        
        # 示例查询
        gr.Examples(
            examples=[
                "平安银行的日K线数据",
                "港股通成份股有哪些",
                "上海证券交易所的融资融券汇总数据",
                "东方财富的财务分析主要指标",
                "深圳证券交易所的行业成交数据",
            ],
            inputs=msg,
            label="示例查询"
        )
        
        # 系统信息
        gr.Markdown("""
---
**Phase 1a 说明：** 当前阶段仅展示路由结果和参数，不执行实际 API 调用。
        """)
        
        def respond(message: str, chat_history: list, conv_manager):
            """
            处理用户消息
            
            Args:
                message: 用户输入
                chat_history: 聊天历史
                conv_manager: 对话管理器
            
            Returns:
                tuple: (清空输入框, 更新的聊天历史, 更新的对话管理器)
            """
            if not message.strip():
                return "", chat_history, conv_manager
            
            # 初始化对话管理器（如果是新会话）
            if conv_manager is None:
                conv_manager = create_conversation()
            
            # 处理消息
            bot_response = conv_manager.handle_message(message)
            
            # 更新聊天历史
            chat_history.append((message, bot_response))
            
            return "", chat_history, conv_manager
        
        def clear_chat():
            """
            清空对话
            
            Returns:
                tuple: (新的对话管理器, 空聊天历史)
            """
            return None, []
        
        def load_examples():
            """
            加载示例查询
            
            Returns:
                示例文本
            """
            return "平安银行2023年的日K线数据"
        
        # 绑定事件
        msg.submit(
            respond,
            inputs=[msg, chatbot, conversation_state],
            outputs=[msg, chatbot, conversation_state]
        )
        
        submit_btn.click(
            respond,
            inputs=[msg, chatbot, conversation_state],
            outputs=[msg, chatbot, conversation_state]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[conversation_state, chatbot]
        )
        
        example_btn.click(
            load_examples,
            outputs=msg
        )
    
    return app


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="AkShare API 路由系统 Web 界面"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=7860,
        help="服务端口（默认 7860）"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="生成公开分享链接"
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
        help=".env 文件路径"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config.load(args.env_path)
    
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
    
    # 初始化全局组件
    initialize_globals(config, csv_path)
    
    # 创建并启动应用
    app = create_app()
    
    print(f"\n启动 Gradio 服务: http://localhost:{args.port}")
    
    app.launch(
        server_port=args.port,
        share=args.share,
        show_error=True
    )


if __name__ == "__main__":
    main()
