from app.services.question.types import MatchQuestion
from typing import List, Tuple
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
from app.services.question.common.spec import QuestionSpec

# 搜索参数
class QuestionArgs(BaseModel):
    stem: str = Field(..., description="Question stem")
    left_options: List[str] = Field(..., description="Left options list")
    right_options: List[str] = Field(..., description="Right options list")
    correct_answer: List[Tuple[str, str]] = Field(..., description="Correct answer")
# 创建题
def add_match_question(
    stack: List[QuestionSpec],
    stem: str, 
    options: List[str], 
    correct_answer: str
) -> str:
    question = MatchQuestion(stem=stem, options=options, correct_answer=correct_answer)
    stack.append(question)
    message = f"MatchQuestion added, size={len(stack)}"
    return message
# 制作函数, 注入应该注入的内容
def build_add_match_tool(stack: List[QuestionSpec]) -> StructuredTool:
    return StructuredTool.from_function(
        name="add_match_question",
        coroutine=partial(add_match_question, stack=stack),
        description=(
            """
Add a match question to the stack.
stem: Question stem
left_options: Left options list
right_options: Right options list
correct_answer: Correct answer
            """
        ),
        args_schema=QuestionArgs,
    )