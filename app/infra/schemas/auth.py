from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    """
    Login request schema.
    
    ログインリクエストスキーマ。
    """
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    """
    Token response schema.
    
    トークンレスポンススキーマ。
    """
    access_token: str
    refresh_token: str

class RefreshTokenSchema(BaseModel):
    """
    Refresh token request schema.
    
    リフレッシュトークンリクエストスキーマ。
    """
    refresh_token: str

__all__ = [
    "LoginSchema",
    "TokenSchema",
    "RefreshTokenSchema",
]
