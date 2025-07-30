from app.services.question.types import ChoiceQuestion
from typing import List
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
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
    question = ChoiceQuestion(stem=stem, options=options, correct_answer=correct_answer)
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
Add a choice question to the stack.
stem: Question stem
options: Options list(4)
correct_answer: Correct answer
            """
        ),
        args_schema=QuestionArgs,
    )