from app.services.question.types import ChoiceQuestion
from typing import List
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
from app.infra.context import uow_ctx
from app.services.question.common.spec import QuestionSpec

# 搜索参数
class QuestionArgs(BaseModel):
    stem: str = Field(..., description="Question stem")
    options: List[str] = Field(..., description="Options list")
    correct_answer: str = Field(..., description="Correct answer")
# 创建题
def add_choice_question(
    stack: List[QuestionSpec],
    stem: str, 
    options: List[str], 
    correct_answer: str
) -> str:
    uow = uow_ctx.get()
    question = ChoiceQuestion(uow=uow, stem=stem, options=options, correct_answer=correct_answer)
    stack.append(question)
    message = f"ChoiceQuestion added, size={len(stack)}"
    return message
# 制作函数, 注入应该注入的内容
def build_add_choice_tool(stack: List[QuestionSpec]) -> StructuredTool:
    return StructuredTool.from_function(
        name="add_choice_question",
        coroutine=partial(add_choice_question, stack=stack),
        description=(
            """
创建一个选择题
stem: 题干
options: 选项列表(4个)
correct_answer: 正确答案
            """
        ),
        args_schema=QuestionArgs,
    )