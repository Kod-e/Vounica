from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai.types.create_embedding_response import CreateEmbeddingResponse
from langchain_core.messages import BaseMessage
from app.infra.context import uow_ctx
from app.llm.models import LLMModel
from langchain_core.language_models import LanguageModelInput
from langchain_openai import ChatOpenAI
from openai import OpenAI
load_dotenv()

# API密钥配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_MAP = {
    LLMModel.HIGH: ChatOpenAI(model=LLMModel.HIGH.model_name),
    LLMModel.STANDARD: ChatOpenAI(model=LLMModel.STANDARD.model_name),
    LLMModel.LOW: ChatOpenAI(model=LLMModel.LOW.model_name),
}
OPENAI_NAVITE_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
class OpenAIClient:
    """OpenAI API客户端封装"""
    # 聊天补全接口
    @staticmethod
    async def chat(input: LanguageModelInput, model_type: LLMModel = LLMModel.STANDARD, **kwargs) -> BaseMessage:
        """
        调用聊天补全API并返回原始响应
        """
        uow = uow_ctx.get()
        # 检查用户token余额是否大于0
        await uow.quota.check()
        # 调用API并返回结果, 并计算token使用量
        response: BaseMessage = MODEL_MAP[model_type].invoke(input, **kwargs)
        # 消费token
        await uow.quota.consume(int(response.response_metadata['token_usage']['total_tokens']) * model_type.price)
        # 返回结果
        return response
    
    #消费接口
    @staticmethod
    async def consume(response: BaseMessage, model_type: LLMModel = LLMModel.STANDARD, **kwargs) -> None:
        """
        消费token
        """
        uow = uow_ctx.get()
        # 消费token
        await uow.quota.consume(int(response.response_metadata['token_usage']['total_tokens']) * model_type.price)

    # 文本向量化接口
    @staticmethod
    async def embed(text: str, model_type: LLMModel = LLMModel.EMBED, **kwargs) -> List[float]:
        """
        将文本转换为向量表示
        
        参数:
            text: 需要向量化的文本
            uow: 用于令牌追踪的工作单元
            model_type: 模型类型枚举
            **kwargs: 额外参数
        """
        uow = uow_ctx.get()
        # 检查用户token余额是否大于0
        await uow.quota.check()
        # 确定使用的嵌入模型
        model = model_type.model_name
        # 调用嵌入API并返回向量
        resp: CreateEmbeddingResponse = OPENAI_NAVITE_CLIENT.embeddings.create(model=model, input=text, **kwargs)
        # 消费token
        await uow.quota.consume(resp.usage.total_tokens * model_type.price)
        # 返回结果
        return resp.data[0].embedding

chat_completion = OpenAIClient.chat
embed = OpenAIClient.embed