from functools import partial
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.infra.context import uow_ctx
from app.services.question.common.spec import QuestionSpec

class QuestionStack():
    
    def __init__(self):
        self.uow = uow_ctx.get()
        self.questions : List[QuestionSpec] = []
        
        
    def get_tools(self) -> List[StructuredTool]:
        from app.services.tools.langchain.question import gather_tools
        return gather_tools(self)