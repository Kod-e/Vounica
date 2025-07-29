"""
简单测试模块，测试基本的fixture加载和初始化。
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.question.types.choice import ChoiceQuestion
from app.services.question.common.types import QuestionType

@pytest.mark.asyncio
async def test_question_initialization(test_uow):
    """测试ChoiceQuestion可以正确初始化"""
    test_uow.target_language = "en"
    test_uow.accept_language = "ja"
    question = ChoiceQuestion(uow=test_uow, stem="What is the capital of France?", options=["Paris", "London", "Berlin", "Madrid"], correct_answer="Paris")
    assert question is not None
    assert question.stem == "What is the capital of France?"
    assert question.options == ["Paris", "London", "Berlin", "Madrid"]
    assert question.correct_answer == "Paris"
    assert question.question_type == QuestionType.CHOICE
    question.answer = "London"
    result = question.judge(question.answer)
    assert result.correct == False
    mistake = question.to_mistake(result)
    assert mistake.question == question.stem
    assert mistake.question_type == question.question_type
    assert mistake.language_type == question.uow.target_language
    assert mistake.answer == question.answer
    assert mistake.correct_answer == question.correct_answer
    assert mistake.error_reason == result.error_reason
    