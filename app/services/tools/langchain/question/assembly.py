from app.services.question.types import AssemblyQuestion
from typing import List, Union
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field
from app.services.question.base.spec import QuestionSpec
from app.services.question.types import QuestionUnion
import random
# 搜索参数
class QuestionArgs(BaseModel):
    stem: str = Field(..., description="Question stem")
    options: List[str] = Field(..., description="Options list")
    correct_answer: Union[str, List[str]] = Field(..., description="Correct answer (single string or list)")
# 创建题
async def add_assembly_question(
    stack: List[QuestionUnion],
    stem: str,
    options: List[str],
    correct_answer: Union[str, List[str]]
) -> str:
    # 如果传入的是 str，则转为单元素 list
    answer_list: List[str]
    if isinstance(correct_answer, str):
        answer_list = [correct_answer]
    else:
        answer_list = correct_answer
    #打乱options
    random.shuffle(options)
    question = AssemblyQuestion(stem=stem, options=options, correct_answer=answer_list)
    stack.append(question)
    message = f"AssemblyQuestion added, size={len(stack)}"
    return message
# 制作函数, 注入应该注入的内容
def build_tools(stack: List[QuestionUnion]) -> StructuredTool:
    return StructuredTool.from_function(
        name="add_assembly_question",
        coroutine=partial(add_assembly_question, stack=stack),
        description=(
            """
Add a assembly question to the stack.
stem: Question stem
options: Options list
correct_answer: Correct answer
            """
        ),
        args_schema=QuestionArgs,
    )