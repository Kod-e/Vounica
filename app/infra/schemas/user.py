from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
if TYPE_CHECKING:
    from app.infra.models.user import User as ORM_User

class UserSchema(BaseModel):
    """
    The User schema by Pydantic.
    """
    
    id: int = Field(default=None, description="The ID of the user.")
    name: str = Field(..., description="The name of the user.")
    email: str = Field(..., description="The email of the user.")
    token_quota: int = Field(..., description="The token quota of the user.")
    created_at: datetime = Field(..., description="The created time of the user.")
    updated_at: datetime = Field(..., description="The updated time of the user.")
    
    model_config = ConfigDict(
        from_attributes=True,
    )