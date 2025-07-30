from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict, TypeAdapter
from datetime import datetime
from app.core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.vocab import Vocab as ORM_Vocab

# 创建用 schema
class VocabCreateSchema(BaseModel):
    """
    The Vocab create schema by Pydantic.
    """
    name: str = Field(..., description="The name of the vocab.")
    usage: str = Field(..., description="The usage of the vocab.")
    status: float = Field(..., description="The status of the vocab.")
    language: str = Field(..., description="The language of the vocab.")

# 对外 schema
class VocabSchema(VocabCreateSchema):
    """
    The Vocab schema by Pydantic.
    """
    
    id: int | None = Field(default=None, description="The ID of the vocab.")
    created_at: datetime = Field(..., description="The created time of the vocab.")
    updated_at: datetime = Field(..., description="The updated time of the vocab.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Vocab":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from app.infra.context import uow_ctx
        uow = uow_ctx.get()
        if self.id is None:
            raise NotFoundException(message="Vocab not found")

        vocab = await uow.db.get(ORM_Vocab, self.id)
        if vocab is None:
            raise NotFoundException(message="Vocab not found")

        user = uow.current_user
        if user is None or vocab.user_id != user.id:
            raise NotFoundException(message="Vocab not found")
        return vocab

# ListAdapter
VocabSchemaListAdapter = TypeAdapter(list[VocabSchema])