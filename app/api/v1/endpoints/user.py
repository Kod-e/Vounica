from fastapi import APIRouter, Depends, HTTPException, status
from app.infra.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse , RegisterResponse, RefreshResponse
from app.infra.uow  import UnitOfWork, get_uow
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth.auth_service import AuthService
from app.core.exceptions.base import BaseException as AppException

router = APIRouter(prefix="/auth", tags=["auth"])


auth_service = AuthService()


@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register(db, name=body.name, email=body.email, password=body.password)
        access_token, refresh = await auth_service.login(db, user.email, body.password) # 这里需要修改, 因为注册的时候没有密码
        # 使用201状态码, 表示资源创建成功
        return RegisterResponse(id=user.id, email=user.email, access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token, refresh = await auth_service.login(db, body.email, body.password)
        # 使用200状态码, 表示请求成功
        return TokenResponse(access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token = await auth_service.refresh(db, refresh_token=body.refresh_token)
        # 使用200状态码, 表示请求成功
        return RefreshResponse(access_token=access_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict()) 