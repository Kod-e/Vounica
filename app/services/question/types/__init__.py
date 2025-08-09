from app.services.question.types.choice import ChoiceQuestion
from app.services.question.types.match import MatchQuestion
from app.services.question.types.assembly import AssemblyQuestion
from typing import Union,Annotated
from pydantic import TypeAdapter, Field


QuestionUnion = Annotated[Union[ChoiceQuestion, MatchQuestion, AssemblyQuestion], Field(discriminator="question_type")]
QuestionAdapter = TypeAdapter(QuestionUnion)
__all__ = ["ChoiceQuestion", "MatchQuestion", "QuestionUnion", "AssemblyQuestion"]
