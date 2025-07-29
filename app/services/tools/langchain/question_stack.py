from functools import partial
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.infra.uow import UnitOfWork
from app.services.question.common.spec import QuestionSpec

class QuestionStack():
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.questions : List[QuestionSpec] = []
        
    