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
    if len(stack) >= 8:
        return f"You have reached the maximum number of questions (8). Please delete some questions first."
    correct_pairs: List[Tuple[str, str]] = [(pair.left, pair.right) for pair in correct_answer]
    #打乱right_options
    random.shuffle(right_options)
    # 确保left_options和right_options长度相同, 并且字符串不重复
    if len(left_options) != len(right_options):
        return f"Left options and right options length must be the same, you should check your input"
    if len(left_options) != len(set(left_options)):
        return f"Left options must be unique, you should check your input"
    if len(right_options) != len(set(right_options)):
        return f"Right options must be unique, you should check your input"
    
    # 确保correct_answer在left_options和right_options中
    if not all(item in left_options for item in [left for left, _ in correct_pairs]):
        return f"Correct answer {correct_pairs} is not in left_options {left_options}, you should check your input"
    if not all(item in right_options for item in [right for _, right in correct_pairs]):
        return f"Correct answer {correct_pairs} is not in right_options {right_options}, you should check your input"
    question = MatchQuestion(
        stem=stem,
        left_options=left_options,
        right_options=right_options,
        correct_answer=correct_pairs,
    )
    stack.append(question)
    message = f"{len(stack)}/8(Max) MatchQuestion added, stem: {stem}"
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