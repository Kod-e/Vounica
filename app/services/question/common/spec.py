from __future__ import annotations

"""
Define abstract Question specification and evaluation result.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.services.question.common.types import QuestionType


# 评判结果
class JudgeResult(BaseModel):
    """
    Standardized evaluation output for a question answer.
    """

    correct: bool

    # 关于题目的基本信息
    question: str
    answer: str
    correct_answer: str = None
    error_reason: str = None


# 题目规范
class QuestionSpec(BaseModel, ABC):
    """Abstract base class that every question type must inherit.
    题目抽象基类
    """

    question_type: QuestionType
    #ISO 639-1 code, 用于多语区分
    language_type: str

    class Config:
        use_enum_values = True
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    # 通过abstractmethod, 强制子类实现
    @abstractmethod
    def prompt(self) -> str:
        """Return ai-readable prompt describing the question.
        返回面向 AI 的题目描述 Prompt。
        """

    @abstractmethod
    def judge(self, answer: str) -> JudgeResult:
        """Judge the given answer and return a JudgeResult object.
        判断用户答案, 返回评判结果。
        """
    
    # 生成error_reason
    @abstractmethod
    def generate_error_reason(self, answer: str) -> str:
        """Generate error reason for the given answer.
        生成错误原因。
        """

    # 生成mistake_dict
    def to_mistake_dict(
        self,
        *,
        user_id: int,
        judge_result: JudgeResult,
    ) -> Dict[str, Any]:
        """Convert wrong answer information into Mistake table payload.
        """
        return {
            "user_id": user_id,
            "question": judge_result.question,
            "question_type": self.question_type.value,
            "language": self.language_type,
            "answer": judge_result.answer,
            "correct_answer": judge_result.correct_answer,
            "error_reason": judge_result.error_reason,
        }

    @classmethod
    @abstractmethod
    def from_json(cls, data: Dict[str, Any]) -> "QuestionSpec":  # noqa: D401
        """Create question instance from JSON dict.
        工厂方法, 从 JSON 数据生成题目实例。
        """


    def __str__(self) -> str:
        return f"<{self.__class__.__name__} type={self.question_type}>" 