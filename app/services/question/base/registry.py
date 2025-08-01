"""Question type registry & factory.

题型注册与工厂方法。
"""

from __future__ import annotations

from typing import Dict, Type

from app.services.question.base.types import QuestionType

from typing import TYPE_CHECKING
from app.services.question.base.spec import QuestionSpec


_QUESTION_REGISTRY: Dict[QuestionType, Type[QuestionSpec]] = {}


def register_question_type(q_type: QuestionType):
    """Decorator to register a QuestionSpec subclass.
    用于将题型类绑定到枚举值, 便于工厂函数动态创建。
    """

    def decorator(cls):

        if not issubclass(cls, QuestionSpec):
            raise TypeError("Class must inherit from QuestionSpec")
        _QUESTION_REGISTRY[q_type] = cls
        return cls

    return decorator


def create_question(data: dict):
    """Factory: build QuestionSpec instance from plain dict.
    工厂方法, 从普通字典构建 QuestionSpec 实例。
    """

    value = data.get("question_type")
    if value is None:
        raise ValueError("'question_type' is required in data")

    try:
        q_type = QuestionType(value)
    except ValueError as exc:
        raise ValueError(f"Unknown question_type: {value}") from exc

    cls = _QUESTION_REGISTRY.get(q_type)
    if cls is None:
        raise ValueError(f"Question type {q_type.value} not registered")

    return cls.from_json(data) 