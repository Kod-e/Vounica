from __future__ import annotations

"""
使用 OPAR 循环实现的 QuestionAgent 类。

OPAR (观察、计划、行动、反思) 循环是一种问题生成的方法论，用于创建针对用户的个性化问题。
"""

from typing import Any, Dict, List, Optional, Tuple, cast
import json

from app.infra.uow import UnitOfWork
from app.llm import chat_completion, LLMModel
from app.services.question.common.registry import create_question
from app.services.question.common.types import QuestionType
from app.services.common.memory import MemoryService
from app.services.common.mistake import MistakeService
from app.services.common.story import StoryService
from app.services.common.vocab import VocabService
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from app.services.tools.langchain import make_tools
from langchain_openai import ChatOpenAI
import logging, langchain
langchain.debug = True
logging.basicConfig(level=logging.INFO)
class QuestionAgent:
    """
    使用 OPAR (观察、计划、行动、反思) 循环的问题生成代理。
    
    该类用于根据用户状态和输入生成个性化的语言学习题目。
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        # 获取tools
        self.tools = make_tools(uow=uow)
        # 创建checkpointer
        self.checkpointer = InMemorySaver()
        # 实例化 LLM
        self.model = ChatOpenAI(model="gpt-4.1")
        # 创建Agent
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            checkpointer=self.checkpointer
        )
        
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        运行完整的 OPAR 循环并根据用户输入生成问题。
        
        该方法协调整个问题生成过程，包括观察、计划、行动和反思阶段。
        """
        
        # 执行OPAR循环
        await self._observe(user_input)
    
    async def _observe(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        while True:
            # 6. 运行 Agent - 第一个问题
            config = {"configurable": {"thread_id": "1"}}
            response = await self.agent.ainvoke(
                {"messages": [
                    {"role": "system", "content": f"""
                    你是一个语言学习平台的智能观察代理。, 用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
                    你的任务是分析当前请求下, 你需要搜索哪些信息才能完成在这个问题下用户的画像
                    并且在数据库进行检索, 当检索完成后, 返回“done”这个string

                    需要考虑以下几点：
                    1. 用户当前的水平和学习目标是什么
                    2. 你应该知道用户喜欢哪些东西, 想要学会语言最重要的是和生活与爱好相关的契机
                    3. 你应该知道用户可能会在什么地方发生错误, 应该怎么去检索这些错误记录, 应该检索哪些错误相关的内容
                    """},
                    {"role": "user", "content": user_input},
                ]},
                config
            )
            last_message = response["messages"][-1]
            if last_message.content == "done":
                break
            else:
                print(last_message.content)
        return last_message.content