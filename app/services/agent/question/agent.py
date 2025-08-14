from __future__ import annotations
from urllib import response

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
        self.finish(QuestionAgentResult(data=self.question_stack.questions))
        return []

    async def _observe(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        # 创建Agent
        observe_agent = create_react_agent(
            model=self.low_model,
            tools=[
                make_search_resource_tool(),
                *self.question_stack.get_tools()
            ],
            checkpointer=self.checkpointer
        )
        # 6. 运行 Agent - 第一个问题
        config = {"configurable": {"thread_id": "1"}}
        payload = {"messages": [
                {"role": "system", "content": f"""
你是一个AI语言学习平台的题目生成Agent(目前开启了开发者模式)

You Can:
1. 使用search_resource获取用户的信息
2. 生成题目放到QuestionStack中


Goal:
- 分析用户的输入, 生成适合用户的题目
- 生成的题目会放到QuestinoStack中, 结束时用户会收到Stack内的所有题目
- 用户正在使用{self.uow.accept_language}学习{self.uow.target_language}语言(ISO 639-1 标准)
Constrains:
- **如果你在过程中发生了任何疑似技术性的错误, 你应该返回错误的信息, 工程师会阅读这个信息并且修复, 所以需要尽可能的详细**
- 在做得到的情况下, 你应该试着从数据库获取用户的喜好
- 如果你找不到任何用户画像, 你应该尝试根据用户的需求给出测试性的练习(如A1-C1之间的渐进难度)
- 你应该在制作过程中告诉用户你做了什么
- 你不应该在给用户的回复中包含任何题目和答案
- 生成的题目应该符合用户的水平


Tools:

search_resouce
这个工具可以检索用户的信息

信息分以下几类
Memory:
- LLM根据用户对题目的回答, 聊天, 记录的用户画像, 这个表完全由LLM管理

Vocab&Grammar:
 - 这个表记录了用户对某个单词/语法的掌握程度
 - name代表这个单词或者语法的名称, 内部字段使用的是用户正在学习的语言记录的
 - usage代表这个单词或者语法的使用场景, 用于区分一个相同的语法的不同场景, 以及用于方便向量查询

Story:
- 这个表记录了用户自己写的一些关于自己的故事

Mistake:
  - 这个表记录了用户的错题集

add_*_question

这一类工具用于添加一个Question到QuestionStack中

                """},
                {"role": "user", "content": f"""
user's memory count and category: {await self.memory_service.get_user_memory_categories_with_number()}
"""},
                {"role": "user", "content": user_input},
            ]}
        await self.run_stream_events(
            agent=observe_agent,
            payload=payload,
            config=config,
        )
        return "生成完成"