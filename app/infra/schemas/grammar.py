# 记录用户语法的习得状态
from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from core.exceptions import NotFoundException
if TYPE_CHECKING:
    from app.infra.models.grammar import Grammar as ORM_Grammar

# 语法习得状态表, 记录用户语法的习得状态
class Grammar(BaseModel):
    """
    The Grammar schema by Pydantic.
    """
    
    id: int = Field(default=None, description="The ID of the grammar.")
    name: str = Field(..., description="The name of the grammar.")
    usage: str = Field(..., description="The usage of the grammar.")
    status: float = Field(..., description="The status of the grammar.")
    language: str = Field(..., description="The language of the grammar.")
    created_at: datetime = Field(..., description="The created time of the grammar.")
    updated_at: datetime = Field(..., description="The updated time of the grammar.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Grammar":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from ..context import uow_ctx
        uow = uow_ctx.get()
        grammar = await uow.db.get(ORM_Grammar, self.id)
        user = uow.current_user
        if user is None or user.id != grammar.user_id or grammar is None:
            raise NotFoundException(message="Grammar not found")
        return grammar