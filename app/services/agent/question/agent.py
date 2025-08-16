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
from app.services.agent.core.schema import AgentMessageEvent,AgentResultEvent,AgentMessageData
from app.services.agent.question.schema import QuestionAgentResult,QuestionAgentEvent
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
        await self._make_questions(user_input)        
        self.event(
            QuestionAgentResult(
                data = self.question_stack.questions
            ))
        return self.question_stack.questions

    async def _make_questions(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        # 创建Agent
        question_agent = create_react_agent(
            model=self.high_model,
            tools=[
                make_search_resource_tool(),
                self.question_stack.build_delete_question_tool(),
                self.question_stack.build_get_questions_prompt_tool(),
                *self.question_stack.get_tools()
            ],
            checkpointer=self.checkpointer
        )
        # 6. 运行 Agent - 第一个问题
        config = {"configurable": {"thread_id": "1"}}
        payload = {"messages": [
                {"role": "system", "content": f"""
你是一个AI语言学习平台的题目生成Agent

#You Can:
1. 使用search_resource获取用户的信息
2. 生成题目放到QuestionStack中


#Goal:
- 分析用户的输入, 生成适合用户的题目
- 在你认为生成完题目后, 使用get_questions工具检查Question是否符合QuestionRule
- 如果Question不符合QuestionRule, 你应该删除QuestionStack中的题目, 并且重新生成题目, 之后检查, 直到符合QuestionRule为止
- 用户正在使用{self.uow.accept_language}学习{self.uow.target_language}语言(ISO 639-1 标准)

#Constrains:
- 在做得到的情况下, 你应该试着从数据库获取用户的喜好
- 如果你找不到任何用户画像, 你应该制作一套测试性的题目, 从最简单到最难(如A1-C1之间的渐进难度)
- 你应该在制作过程中告诉用户你做了什么
- 生成的题目应该符合用户的水平, 并且针对用户可能的薄弱点进行训练

#QuestionRule:
- 用户对corrent_answer不可见, 你应该只把答案安全的放到这个里面
- 题目的答案不能在corrent_answer外出现
- 用户不能在不掌握题目的实际知识的情况下, 通过推理已有的内容(如steam, choice)直接得出答案
- 题目的答案应该唯一
- 题目的答案应该正确
- 题目的答案应该明确, 不应该存在歧义
- 题目应该只出现用户使用的语言和目标语言, 不应该出现其他语言
- 你应该在初级题目中, 只使用用户的母语制作题干, 因为初级用户使用者可能可以读懂题目却无法理解题干
- 你可以在高级题目中使用目标语言制作题干
- **题目应该兼顾语法和词汇**
- **题目应该有多样性**

#错误的Question例子

##Stem: What is the capital of the moon(Eclipse City)? 
Correct Answer: The capital of the moon is called 'Eclipse City'
Choices: 
A. Eclipse City
B. New World
C. City of Light
- 题目的stem中出现了“Eclipse City”, 用户可以直接通过stem推理出答案, 因此这是一个错误的题目

##Stem: 请选择thanks在日语中对应的意思
用户正在使用cn学习ja语言(ISO 639-1 标准)
Correct Answer: ありがとう
Choices: 
A. ありがとう
B. おはよう
C. ありがとう
- 在这个题目中, 用户只使用cn和ja, 但是stem使用英语询问了“thanks”的意思, 你不应该要求用户会使用其他语言, 即使是英语

#QuestionType

##Choice
生成选择题, 用户从多个选项中选择一个正确答案

##Match
生成连线题, 用户将左边的和右边的答案进行匹配
用户那里会在左边和右边分别显示4个Tab, 并且将左边的和右边的Tab进行匹配

##Assembly
生成分散的词语拼接成完整句子的题目
stem应该是一个要求, 或者母语的句子, 例如
corrent_anwser表示怎么拼接是正确的
options表示给用户的选项, 这里混杂着正确答案的部分单词(可以视为token), 干扰项, 可以不和corrent_answer一样长, 但是一定可以拼出corrent_answer
options或者correct_answer中, 不应该出现标点符号
Stem: Transformer 是一种神经网络模型
correct_answer : [Transformer, is, a, model, of, neural, network]
options: [Transformer, network, of, schema, bugs, neural, is, a, model]

Tools:

- search_resouce
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

- delete_question
这个工具用于删除QuestionStack中的一个题目

- get_questions
这个工具用于获取QuestionStack中的所有题目, 并且以多行文本的形式返回
                """},
                {"role": "system", "content": f"""
#User Info
- 这里记载了User在数据库中记录了多少信息, 如果你使用search_resource工具, 会在下方列出的信息内检索
{await self.memory_service.get_user_memory_count_prompt_for_agent()}
{await self.story_service.get_user_story_count_prompt_for_agent()}
{await self.mistake_service.get_user_mistake_count_prompt_for_agent()}
{await self.vocab_service.get_user_vocab_count_prompt_for_agent()}
{await self.grammar_service.get_user_grammar_count_prompt_for_agent()}
"""},
                {"role": "system", "content": f"""
{await self.memory_service.get_user_memory_summary_prompt_for_agent()}
"""},
                {"role": "system", "content": f"""
{await self.story_service.get_user_story_summary_prompt_for_agent()}
"""},
                {"role": "user", "content": user_input},
            ]}
        await self.run_stream_events(
            agent=question_agent,
            payload=payload,
            config=config,
        )