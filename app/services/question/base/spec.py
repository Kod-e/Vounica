from __future__ import annotations

"""
Define abstract Question specification and evaluation result.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel,Field, ConfigDict

from app.services.question.base.types import QuestionType
from app.infra.models import Mistake
from app.infra.context import uow_ctx
# 评判结果
class JudgeResult(BaseModel):
    """
    Standardized evaluation output for a question answer.
    """

    correct: bool
    # 关于题目的基本信息
    question: str
    answer: str
    correct_answer: Optional[str] = None
    error_reason: Optional[str] = None

    
# 题目规范
class QuestionSpec(BaseModel, ABC):
    """Abstract base class that every question type must inherit.
    题目抽象基类
    """

    question_type: QuestionType

    model_config = ConfigDict(
        from_attributes=True,   # 取代 orm_mode
        validate_by_name=True,  # 取代 allow_population_by_field_name
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    # 通过abstractmethod, 强制子类实现
    @abstractmethod
    def prompt(self) -> str:
        """Return ai-readable prompt describing the question.
        返回面向 AI 的题目描述 Prompt。
        """
        
    @abstractmethod
    async def judge(self) -> JudgeResult:
        """Judge the given answer and return a JudgeResult object.
        判断用户答案, 返回评判结果。
        """
    # 生成用户的回答

    # 生成error_reason
    @abstractmethod
    async def generate_error_reason(self) -> str:
        """Generate error reason for the given answer.
        生成错误原因。
        """

    # 生成mistake
    def to_mistake(
        self,
        judge_result: JudgeResult,
    ) -> Mistake:
        """Convert wrong answer information into Mistake table payload."""
        uow = uow_ctx.get()
        return Mistake(
            user_id=uow.current_user_id,
            question=judge_result.question,
            question_type=self.question_type,
            language=uow.target_language,
            answer=judge_result.answer,
            correct_answer=judge_result.correct_answer,
            error_reason=judge_result.error_reason,
            question_json=self.model_dump(),
        )
    # 从mistake中还原题目
    @classmethod
    def from_mistake(cls, mistake: Mistake) -> "QuestionSpec":
        """Create question instance from Mistake table payload."""
        # 确定mistake的类型
        question_type = mistake.question_type
        # 延迟导入以避免循环
        from app.services.question.base.registry import _QUESTION_REGISTRY
        question_cls = _QUESTION_REGISTRY.get(question_type)
        if question_cls is None:
            raise ValueError(f"Question type {question_type} not registered")
        question =  question_cls.model_validate(mistake.question_json)
        return question

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} type={self.question_type}>" 