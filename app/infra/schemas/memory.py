# Memory Schema
from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.memory import Memory as ORM_Memory

class Memory(BaseModel):
    """
    The Memory schema by Pydantic.
    """
    
    id: int = Field(default=None, description="The ID of the memory.")
    content: str = Field(..., description="The content of the memory.")
    category: str = Field(..., description="The category of the memory.")
    priority: int = Field(..., description="The priority of the memory.")
    language: str = Field(..., description="The language of the memory.")
    created_at: datetime = Field(..., description="The created time of the memory.")
    updated_at: datetime = Field(..., description="The updated time of the memory.")

    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Memory":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from ..context import uow_ctx
        uow = uow_ctx.get()
        memory = await uow.db.get(ORM_Memory, self.id)
        user = uow.current_user
        if user is None or user.id != memory.user_id or memory is None:
            raise NotFoundException(message="Memory not found")
        return memory