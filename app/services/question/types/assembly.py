"""
Assembly question implementation based on QuestionSpec.

选词填空 / 词块拼接实现。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import Field

from app.services.question.base.spec import JudgeResult, QuestionSpec
from app.services.question.base.registry import register_question_type
from app.services.question.base.types import QuestionType
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import LanguageModelInput
from app.llm.client import chat_completion
from app.llm.models import LLMModel
from app.infra.context import uow_ctx

@register_question_type(QuestionType.ASSEMBLY)
class AssemblyQuestion(QuestionSpec):
    """Assembly question (fill in the blanks)."""
    
    # 题干及答案相关字段 (Pydantic 模型字段)
    stem: str
    options: List[str]
    correct_answer: List[str]
    # 用户答案
    answer: Optional[List[str]] = None
    question_type: Literal[QuestionType.ASSEMBLY] = Field(
        default=QuestionType.ASSEMBLY, description="discriminator"
    )
    
    # 描述题目
    def prompt(self) -> str:
        """Return the question stem as prompt."""
        question_prompt = f"""
Assembly Question:
{self.stem}
Options:
{self.options}
Correct Answer:
{self.correct_answer}
        """
        return question_prompt
    
    # 判断答案
    async def judge(self, answer: List[str]) -> JudgeResult:
        """Judge user answer against the correct answer.
        判断答案时，仅在错误情况下调用 LLM 生成 error_reason。
        """
        # 如果答案为空，则认为答案错误
        if not answer:
            return JudgeResult(
                correct=False,
                error_reason=await self.generate_error_reason(answer)
            )
        # 如果不一致，则认为答案错误
        elif answer != self.correct_answer:
            return JudgeResult(
                correct=False,
                error_reason=await self.generate_error_reason(answer)
            )
        # 如果一致，则认为答案正确
        else:
            return JudgeResult(
                correct=True,
                error_reason=None
            )
    
    # 生成错误原因
    async def generate_error_reason(self, answer: List[str]) -> str:
        """调用 LLM 生成错误原因。"""
        uow = uow_ctx.get()
        response = await chat_completion(
            input=[
                    SystemMessage(content=f"""
You are the best language learning platform's intelligent judge AI,
you need to generate the user's error reason in a very short way,
use the question's language({uow.target_language}) to generate the error reason.
"""),
                    HumanMessage(content=self.prompt() + f"""
The user's answer is: {answer}
                    """)
                ],
            model_type=LLMModel.STANDARD.value["name"]
        )
        return response.content
    
    