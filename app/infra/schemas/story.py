from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict, TypeAdapter
from datetime import datetime
from core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.story import Story as ORM_Story

# 创建用 schema
class StoryCreateSchema(BaseModel):
    """
    The Story create schema by Pydantic.
    """
    content: str = Field(..., description="The content of the story.")
    summary: str = Field(..., description="The summary of the story.")
    category: str = Field(..., description="The category of the story.")
    language: str = Field(..., description="The language of the story.")

# 对外 schema
class StorySchema(StoryCreateSchema):
    """
    The Story schema by Pydantic.
    """
    
    id: int | None = Field(default=None, description="The ID of the story.")
    created_at: datetime = Field(..., description="The created time of the story.")
    updated_at: datetime = Field(..., description="The updated time of the story.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Story":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from app.infra.context import uow_ctx
        uow = uow_ctx.get()

        if self.id is None:
            raise NotFoundException(message="Story not found")

        story = await uow.db.get(ORM_Story, self.id)
        if story is None:
            raise NotFoundException(message="Story not found")

        user = uow.current_user
        if user is None or story.user_id != user.id:
            raise NotFoundException(message="Story not found")
        return story

# ListAdapter
StorySchemaListAdapter = TypeAdapter(list[StorySchema])