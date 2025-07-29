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
from app.services.tools import handle_tool_calls, SEARCH_SCHEMA, SEND_CONSOLE_SCHEMA
from app.services.common.memory import MemoryService
from app.services.common.mistake import MistakeService
from app.services.common.story import StoryService
from app.services.common.vocab import VocabService


class QuestionAgent:
    """
    使用 OPAR (观察、计划、行动、反思) 循环的问题生成代理。
    
    该类用于根据用户状态和输入生成个性化的语言学习题目。
    """
    
    def __init__(self, uow: UnitOfWork, model_type: LLMModel = LLMModel.STANDARD):
        self.uow = uow
        self.model_type = model_type
        
        # 存储OPAR循环的状态和结果
        self.observation_results = []
        self.plan_results = {}
        self.action_results = []
        self.reflection_result = None
        
        # 存储用于给ai看的logs, 用于让Agent知道之前发生了什么
        self.logs = []
        
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        运行完整的 OPAR 循环并根据用户输入生成问题。
        
        该方法协调整个问题生成过程，包括观察、计划、行动和反思阶段。
        """
        
        # 执行OPAR循环
        await self._observe(user_input)
        await self._plan()
        await self._act()
        is_valid = await self._reflect()
        
        # 如果反思阶段认为结果不合理，可以重新执行某个阶段
        retries = 0
        max_retries = 2
        
        while not is_valid and retries < max_retries:
            
            # 根据反思结果决定从哪个阶段重新开始
            if self.reflection_result.get("stage_to_retry") == "observe":
                await self._observe(user_input)
                await self._plan()
                await self._act()
            elif self.reflection_result.get("stage_to_retry") == "plan":
                await self._plan()
                await self._act()
            elif self.reflection_result.get("stage_to_retry") == "act":
                await self._act()
            
            is_valid = await self._reflect()
            retries += 1
        
        # 返回最终生成的题目
        return {
            "questions": self.action_results,
            "is_valid": is_valid,
            "context": {
                "user_is_new": await self._is_new_user(),
                "observations": self.observation_results,
                "plan": self.plan_results
            }
        }
    
    async def _observe(self, user_input: str) -> None:
        """
        观察阶段：观察用户上下文并搜索相关信息。
        
        分析用户输入，识别用户可能的需求，并在数据库中搜索相关资源。
        """
        # 重置观察结果
        self.observation_results = []
        # 应该在构造之前, 获取用户的记忆, LLM的泛化能力可以很容易的确认用户是否是新用户
        # 获取用户的记忆, 20条最重要的, 用于让LLM知道用户之前发生了什么
        memories = await MemoryService(self.uow).get_user_memories_list(limit=20)
        # 获取用户的记忆的category, 用于让LLM知道用户留下了什么样的记忆
        memory_categories = await MemoryService(self.uow).get_user_memory_categories_with_number()
        # 获取用户的最近的5道错题, 用于让LLM知道用户之前犯了什么错
        mistakes = await MistakeService(self.uow).get_user_mistakes(limit=5)
        
        # 构建提示词
        observe_prompt = [
            {"role": "system", "content": f"""
你是一个语言学习平台的智能观察代理。, 用户正在学习{self.uow.target_language}语言(ISO 639-1 标准)
你的任务是分析当前请求下, 你需要搜索哪些信息才能完成在这个问题下用户的画像, 并且返回需要在数据库检索什么, 实际的检索会交给下一个AI完成

需要考虑以下几点：
1. 用户当前的水平和学习目标是什么
2. 你应该知道用户喜欢哪些东西, 想要学会语言最重要的是和生活与爱好相关的契机
3. 你应该知道用户可能会在什么地方发生错误, 应该怎么去检索这些错误记录, 应该检索哪些错误相关的内容

根据用户的请求，使用search_resource函数主动搜索相关的学习资源
你可以搜索：词汇（vocab）、语法（grammar）、错题（mistakes）、故事（stories）和记忆（memories）。
请在回复前尝试搜索相关资源，以获取更准确的上下文信息。

                            """},
            {"role": "user", "content": f"""
下面附带了一些AI对用户的画像, 全部都是由AI主动记录的
关于这个用户当前语言的最重要的最近的20条记忆, 如果不足20条会使用其他语言补齐：{memories}
用户记忆的category和数量：{memory_categories}
关于这个用户当前语言的最近的5道错题：{mistakes}
            """},
            {"role": "user", "content": f"""
用户请求：{user_input}
分析这个请求并主动搜索相关学习资源。可使用search_resource函数来查找与用户需求相关的资源。
            """}
        ]
        # 调用LLM进行观察分析
        response = await chat_completion(
            messages=observe_prompt, 
            uow=self.uow, 
            model_type=self.model_type,
            tools=[SEARCH_SCHEMA],
            tool_choice="auto"
        )
        
        # 处理函数调用
        tool_calls = await handle_tool_calls(
            response_message=response.choices[0].message,
            uow=self.uow
        )
        
        # 如果有函数调用结果，则添加到观察结果中
        for call in tool_calls:
            if 'results' in call and call['results']:
                self.observation_results.append({
                    "resource_type": call['args'].get('resource'),
                    "query": call['args'].get('query'),
                    "results": call['results']
                })
        #
    async def _plan(self) -> None:
        """ 
        计划阶段：基于观察结果规划问题生成。
        
        根据观察阶段收集的信息，规划需要生成的问题类型、数量和难度。
        """
        # 重置计划结果
        self.plan_results = {}
        
        if not self.observation_results:
            # 如果没有观察结果，则制定一个基础计划
            self.plan_results = {
                "question_count": 5,
                "question_types": ["choice", "cloze", "free"],
                "difficulty": "beginner",
                "focus": "general_assessment"
            }
            return
        
        # 构建提示词，包含观察结果
        plan_prompt = [
            {"role": "system", "content": """
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
            """},
            {"role": "user", "content": f"""
观察结果：
{self.observation_results}

请创建问题生成计划。
            """}
        ]
        #应该在这里插入所有题目的描述
        
        # 调用LLM制定计划
        response = await chat_completion(messages=plan_prompt, uow=self.uow, model_type=self.model_type)
        plan_text = response.choices[0].message.content
        
        # 解析LLM的计划
        # 实际实现可能需要更复杂的解析逻辑
        self.plan_results = self._parse_plan(plan_text)
    
    async def _act(self) -> None:
        """
        行动阶段：根据计划生成问题。
        
        按照计划阶段制定的规划，生成具体的问题内容。
        """
        # 重置行动结果
        self.action_results = []
        
        if not self.plan_results:
            return
        
        question_count = self.plan_results.get("question_count", 5)
        question_types = self.plan_results.get("question_types", ["choice"])
        difficulty = self.plan_results.get("difficulty", "beginner")
        focus = self.plan_results.get("focus", "general")
        
        # 对于每个计划的问题，调用LLM生成具体题目
        for i in range(question_count):
            # 为了多样性，循环使用不同题型
            q_type = question_types[i % len(question_types)]
            
            # 构建提示词
            act_prompt = [
                {"role": "system", "content": f"""
你是一个语言学习平台的问题生成代理。
生成一个具有以下参数的{q_type}类型问题：
- 难度：{difficulty}
- 重点领域：{focus}
- 问题类型：{q_type}

包括问题所需的所有必要信息，例如：
- 问题文本
- 答案选项（对于选择题）
- 正确答案
- 为什么答案是正确的解释

请以JSON对象的适当字段格式化你的回复。
                """},
                {"role": "user", "content": f"""
请生成第{i+1}题（共{question_count}题）。
使用以下观察结果作为上下文：
{self.observation_results}
                """}
            ]
            
            # 调用LLM生成题目
            response = await chat_completion(messages=act_prompt, uow=self.uow, model_type=self.model_type)
            question_data = response.choices[0].message.content
            
            # 解析生成的题目数据
            parsed_question = self._parse_question(question_data, q_type)
            if parsed_question:
                self.action_results.append(parsed_question)
    
    async def _reflect(self) -> bool:
        """
        反思阶段：反思生成的问题并确定它们是否合适。
        
        评估生成问题的质量和适合度，决定是否需要修改。
        
        Returns:
            bool: 如果问题有效则返回True，如果需要修改则返回False
        """
        if not self.action_results:
            self.reflection_result = {
                "is_valid": False,
                "reason": "No questions were generated",
                "stage_to_retry": "act"
            }
            return False
        
        # 构建提示词
        reflect_prompt = [
            {"role": "system", "content": """
你是一个语言学习平台的反思代理。
你的任务是评估生成的问题的质量和适合度。

考虑以下几点：
1. 问题是否符合用户的学习需求和水平？
2. 问题是否多样化且有吸引力？
3. 问题是否存在任何问题（歧义、错误等）？
4. 总体而言，这些问题是否适合用户？

提供详细评估，并确定这些问题是否可以呈现给用户。
如果不行，请指明应该重试OPAR过程的哪个阶段："observe"、"plan"或"act"。
            """},
            {"role": "user", "content": f"""
原始用户请求：[这里应该是用户的原始输入]
生成的问题：
{self.action_results}

请评估这些问题并确定它们是否合适。
            """}
        ]
        
        # 调用LLM进行反思评估
        response = await chat_completion(messages=reflect_prompt, uow=self.uow, model_type=self.model_type)
        reflection = response.choices[0].message.content
        
        # 解析反思结果
        self.reflection_result = self._parse_reflection(reflection)
        
        return self.reflection_result.get("is_valid", False)

    
    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """解析LLM的计划输出。"""
        # 这个函数需要解析LLM输出的计划文本，提取结构化数据
        # 实际实现中可能会使用更复杂的解析逻辑或让LLM直接输出JSON
        
        # 简单示例实现
        plan = {
            "question_count": 5,
            "question_types": ["choice"],
            "difficulty": "beginner",
            "focus": "general"
        }
        
        # 解析问题数量
        if "questions:" in plan_text.lower():
            for line in plan_text.split("\n"):
                if "questions:" in line.lower():
                    try:
                        count = int(line.split(":")[1].strip().split(" ")[0])
                        plan["question_count"] = count
                    except (ValueError, IndexError):
                        pass
        
        # 解析问题类型
        question_types = []
        for q_type in ["choice", "cloze", "free", "match_audio", "match_native", "order", "free_limit", "roleplay"]:
            if q_type in plan_text.lower():
                question_types.append(q_type)
        
        if question_types:
            plan["question_types"] = question_types
        
        # 解析难度
        for difficulty in ["beginner", "intermediate", "advanced"]:
            if difficulty in plan_text.lower():
                plan["difficulty"] = difficulty
                break
        
        return plan
    
    def _parse_question(self, question_data: str, q_type: str) -> Optional[Dict[str, Any]]:
        """解析LLM输出的问题数据。"""
        # 这个函数需要解析LLM生成的问题数据
        # 实际实现中可能需要更复杂的JSON解析
        
        # 简单示例实现，假设LLM输出的是易于解析的格式
        try:
            # 解析LLM输出，提取问题数据
            # 实际实现应该使用JSON解析或更结构化的方法
            
            # 返回通用结构
            return {
                "question_type": q_type,
                "question_text": "示例问题文本",  # 应从question_data中解析
                "options": ["选项A", "选项B", "选项C", "选项D"] if q_type == "choice" else None,
                "correct_answer": "正确答案",  # 应从question_data中解析
                "explanation": "解释",  # 应从question_data中解析
                "raw_data": question_data  # 保存原始数据，便于调试
            }
        except Exception as e:
            return None
    
    def _parse_reflection(self, reflection: str) -> Dict[str, Any]:
        """解析LLM的反思输出。"""
        # 解析反思结果，判断是否需要重新执行某个阶段
        result = {
            "is_valid": False,
            "reason": "",
            "stage_to_retry": None
        }
        
        # 判断LLM是否认为题目是合适的
        if "suitable" in reflection.lower() and "yes" in reflection.lower():
            result["is_valid"] = True
        
        # 如果不合适，确定应该重新执行哪个阶段
        if not result["is_valid"]:
            if "observe" in reflection.lower():
                result["stage_to_retry"] = "observe"
            elif "plan" in reflection.lower():
                result["stage_to_retry"] = "plan"
            else:
                # 默认重新执行行动阶段
                result["stage_to_retry"] = "act"
        
        # 提取原因
        result["reason"] = reflection
        
        return result 