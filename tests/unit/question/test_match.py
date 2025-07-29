"""
简单测试模块，测试基本的fixture加载和初始化。
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.question.types.match import MatchQuestion
from app.services.question.common.types import QuestionType
from app.services.question.common.spec import QuestionSpec

@pytest.mark.asyncio
async def test_question_model(test_uow):
    """测试ChoiceQuestion可以正确初始化"""
    test_uow.target_language = "fr"
    test_uow.accept_language = "en"
    question = MatchQuestion(uow=test_uow, left_options=["route", "carte", "livre", "stylo"], right_options=["road", "map", "book", "pen"], correct_answer=[("route", "road"), ("carte", "map"), ("livre", "book"), ("stylo", "pen")])
    assert question is not None
    assert question.left_options == ["route", "carte", "livre", "stylo"]
    assert question.right_options == ["road", "map", "book", "pen"]
    assert question.correct_answer == [("route", "road"), ("carte", "map"), ("livre", "book"), ("stylo", "pen")]
    assert question.question_type == QuestionType.MATCH
    question.answer = [("route", "road"), ("livre", "map"), ("carte", "book"), ("stylo", "pen")]
    result = await question.judge(question.answer)
    assert result.correct == False
    mistake = question.to_mistake(result)
    assert mistake.question == f"{question.left_options} Match -> {question.right_options}"
    assert mistake.question_type == question.question_type
    assert mistake.language_type == question.uow.target_language
    assert mistake.error_reason == result.error_reason
    
    # 测试从mistake中还原题目
    question_from_mistake = QuestionSpec.from_mistake(test_uow, mistake)
    assert question_from_mistake.question_type == question.question_type
    assert question_from_mistake.uow.target_language == question.uow.target_language
    assert question_from_mistake.answer == question.answer
    assert question_from_mistake.left_options == question.left_options
    assert question_from_mistake.right_options == question.right_options
    assert question_from_mistake.correct_answer == question.correct_answer
    