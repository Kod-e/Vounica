from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr

class RefreshResponse(BaseModel):
    access_token: str

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "RefreshRequest",
    "TokenResponse",
    "RegisterResponse",
    "RefreshResponse",
]
