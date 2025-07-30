# 错题集记录时, 记录整个题目的string内容, 并且让GPT生成错在哪里的评价
from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict, TypeAdapter
from datetime import datetime
from app.core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.mistake import Mistake as ORM_Mistake

# 创建用 schema
class MistakeCreateSchema(BaseModel):
    """
    The Mistake create schema by Pydantic.
    """
    question: str = Field(..., description="The question of the mistake.")
    question_type: str = Field(..., description="The type of the question.")
    language: str = Field(..., description="The language type of the question.")
    answer: str = Field(..., description="The answer of the mistake.")
    correct_answer: str = Field(..., description="The correct answer of the mistake.")
    error_reason: str = Field(..., description="The reason of the mistake.")

# 对外 schema
class MistakeSchema(MistakeCreateSchema):
    """
    The Mistake schema by Pydantic.
    """ 
    
    id: int | None = Field(default=None, description="The ID of the mistake.")
    created_at: datetime = Field(..., description="The created time of the mistake.")
    updated_at: datetime = Field(..., description="The updated time of the mistake.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Mistake":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from app.infra.context import uow_ctx
        uow = uow_ctx.get()
        if self.id is None:
            raise NotFoundException(message="Mistake not found")

        mistake = await uow.db.get(ORM_Mistake, self.id)
        if mistake is None:
            raise NotFoundException(message="Mistake not found")

        user = uow.current_user
        if user is None or mistake.user_id != user.id:
            raise NotFoundException(message="Mistake not found")
        return mistake

# ListAdapter
MistakeSchemaListAdapter = TypeAdapter(list[MistakeSchema])