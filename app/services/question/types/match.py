"""
Match question implementation based on QuestionSpec.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field

from app.services.question.common.spec import JudgeResult, QuestionSpec
from app.services.question.common.registry import register_question_type
from app.services.question.common.types import QuestionType
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import LanguageModelInput
from app.llm.client import chat_completion
from app.llm.models import LLMModel
from app.infra.context import uow_ctx
import json

@register_question_type(QuestionType.MATCH)
class MatchQuestion(QuestionSpec):
    """Match question (match language to language, and match the correct answer)."""
    
    # 题干及答案相关字段 (Pydantic 模型字段)
    left_options: List[str] = Field(...)
    right_options: List[str] = Field(...)
    # 正确答案
    correct_answer: List[Tuple[str, str]] = Field(...)
    # 用户答案
    answer: Optional[List[Tuple[str, str]]] = None
    # 题目类型
    question_type: QuestionType = Field(
       default=QuestionType.MATCH
    )
    
    # 描述题目
    def prompt(self) -> str:
        """Return the question stem as prompt."""
        question_prompt = f"""
Match Question:
Left Options:
{self.left_options}
Right Options:
{self.right_options}
Correct Answer:
{self.correct_answer}

        """
        return question_prompt

    # 判断答案
    async def judge(self, answer: List[Tuple[str, str]]) -> JudgeResult:
        """Judge user answer against the correct answer.
        判断答案时，仅在错误情况下调用 LLM 生成 error_reason。
        """
        is_correct = answer == self.correct_answer

        error_reason: str | None = None
        if not is_correct:
            error_reason = await self.generate_error_reason(answer)

        return JudgeResult(
            correct=is_correct,
            question=f"{self.left_options} Match -> {self.right_options}",
            answer=f"{answer}",
            correct_answer=f"{self.correct_answer}",
            error_reason=error_reason,
        )
    # 生成错误原因
    async def generate_error_reason(self, answer: List[Tuple[str, str]]) -> str:
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
            model_type=LLMModel.STANDARD,
        )
        return response.content