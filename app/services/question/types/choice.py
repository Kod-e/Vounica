"""
Choice question implementation based on QuestionSpec.

選択(せんたく)問題(もんだい)クラス。
选择题实现。
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import Field

from app.services.question.common.spec import JudgeResult, QuestionSpec
from app.services.question.common.registry import register_question_type
from app.services.question.common.types import QuestionType
from app.llm.client import chat_completion
from app.infra.uow import UnitOfWork

@register_question_type(QuestionType.CHOICE)
class ChoiceQuestion(QuestionSpec):
    """Multiple-choice question (single correct answer)."""
    
    # 题目
    stem: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of selectable answers")
    correct_answer: str = Field(..., description="The correct option in plain text")

    # ------------------------------------------------------------------
    # Mandatory overrides
    # ------------------------------------------------------------------

    def prompt(self) -> str:
        """Return the question stem as prompt."""

        return self.stem

    def judge(self, answer: str) -> JudgeResult:
        """Judge user answer against the correct answer."""

        is_correct = answer.strip() == self.correct_answer.strip()
        return JudgeResult(
            correct=is_correct,
            question=self.stem,
            answer=answer,
            correct_answer=self.correct_answer,
            error_reason=self.generate_error_reason(answer),
        )

    # 生成错误原因
    def generate_error_reason(self, answer: str, uow: UnitOfWork) -> str:
        """Generate error reason for the given answer."""
        return "incorrect choice"
    
    # 工厂方法
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ChoiceQuestion":
        """Create ChoiceQuestion from JSON-like dict."""
        return cls(
            question_type=QuestionType.CHOICE,
            language_type=data["language_type"],
            stem=data["stem"],
            options=data["options"],
            correct_answer=data["correct_answer"],
        ) 