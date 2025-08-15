from functools import partial
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.infra.context import uow_ctx
from app.services.question.types import QuestionUnion

class EmptyArgs(BaseModel):
    pass

class DeleteQuestionArgs(BaseModel):
    index: int = Field(..., description="delete question index")


class QuestionStack():
    
    def __init__(self):
        self.uow = uow_ctx.get()
        self.questions : List[QuestionUnion] = []
        
        
    def get_tools(self) -> List[StructuredTool]:
        from app.services.tools.langchain.question import gather_tools
        return gather_tools(self)
    
    def build_delete_question_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            name="delete_question",
            description="Delete a question from the stack. Deleting a question shifts subsequent indices",
            func=self.delete_question,
            args_schema=DeleteQuestionArgs,
        )
    def build_get_questions_prompt_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            name="get_questions",
            description="Return all questions in the stack as a single multi-line prompt.",
            func=self.get_questions_prompt,  # 或者 func=self.get_questions_prompt（同步）
            args_schema=EmptyArgs,  # 无参数时传空schema，调用时传 {}
        )
    def delete_question(self, index: int) -> str:
        if index < 0 or index >= len(self.questions):
            return f"Index out of range, index: {index}, length: {len(self.questions)}"
        self.questions.pop(index)
        return f"Question deleted, index: {index}, length: {len(self.questions)}"
    
    # 获取目前所有的问题的prompt
    def get_questions_prompt(self) -> str:
        return "\n".join([f"Question {index}: {question.prompt()}" for index, question in enumerate(self.questions)])