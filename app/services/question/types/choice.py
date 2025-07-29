"""
Choice question implementation based on QuestionSpec.

選択(せんたく)問題(もんだい)クラス。
选择题实现。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from app.services.question.common.spec import JudgeResult, QuestionSpec
from app.services.question.common.registry import register_question_type
from app.services.question.common.types import QuestionType
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import LanguageModelInput
from app.llm.client import chat_completion
from app.llm.models import LLMModel
from app.infra.uow import UnitOfWork

@register_question_type(QuestionType.CHOICE)
class ChoiceQuestion(QuestionSpec):
    """Multiple-choice question (single correct answer)."""
    
    # 题干及答案相关字段 (Pydantic 模型字段)
    stem: str = Field(...)
    options: List[str] = Field(...)
    correct_answer: str = Field(...)
    # 用户答案
    answer: Optional[str] = None
    # init方法
    def __init__(self, uow: UnitOfWork, stem: str, options: List[str], correct_answer: str):
        # 调用 Pydantic BaseModel 初始化, 一次性传入所有必填字段
        super().__init__(
            question_type=QuestionType.CHOICE,
            uow=uow,
            stem=stem,
            options=options,
            correct_answer=correct_answer,
        )
    # ------------------------------------------------------------------
    # Mandatory overrides
    # ------------------------------------------------------------------
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
    def judge(self, answer: str) -> JudgeResult:
        """Judge user answer against the correct answer.
        判断答案时，仅在错误情况下调用 LLM 生成 error_reason。
        """
        is_correct = answer.strip() == self.correct_answer.strip()

        error_reason: str | None = None
        if not is_correct:
            error_reason = self.generate_error_reason(answer)

        return JudgeResult(
            correct=is_correct,
            question=self.stem,
            answer=answer,
            correct_answer=self.correct_answer,
            error_reason=error_reason,
        )
    # 生成错误原因
    def generate_error_reason(self, answer: str) -> str:
        """调用 LLM 生成错误原因。"""
        response = chat_completion(
            input=[
                    SystemMessage(content=f"""
You are the best language learning platform's intelligent judge AI,
you need to generate the user's error reason in a very short way,
use the question's language({self.uow.target_language}) to generate the error reason.
"""),
                    HumanMessage(content=self.prompt() + f"""
                    The user's answer is: {answer}
                    """)
                ],
            uow=self.uow,
            model_type=LLMModel.STANDARD,
        )
        return response.content
    
    # 工厂方法
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ChoiceQuestion":
        """Create ChoiceQuestion from JSON-like dict."""
        return cls(
            question_type=QuestionType.CHOICE,
            stem=data["stem"],
            options=data["options"],
            correct_answer=data["correct_answer"],
        ) 