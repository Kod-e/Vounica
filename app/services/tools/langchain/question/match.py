from app.services.question.types import MatchQuestion
import random
from typing import List, Tuple
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
from app.services.question.base.spec import QuestionSpec
from app.services.question.types import QuestionUnion
# 搜索参数
class AnswerPair(BaseModel):
    left: str = Field(..., description="Left option")
    right: str = Field(..., description="Right option")
class QuestionArgs(BaseModel):
    stem: str = Field(..., description="Question stem")
    left_options: List[str] = Field(..., description="Left options list")
    right_options: List[str] = Field(..., description="Right options list")
    correct_answer: List[AnswerPair] = Field(..., description="Correct answer pairs")
# 创建题
async def add_match_question(
    stack: List[QuestionUnion],
    stem: str,
    left_options: List[str],
    right_options: List[str],
    correct_answer: List[AnswerPair]
) -> str:
    correct_pairs: List[Tuple[str, str]] = [(pair.left, pair.right) for pair in correct_answer]
    #打乱right_options
    random.shuffle(right_options)
    question = MatchQuestion(
        stem=stem,
        left_options=left_options,
        right_options=right_options,
        correct_answer=correct_pairs,
    )
    stack.append(question)
    message = f"MatchQuestion added, size={len(stack)}"
    return message
# 制作函数, 注入应该注入的内容
def build_tools(stack: List[QuestionUnion]) -> StructuredTool:
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