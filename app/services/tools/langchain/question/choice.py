from app.services.question.types import ChoiceQuestion
from typing import List
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
from app.services.question.base.spec import QuestionSpec
from app.services.question.types import QuestionUnion
# 搜索参数
class QuestionArgs(BaseModel):
    stem: str = Field(..., description="Question stem")
    options: List[str] = Field(..., description="Options list")
    correct_answer: str = Field(..., description="Correct answer")
# 创建题
async def add_choice_question(
    stack: List[QuestionUnion],
    stem: str, 
    options: List[str], 
    correct_answer: str
) -> str:
    if len(stack) >= 10:
        return f"You have reached the maximum number of questions (10). Please delete some questions first."
    # 确保correct_answer在options中
    if correct_answer not in options:
        return f"Correct answer {correct_answer} is not in options {options}, you should check your input"
    question = ChoiceQuestion(stem=stem, options=options, correct_answer=correct_answer)
    stack.append(question)
    message = f"{len(stack)}/10(Max) ChoiceQuestion added, stem: {stem} Now We Have {len(stack)} Questions, Max 10 Questions"
    return message
# 制作函数, 注入应该注入的内容
def build_tools(stack: List[QuestionUnion]) -> StructuredTool:
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