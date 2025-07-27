from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse
from app.infra.uow import UnitOfWork
from app.llm.models import LLMModel, OPENAI_MODEL_STADARD, OPENAI_EMBED_MODEL

load_dotenv()

# API密钥配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIClient:
    """OpenAI API客户端封装"""

    def __init__(
        self,
        api_key: str = OPENAI_API_KEY,
        default_model: str = OPENAI_MODEL_STADARD,
        default_embed_model: str = OPENAI_EMBED_MODEL,
    ) -> None:
        # 初始化OpenAI客户端
        self._client = OpenAI(api_key=api_key)
        self.default_model = default_model
        self.default_embed_model = default_embed_model
    
    # 聊天补全接口
    def chat(self, *, messages: List[Dict[str, Any]], uow: UnitOfWork, model_type: LLMModel = LLMModel.STANDARD, **kwargs) -> ChatCompletion:
        """
        调用聊天补全API并返回原始响应
        
        参数:
            messages: 发送给模型的消息列表
            uow: 用于令牌追踪的工作单元
            model_type: 模型类型枚举，用于指定使用哪个模型
            **kwargs: 传递给OpenAI API的额外参数
        """
        # 检查用户token余额是否大于0
        uow.quota.check()
        # 确定使用的模型
        model = model_type.model_name
        # 调用API并返回结果, 并计算token使用量
        data: ChatCompletion = self._client.chat.completions.create(model=model, messages=messages, **kwargs)
        # 消费token
        uow.quota.consume(data.usage.total_tokens * model_type.price)
        # 返回结果
        return data

    # 文本向量化接口
    def embed(self, text: str, uow: UnitOfWork, model_type: LLMModel = LLMModel.EMBED, **kwargs) -> List[float]:
        """
        将文本转换为向量表示
        
        参数:
            text: 需要向量化的文本
            uow: 用于令牌追踪的工作单元
            model_type: 模型类型枚举
            **kwargs: 额外参数
        """
        # 检查用户token余额是否大于0
        uow.quota.check()
        # 确定使用的嵌入模型
        model = model_type.model_name
        # 调用嵌入API并返回向量
        resp: CreateEmbeddingResponse = self._client.embeddings.create(model=model, input=text, **kwargs)
        # 消费token
        uow.quota.consume(resp.usage.total_tokens * model_type.price)
        # 返回结果
        return resp.data[0].embedding


# 创建默认客户端实例
_default_client = OpenAIClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    default_model=os.getenv("OPENAI_MODEL", "o4-mini"),
    default_embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
)

# 导出默认客户端的方法
chat_completion = _default_client.chat
embed = _default_client.embed