"""
Implement the Question Agent using LangChain.

LangChain を使って Question Agent を実装します。
"""

from typing import Dict, List, Any, Optional, Callable, Awaitable
import os
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock

# 修复导入路径
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.react.base import create_react_agent
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from langchain_core.language_models import BaseLLM
from langchain_core.pydantic_v1 import BaseModel, Field

from app.infra.uow import UnitOfWork
from app.llm import LLMModel
from app.services.tools.function.search import search_resource
from app.services.common.memory import MemoryService
from app.services.common.mistake import MistakeService
from app.services.common.vocab import VocabService
from app.services.common.story import StoryService


class SearchInput(BaseModel):
    """
    Search input for the search tool.
    
    検索ツールのための入力です。
    """
    resource: str = Field(description="Resource type to search for")
    field: str = Field(description="Field name to search within")
    query: str = Field(description="Query string to search with")
    method: str = Field(description="Search method (regex or vector)", default="regex")
    limit: int = Field(description="Max number of results to return", default=20)


def get_search_tool(uow: UnitOfWork) -> Tool:
    """
    Create a search tool for the agent.
    
    Agent のための検索ツールを作成します。
    """
    async def search_func(input_str: str) -> str:
        try:
            # Parse the input string as JSON
            input_data = SearchInput.parse_raw(input_str)
            # Call the search_resource function
            results = await search_resource(
                uow=uow,
                resource=input_data.resource,
                field=input_data.field,
                query=input_data.query,
                method=input_data.method,
                limit=input_data.limit
            )
            return str(results)
        except Exception as e:
            return f"Error searching resource: {str(e)}"
    
    return Tool(
        name="search_resource",
        description="""
Search for resources in the database.
Resource types: vocab, grammar, mistakes, stories, memories
Fields depend on resource type:
- vocab: name, usage
- grammar: name, usage
- memory: content
- story: content, summary, category
- mistake: question, answer, correct_answer, error_reason
Method can be 'regex' or 'vector'
        """,
        func=search_func,
        args_schema=SearchInput
    )


class LangChainQuestionAgent:
    """
    Question Agent implementation using LangChain.
    
    LangChain を使った Question Agent の実装です。
    """
    
    def __init__(self, uow: UnitOfWork, model_type: LLMModel = LLMModel.STANDARD):
        """
        Initialize the agent with the unit of work and model type.
        
        Agent を Unit of Work とモデルタイプで初期化します。
        """
        self.uow = uow
        self.model_type = model_type
        
        # 使用模型配置
        model_name = model_type.value["name"]
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name=model_name
        )
        
        # 设置工具
        self.tools = [get_search_tool(uow)]
        
        # 存储OPAR循环的状态和结果
        self.observation_results = []
        self.plan_results = {}
        self.action_results = []
        self.reflection_result = None
        
        # 调试模式
        self.debug = False
    
    async def _is_new_user(self) -> bool:
        """
        Check if the current user is a new user.
        
        現在のユーザーが新しいユーザーかどうかを確認します。
        """
        # Get user memories and check if they exist
        memories = await MemoryService(self.uow).get_user_memories_list(limit=1)
        return len(memories) == 0
    
    async def _observe(self, user_input: str) -> None:
        """
        Observation stage: collect and analyze information about the user.
        
        観察段階: ユーザーに関する情報を収集し、分析します。
        """
        # 获取用户相关数据
        memories = await MemoryService(self.uow).get_user_memories_list(limit=20)
        memory_categories = await MemoryService(self.uow).get_user_memory_categories_with_number()
        mistakes = await MistakeService(self.uow).get_user_mistakes(limit=5)
        
        # 构建观察阶段提示词
        observe_prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个语言学习平台的智能观察代理，用户正在学习目标语言。
你的任务是分析当前请求下，需要搜索哪些信息才能完成用户的画像，并返回需要在数据库检索的内容。

需要考虑以下几点：
1. 用户当前的水平和学习目标是什么
2. 用户喜欢哪些东西，想要学会语言最重要的是和生活与爱好相关的契机
3. 用户可能会在什么地方发生错误，应该怎么去检索这些错误记录

你可以使用search_resource工具搜索以下资源：
- vocab (词汇): 可搜索name和usage字段
- grammar (语法): 可搜索name和usage字段
- memory (记忆): 可搜索content字段
- story (故事): 可搜索content、summary和category字段
- mistake (错题): 可搜索question、answer、correct_answer和error_reason字段

请主动搜索相关资源，以获取更准确的上下文信息。
            """),
            ("user", """
下面附带了一些AI对用户的画像，全部都是由AI主动记录的
关于这个用户当前语言的最重要的最近的记忆: {memories}
用户记忆的category和数量：{memory_categories}
关于这个用户当前语言的最近的错题：{mistakes}

用户请求：{user_input}
分析这个请求并主动搜索相关学习资源。
            """)
        ])
        
        # 创建ReAct代理
        agent = create_react_agent(self.llm, self.tools, observe_prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.debug,
            handle_parsing_errors=True
        )
        
        # 运行代理
        response = await agent_executor.ainvoke({
            "memories": memories,
            "memory_categories": memory_categories,
            "mistakes": mistakes,
            "user_input": user_input,
        })
        
        # 存储观察结果
        self.observation_results = response["output"]
    
    async def _plan(self) -> None:
        """
        Planning stage: plan the questions based on observations.
        
        計画段階: 観察に基づいて問題を計画します。
        """
        # 构建计划阶段提示词
        plan_prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是语言学习平台的问题规划代理。
根据观察结果，为用户规划一组问题。

需要确定：
1. 生成多少问题（推荐5-10题）
2. 包含哪些类型的问题（选择题、填空题、自由回答等）
3. 基于用户历史和学习需求的重点领域
4. 适合用户的难度级别

可用的问题类型：
- choice：选择题
- match_audio：音频和文本匹配
- match_native：母语和目标语言匹配
- cloze：填空题
- order：句子排序
- free：自由回答
- free_limit：带有指定词汇/语法的自由回答
- roleplay：角色扮演以达成目标

请返回JSON格式的计划，包含question_count、question_types、difficulty和focus字段。
            """),
            ("user", "观察结果：\n{observations}\n\n请创建问题生成计划。")
        ])
        
        # 创建计划链
        plan_chain = LLMChain(llm=self.llm, prompt=plan_prompt)
        
        # 运行计划链
        response = await plan_chain.ainvoke({"observations": self.observation_results})
        
        # 解析计划结果
        try:
            self.plan_results = json.loads(response["text"])
        except:
            # 解析失败时使用默认计划
            self.plan_results = {
                "question_count": 5,
                "question_types": ["choice", "cloze", "free"],
                "difficulty": "beginner",
                "focus": "general_assessment"
            }
    
    async def _act(self) -> None:
        """
        Action stage: generate questions based on the plan.
        
        行動段階: 計画に基づいて問題を生成します。
        """
        # 重置行动结果
        self.action_results = []
        
        # 获取计划参数
        question_count = self.plan_results.get("question_count", 5)
        question_types = self.plan_results.get("question_types", ["choice"])
        difficulty = self.plan_results.get("difficulty", "beginner")
        focus = self.plan_results.get("focus", "general")
        
        # 构建行动阶段提示词
        act_prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个语言学习平台的问题生成代理。
生成一个具有以下参数的问题：
- 难度：{difficulty}
- 重点领域：{focus}
- 问题类型：{question_type}

包括问题所需的所有必要信息，例如：
- 问题文本
- 答案选项（对于选择题）
- 正确答案
- 解释为什么答案是正确的

请以JSON格式返回问题数据。
            """),
            ("user", """
请生成第{q_num}题（共{total}题）。
使用以下观察结果和计划作为上下文：

观察结果：
{observations}

计划：
{plan}
            """)
        ])
        
        # 创建行动链
        act_chain = LLMChain(llm=self.llm, prompt=act_prompt)
        
        # 生成问题
        for i in range(question_count):
            # 选择问题类型
            q_type = question_types[i % len(question_types)]
            
            # 运行行动链
            response = await act_chain.ainvoke({
                "difficulty": difficulty,
                "focus": focus,
                "question_type": q_type,
                "q_num": i + 1,
                "total": question_count,
                "observations": self.observation_results,
                "plan": self.plan_results
            })
            
            # 解析和存储问题
            try:
                question_data = json.loads(response["text"])
                # 如果没有问题类型则添加
                if "question_type" not in question_data:
                    question_data["question_type"] = q_type
                self.action_results.append(question_data)
            except:
                # 如果解析失败，存储原始文本
                self.action_results.append({
                    "question_type": q_type,
                    "raw_data": response["text"]
                })
    
    async def _reflect(self) -> bool:
        """
        Reflection stage: evaluate the generated questions.
        
        反省段階: 生成された問題を評価します。
        """
        # 构建反思阶段提示词
        reflect_prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一个语言学习平台的反思代理。
评估生成的问题的质量和适合度。

考虑以下几点：
1. 问题是否符合用户的学习需求和水平？
2. 问题是否多样化且有吸引力？
3. 问题是否存在任何问题（歧义、错误等）？
4. 总体而言，这些问题是否适合用户？

提供详细评估，并确定这些问题是否可以呈现给用户。
如果不行，请指明应该重试哪个阶段："observe"、"plan"或"act"。

请以JSON格式返回评估结果，包含is_valid（布尔值）、reason（字符串）和stage_to_retry（字符串，可选）字段。
            """),
            ("user", """
原始用户请求：{user_input}

观察结果：
{observations}

计划：
{plan}

生成的问题：
{questions}

请评估这些问题并确定它们是否合适。
            """)
        ])
        
        # 创建反思链
        reflect_chain = LLMChain(llm=self.llm, prompt=reflect_prompt)
        
        # 运行反思链
        response = await reflect_chain.ainvoke({
            "user_input": self.user_input,
            "observations": self.observation_results,
            "plan": self.plan_results,
            "questions": self.action_results
        })
        
        # 解析反思结果
        try:
            self.reflection_result = json.loads(response["text"])
        except:
            # 解析失败时使用默认结果
            self.reflection_result = {
                "is_valid": True,
                "reason": "Generated questions seem appropriate."
            }
        
        return self.reflection_result.get("is_valid", True)
    
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        Run the complete OPAR cycle to generate questions.
        
        OPAR サイクルを実行して問題を生成します。
        """
        # 存储用户输入
        self.user_input = user_input
        
        # 执行OPAR循环
        await self._observe(user_input)
        await self._plan()
        await self._act()
        is_valid = await self._reflect()
        
        # 处理重试
        retries = 0
        max_retries = 2
        
        while not is_valid and retries < max_retries:
            stage_to_retry = self.reflection_result.get("stage_to_retry", "act")
            
            if stage_to_retry == "observe":
                await self._observe(user_input)
                await self._plan()
                await self._act()
            elif stage_to_retry == "plan":
                await self._plan()
                await self._act()
            elif stage_to_retry == "act":
                await self._act()
            
            is_valid = await self._reflect()
            retries += 1
        
        # 返回最终结果
        return {
            "questions": self.action_results,
            "is_valid": is_valid,
            "context": {
                "user_is_new": await self._is_new_user(),
                "observations": self.observation_results,
                "plan": self.plan_results,
                "reflection": self.reflection_result
            }
        }


# 简单演示函数，便于快速测试
async def run_simple_demo():
    """
    Run a simple demo of the LangChain Question Agent with minimal dependencies.
    This function can be used for basic testing without requiring all project components.
    
    最小限の依存関係でLangChain Question Agentの簡単なデモを実行します。
    """
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 请先设置OPENAI_API_KEY环境变量")
        return
    
    from langchain_core.language_models import BaseChatModel
    
    # 创建简单的模拟LLM，避免实际API调用
    class MockChatModel(BaseChatModel):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return "这是一个模拟的回复"
        
        def _llm_type(self):
            return "mock_chat_model"
    
    # 创建最小化测试所需的模拟对象
    mock_user = MagicMock()
    mock_user.id = 1
    
    mock_db = AsyncMock()
    mock_db.execute.return_value = AsyncMock()
    
    mock_memory_service = MagicMock()
    mock_memory_service.get_user_memories_list = AsyncMock(return_value=[
        {"content": "用户喜欢旅行", "category": "preference"}
    ])
    mock_memory_service.get_user_memory_categories_with_number = AsyncMock(
        return_value={"preference": 1}
    )
    
    mock_mistake_service = MagicMock()
    mock_mistake_service.get_user_mistakes = AsyncMock(return_value=[])
    
    # 替换服务方法
    original_memory_service = MemoryService
    original_mistake_service = MistakeService
    
    # 使用自定义服务替换原始服务
    MemoryService = lambda _: mock_memory_service
    MistakeService = lambda _: mock_mistake_service
    
    try:
        # 创建模拟的UnitOfWork
        mock_uow = MagicMock()
        mock_uow.db = mock_db
        mock_uow.current_user = mock_user
        
        print("🚀 开始LangChain问题生成Agent演示")
        print("这是一个简化版演示，仅用于测试基本功能")
        
        # 创建Agent实例
        agent = LangChainQuestionAgent(mock_uow)
        agent.debug = True
        
        # 使用简单示例运行
        result = await agent.run("我想学习关于旅行的日语")
        
        print("\n✅ 生成的问题结构:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    finally:
        # 恢复原始服务类
        MemoryService = original_memory_service
        MistakeService = original_mistake_service


# 为单元测试准备的演示函数
async def run_test_example(uow: UnitOfWork, user_input: str) -> Dict[str, Any]:
    """
    Run a test example using the provided UnitOfWork.
    This function is designed for unit testing.
    
    提供されたUnitOfWorkを使用してテスト例を実行します。
    この関数は単体テスト用に設計されています。
    """
    agent = LangChainQuestionAgent(uow)
    return await agent.run(user_input)


# 当直接运行此文件时执行简单演示
if __name__ == "__main__":
    asyncio.run(run_simple_demo())