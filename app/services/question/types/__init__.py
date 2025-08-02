from app.services.question.types.choice import ChoiceQuestion
from app.services.question.types.match import MatchQuestion
from app.services.question.types.assembly import AssemblyQuestion
from typing import Union
from pydantic import TypeAdapter


QuestionUnion = Union[ChoiceQuestion, MatchQuestion]
QuestionAdapter = TypeAdapter(QuestionUnion)
__all__ = ["ChoiceQuestion", "MatchQuestion", "QuestionUnion", "AssemblyQuestion"]
