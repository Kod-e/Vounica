"""
Choice question implementation based on QuestionSpec.

選択(せんたく)問題(もんだい)クラス。
选择题实现。
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

@register_question_type(QuestionType.CHOICE)
class ChoiceQuestion(QuestionSpec):
    """Multiple-choice question (single correct answer)."""
    
    # 题干及答案相关字段 (Pydantic 模型字段)
    stem: str
    options: List[str]
    correct_answer: str
    # 用户答案
    answer: Optional[str] = None
    question_type: Literal[QuestionType.CHOICE] = Field(
        default=QuestionType.CHOICE, description="discriminator"
    )
    # 描述题目
    def prompt(self) -> str:
        """Return the question stem as prompt."""
        question_prompt = f"""
Choice Question:
{self.stem}
Options:
{self.options}
Correct Answer:
{self.correct_answer}
        """
        return question_prompt

    # 判断答案
    async def judge(self) -> JudgeResult:
        """Judge user answer against the correct answer.
        判断答案时，仅在错误情况下调用 LLM 生成 error_reason。
        """
        is_correct = self.answer.strip() == self.correct_answer.strip()

        error_reason: str | None = None
        if not is_correct:
            error_reason = await self.generate_error_reason(self.answer)

        return JudgeResult(
            correct=is_correct,
            question=f"{self.stem} Select -> {self.options}",
            answer=self.answer,
            correct_answer=self.correct_answer,
            error_reason=error_reason,
        )
    # 生成错误原因
    async def generate_error_reason(self, answer: str) -> str:
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
