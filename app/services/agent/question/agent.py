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
from app.services.agent.core.schema import AgentEventType, AgentMessageEvent, AgentMessageData
from app.services.agent.question.schema import QuestionAgentResult
from app.services.common.memory import MemoryService
from app.services.common.grammar import GrammarService
from app.services.common.story import StoryService
from app.services.common.mistake import MistakeService
from app.services.common.vocab import VocabService
class QuestionAgent(CoreAgent):
    """
    使用 OPAR (观察、计划、行动、反思) 循环的问题生成代理。
    
    该类用于根据用户状态和输入生成个性化的语言学习题目。
    """
    
    def __init__(self):
        super().__init__()
        # 题目
        self.question_stack = QuestionStack()
        self.memory_service = MemoryService()
        self.grammar_service = GrammarService()
        self.story_service = StoryService()
        self.mistake_service = MistakeService()
        self.vocab_service = VocabService()
        self.user_input = ""
        self.plan_result = ""
        self.observe_result = ""
        
        
    # 实现run方法
    async def run(self, user_input: str) -> List[QuestionUnion]:
        """
        运行完整的 OPAR 循环并根据用户输入生成问题。
        
        该方法协调整个问题生成过程，包括观察、计划、行动和反思阶段。
        """
        
        # 执行OPAR循环
        self.user_input = user_input
        self.observe_result =  await self._observe(user_input)
        self.plan_result = await self._plan_question()        
        questions = await self._generate_question()
        self.finish(QuestionAgentResult(data=questions))
        return questions
        
    
    async def _observe(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        self.message(AgentMessageData(
                emoji="🔍",
                message=user_input
            )
        )
        # 创建Agent
        observe_agent = create_react_agent(
            model=self.low_model,
            tools=[
                make_search_resource_tool()
            ],
            checkpointer=self.checkpointer
        )
        # 6. 运行 Agent - 第一个问题
        config = {"configurable": {"thread_id": "1"}}
        response = await observe_agent.ainvoke(
            {"messages": [
                {"role": "system", "content": f"""
你是一个语言学习平台的智能观察代理。, 用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
你的任务是分析在当前请求下的用户画像, 如果没有找到当前的画像, 你可以回答没找到, 但是不要进行编造

需要考虑以下几点：
1. 用户当前的水平和学习目标是什么
2. 你应该知道用户喜欢哪些东西, 想要学会语言最重要的是和生活与爱好相关的契机
3. 你应该知道用户可能会在什么地方发生错误, 应该怎么去检索这些错误记录, 应该检索哪些错误相关的内容

你应该用{self.uow.accept_language}语言回答你做了什么
                """},
                {"role": "user", "content": f"""
user's memory count and category: {self.memory_service.get_user_memory_categories_with_number()}
"""},
                {"role": "user", "content": user_input},
            ]},
            config
        )
        last_message = response["messages"][-1]
        print(last_message.content)
        self.message(AgentMessageData(
                    emoji="🔍",
                    message=last_message.content
            )
        )
        return last_message.content
    # 计划问题
    async def _plan_question(self) -> str:
        """
        计划问题
        """
        # 创建agent
        plan_agent = create_react_agent(
            model=self.low_model,
            tools=[],
            checkpointer=self.checkpointer
        )
        # 6. 运行 Agent - 第一个问题
        config = {"configurable": {"thread_id": "1"}}
        response = await plan_agent.ainvoke(
            {"messages": [
                {"role": "system", "content": f"""
你是一个语言学习平台的智能题目计划代理
用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
你的任务是根据用户的画像和用户的请求生成一个计划, 计划生成怎么样的请求

计划的内容包括
用户应该针对哪些内容进行练习
用户可能喜欢什么, 喜欢的内容应该怎么穿插在题目里, 如果用户画像里没有相关的内容,请忽略这一条
用户最近可能在做什么, 题目应该怎么融合用户正在做的或者未来可能做的事情的场景, 如果用户画像里没有相关的内容,请忽略这一条
用户的水平怎么样, 针对用户请求的问题, 怎么制定题目会让用户学到东西又不至于太难
用户画像如下:
{self.observe_result}
                    """},
                
                {"role": "user", "content": self.user_input}
            ]},
            config
        )
        last_message = response["messages"][-1]
        self.message(AgentMessageData(
                    emoji="📋",
                    message=last_message.content
            )
        )
        return last_message.content
        # 6. 运行 Agent - 第一个问题
    # 生成问题
    async def _generate_question(self) -> List[QuestionUnion]:
        """
        生成问题
        """
        #创建agent
        generate_agent = create_react_agent(
            model=self.low_model,
            tools=[
                # 添加question_stack的工具
                *self.question_stack.get_tools()
            ],
            checkpointer=self.checkpointer
        )
        # 6. 运行 Agent - 第一个问题
        config = {"configurable": {"thread_id": "1"}}
        response = await generate_agent.ainvoke(
            {"messages": [
                {"role": "system", "content": f"""
你是一个语言学习平台的智能题目生成代理
用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
你的任务是根据计划生成7-10个题目

你应该保证题型的多元化,不能只有一种题目
题目需要满足练习的要求
题目应该符合用户的喜好和水平
题目应该答案唯一, 不能有多个答案
题目应该有指向性, 不能是开放性问题
题目应该只包含语言学习, 不能包含其他内容,比如专业知识

题目不应该放在回答里, 应该只通过工具调用生成
回答应该不包含题目的内容, 只包含你做了什么
                    """},
                
                {"role": "user", "content": self.plan_result}
            ]},
            config
        )
        last_message = response["messages"][-1]
        self.message(AgentMessageData(
                    emoji="🤔",
                    message=last_message.content
            )
        )
        print(self.question_stack.get_questions_prompt())
        return self.question_stack.questions