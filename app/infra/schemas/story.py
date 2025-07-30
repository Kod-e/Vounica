from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
if TYPE_CHECKING:
    from app.infra.models.story import Story as ORM_Story

class Story(BaseModel):
    """
    The Story schema by Pydantic.
    """
    
    id: int = Field(default=None, description="The ID of the story.")
    content: str = Field(..., description="The content of the story.")
    summary: str = Field(..., description="The summary of the story.")
    category: str = Field(..., description="The category of the story.")
    language: str = Field(..., description="The language of the story.")
    created_at: datetime = Field(..., description="The created time of the story.")
    updated_at: datetime = Field(..., description="The updated time of the story.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Story":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from ..context import uow_ctx
        uow = uow_ctx.get()