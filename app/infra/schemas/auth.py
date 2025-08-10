from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
class RegisterResponseSchema(BaseModel):
    id: int
    email: str
    access_token: str
    refresh_token: str

class RefreshSchema(BaseModel):
    refresh_token: str

class RefreshResponseSchema(BaseModel):
    access_token: str

__all__ = [
    "RegisterSchema",
    "LoginSchema",
    "TokenSchema",
    "RegisterResponseSchema",
    "RefreshSchema",
    "RefreshResponseSchema",
]
