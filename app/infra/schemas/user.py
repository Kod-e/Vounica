from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
if TYPE_CHECKING:
    from app.infra.models.user import User as ORM_User

class UserCreateSchema(BaseModel):
    """
    The User create schema by Pydantic.
    
    ユーザー作成用スキーマ。
    """
    name: str = Field(..., description="The name of the user.")
    email: EmailStr = Field(..., description="The email of the user.")
    password: str = Field(..., description="The password of the user.")

class UserUpdateSchema(BaseModel):
    """
    The User update schema by Pydantic.
    
    ユーザー更新用スキーマ。
    """
    name: Optional[str] = Field(None, description="The name of the user.")
    email: Optional[EmailStr] = Field(None, description="The email of the user.")
    password: Optional[str] = Field(None, description="The password of the user.")
    token_quota: Optional[int] = Field(None, description="The token quota of the user.")

class UserSchema(BaseModel):
    """
    The User schema by Pydantic.
    
    ユーザースキーマ。
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

__all__ = [
    "UserCreateSchema",
    "UserUpdateSchema",
    "UserSchema",
]