from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, cast, abstractmethod
import json, asyncio
from pydantic import BaseModel
from app.infra.context import uow_ctx
from app.llm import chat_completion, LLMModel
from app.services.agent.core.schema import AgentEventType, AgentEvent, AgentMessageEvent, AgentResultEvent
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from app.services.tools.langchain import make_search_resource_tool, QuestionStack, LoopTool
from langchain_openai import ChatOpenAI
import logging, langchain


class CoreAgent:
    """基础 Agent，提供模型、推送等通用能力。"""

    def __init__(self):
        # UoW 与模型
        self.uow = uow_ctx.get()
        self.model = ChatOpenAI(model=LLMModel.STANDARD.value["name"])
        self.high_model = ChatOpenAI(model=LLMModel.HIGH.value["name"])
        self.low_model = ChatOpenAI(model=LLMModel.LOW.value["name"])
        self.checkpointer = InMemorySaver()
        
        # 消息队列
        self._message_queue: asyncio.Queue = asyncio.Queue()



    # Agent必须要实现run方法, 类似Swift的Protocol, 这个协议必须返回一个合法的pydantic对象
    @abstractmethod
    async def run(self, *args) -> BaseModel:
        raise NotImplementedError("agent must have run method")

    # 暴露内部队列供外层 StreamingResponse 消费
    def get_queue(self) -> asyncio.Queue:
        """暴露内部队列供外层 StreamingResponse 消费。"""
        return self._message_queue
    
    # finish方法, 调用后会发出带result的AgentEvent
    def finish(self, data: BaseModel):
        self._message_queue.put_nowait(AgentResultEvent(data=data))
        
    # message方法, 调用后会发出带message的AgentEvent
    def message(self, data: BaseModel):
        self._message_queue.put_nowait(AgentMessageEvent(data=data))
    
    # 持续向外部stream消息, 每个消息必须是一个AgentEvent对象, 并且可以被直接放到FastAPI的StreamingResponse中
    async def run_stream(self, *args):
        agent_task = asyncio.create_task(self.run(*args))
        # 创建task, 并且
        while True:
            message: AgentEvent = await self._message_queue.get()
            # 发送信息
            yield json.dumps(message.model_dump(), ensure_ascii=False)
            if message.type == AgentEventType.RESULT:
                break
        # 确保AgentTask完成
        await agent_task