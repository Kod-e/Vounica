from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.vocab import Vocab as ORM_Vocab

class Vocab(BaseModel):
    """
    The Vocab schema by Pydantic.
    """
    
    id: int = Field(default=None, description="The ID of the vocab.")
    name: str = Field(..., description="The name of the vocab.")
    usage: str = Field(..., description="The usage of the vocab.")
    status: float = Field(..., description="The status of the vocab.")
    language: str = Field(..., description="The language of the vocab.")
    created_at: datetime = Field(..., description="The created time of the vocab.")
    updated_at: datetime = Field(..., description="The updated time of the vocab.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Vocab":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from ..context import uow_ctx
        uow = uow_ctx.get()
        vocab = await uow.db.get(ORM_Vocab, self.id)
        user = uow.current_user
        if user is None or user.id != vocab.user_id or vocab is None:
            raise NotFoundException(message="Vocab not found")
        return vocab