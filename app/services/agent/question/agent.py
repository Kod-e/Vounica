from __future__ import annotations

"""
使用 OPAR 循环实现的 QuestionAgent 类。

OPAR (观察、计划、行动、反思) 循环是一种问题生成的方法论，用于创建针对用户的个性化问题。
"""

from typing import Any, Dict, List, Optional, Tuple, cast
import json

from app.services.agent.core.core import CoreAgent
from app.infra.context import uow_ctx
from app.llm import chat_completion, LLMModel
from app.services.question.types import QuestionUnion
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from app.services.tools.langchain import make_search_resource_tool, QuestionStack, LoopTool
from langchain_openai import ChatOpenAI
import logging, langchain
langchain.debug = True
logging.basicConfig(level=logging.INFO)
from app.services.agent.core.schema import AgentEventType, AgentMessageEvent, AgentMessageData
from app.services.agent.question.schema import QuestionAgentResult

class QuestionAgent(CoreAgent):
    """
    使用 OPAR (观察、计划、行动、反思) 循环的问题生成代理。
    
    该类用于根据用户状态和输入生成个性化的语言学习题目。
    """
    
    def __init__(self):
        super().__init__()
        # 题目
        self.question_stack = QuestionStack()
        
    # 实现run方法
    async def run(self, user_input: str) -> List[QuestionUnion]:
        """
        运行完整的 OPAR 循环并根据用户输入生成问题。
        
        该方法协调整个问题生成过程，包括观察、计划、行动和反思阶段。
        """
        
        # 执行OPAR循环
        observe_result =  await self._observe(user_input)
        questions = await self._generate_question(observe_result)
        self.finish(QuestionAgentResult(data=questions))
        return questions
        
    
    async def _observe(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        # 创建Agent
        loop_tool = LoopTool(max_loop_num=5)
        observe_agent = create_react_agent(
            model=self.model,
            tools=[
                make_search_resource_tool(),
                *loop_tool.tool_call,
            ],
            checkpointer=self.checkpointer
        )
        while loop_tool.is_loop:
            # 6. 运行 Agent - 第一个问题
            config = {"configurable": {"thread_id": "1"}}
            response = await observe_agent.ainvoke(
                {"messages": [
                    {"role": "system", "content": f"""
                    你是一个语言学习平台的智能观察代理。, 用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
                    你的任务是分析当前请求下, 你需要搜索哪些信息才能完成在这个问题下用户的画像
                    并且在数据库进行检索, 当检索完成后, 返回“done”这个string

                    需要考虑以下几点：
                    1. 用户当前的水平和学习目标是什么
                    2. 你应该知道用户喜欢哪些东西, 想要学会语言最重要的是和生活与爱好相关的契机
                    3. 你应该知道用户可能会在什么地方发生错误, 应该怎么去检索这些错误记录, 应该检索哪些错误相关的内容
                    
                    如果你觉得已经检索完成, 请调用stop_loop工具
                    并且返回你对用户在这个场景下的用户画像
                    """},
                    {"role": "user", "content": user_input},
                    {"role": "user", "content": loop_tool.get_loop_prompt()},
                ]},
                config
            )
            last_message = response["messages"][-1]
            print(last_message.content)
            self.message(
                AgentMessageEvent(
                    type=AgentEventType.MESSAGE,
                    data=AgentMessageData(
                        emoji="🔍",
                        message=last_message.content
                    )
                )
            )
            loop_tool.loop()
        return last_message.content
    
    # 生成问题
    async def _generate_question(self, user_input: str) -> List[QuestionUnion]:
        """
        生成问题
        """
        #创建agent
        loop_tool = LoopTool(max_loop_num=5)
        generate_agent = create_react_agent(
            model=self.model,
            tools=[
                # 添加question_stack的工具
                *self.question_stack.get_tools(),
                *loop_tool.tool_call,
            ],
            checkpointer=self.checkpointer
        )
        while loop_tool.is_loop:
            # 6. 运行 Agent - 第一个问题
            config = {"configurable": {"thread_id": "1"}}
            response = await generate_agent.ainvoke(
                {"messages": [
                    {"role": "system", "content": f"""
                     {user_input}
                     你需要根据要求生成7个左右的题目
                     如果你觉得已经生成的不错了, 请调用stop_loop工具
                     """},
                    
                    {"role": "user", "content": self.question_stack.get_questions_prompt()}
                ]},
                config
            )
            last_message = response["messages"][-1]
            self.message(
                AgentMessageEvent(
                    type=AgentEventType.MESSAGE,
                    data=AgentMessageData(
                        emoji="�",
                        message=last_message.content
                    )
                )
            )
            loop_tool.loop()
        
        return self.question_stack.questions