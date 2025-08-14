from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, cast, abstractmethod
from langgraph.graph.state import CompiledStateGraph
import json, asyncio
from pydantic import BaseModel
from app.infra.context import uow_ctx
from app.llm import chat_completion, LLMModel
from app.services.agent.core.schema import *
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
        # 最后的Event
        self.last_event: Optional[AgentEvent] = None
        # 消息队列
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._loop = asyncio.get_running_loop()
        
        # stream缓存
        self.stream_cache: str = ""
        
        # 是否正在stream
        self.is_streaming: bool = False



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
        event = AgentMessageEvent(type=AgentEventType.MESSAGE, data=data)
        self._loop.call_soon_threadsafe(self._message_queue.put_nowait, event)
    # event 方法, 代替message方法, 直接发出AgentEvent
    def event(self, event: AgentEvent):
        self._loop.call_soon_threadsafe(self._message_queue.put_nowait, event)
    # 持续向外部stream消息, 每个消息必须是一个AgentEvent对象, 并且可以被直接放到FastAPI的StreamingResponse中
    async def run_stream(self, *args):
        agent_task = asyncio.create_task(self.run(*args))
        # 创建task, 并且
        while True:
            message: AgentEvent = await self._message_queue.get()
            # 发送信息
            yield message
            if message.type == AgentEventType.RESULT:
                break
        # 确保AgentTask完成
        await agent_task
    
    # 持续向外部发送stream event, 通过agent和payload, config
    async def run_stream_events(self, agent:CompiledStateGraph , payload: Dict[str, Any], config: Dict[str, Any]):
        async for ev in agent.astream_events(payload, config=config, version="v2"):
            t = ev["event"]
            name = ev.get("name")  # 哪个节点/模型/工具
            data = ev.get("data", {})

            if t == "on_chat_model_start":
                self.event(AgentThinkingEvent())
            elif t == "on_chat_model_stream":
                if self.is_streaming == False:
                    self.is_streaming = True
                    self.stream_cache = ""
                chunk = data.get("chunk")
                # 兼容 AIMessageChunk 或 provider 自定义结构
                text = getattr(chunk, "content", None)
                if text:
                    self.stream_cache += text
                    self.event(AgentStreamChunkEvent(
                        data=AgentStreamChunkData(chunk=text)
                    ))

            elif t == "on_chat_model_end":
                # self.message(AgentMessageData(
                #     emoji="💬",
                #     message=self.stream_cache
                # ))
                self.event(AgentStreamEndEvent())
                self.is_streaming = False

            elif t == "on_tool_end":
                self.event(AgentToolCallEvent(
                    data = AgentToolData(
                        tool_name=name,
                        tool_input="test"
                    )
                ))

            elif t == "on_chain_end":
                # 整个子链/节点收尾
                if self.last_event:
                    self.event(self.last_event)
            
            print("event",t,"name", name, "data")