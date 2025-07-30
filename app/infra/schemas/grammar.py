# 记录用户语法的习得状态
from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.core.exceptions import NotFoundException
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from app.infra.models.grammar import Grammar as ORM_Grammar

# 创建用 schema（不含 id、时间戳）
class GrammarCreateSchema(BaseModel):
    """
    The Grammar create schema by Pydantic.
    """
    name: str = Field(..., description="The name of the grammar.")
    usage: str = Field(..., description="The usage of the grammar.")
    status: float = Field(..., description="The status of the grammar.")
    language: str = Field(..., description="The language of the grammar.")

# 最终对外 schema
class GrammarSchema(GrammarCreateSchema):
    """
    The Grammar schema by Pydantic.
    """
    
    id: int | None = Field(default=None, description="The ID of the grammar.")
    created_at: datetime = Field(..., description="The created time of the grammar.")
    updated_at: datetime = Field(..., description="The updated time of the grammar.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    async def get_orm(self) -> "ORM_Grammar":
        """Convert the Pydantic model to a SQLAlchemy model."""
        from app.infra.context import uow_ctx
        uow = uow_ctx.get()
        # id 为 None 直接报错
        if self.id is None:
            raise NotFoundException(message="Grammar not found")

        grammar = await uow.db.get(ORM_Grammar, self.id)
        if grammar is None:
            raise NotFoundException(message="Grammar not found")

        user = uow.current_user
        if user is None or grammar.user_id != user.id:
            raise NotFoundException(message="Grammar not found")
        return grammar

# 列表批量转换适配器
GrammarSchemaListAdapter = TypeAdapter(list[GrammarSchema])