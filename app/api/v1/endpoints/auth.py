from fastapi import APIRouter, Depends, HTTPException, status
from app.infra.schemas import RegisterSchema, LoginSchema, RefreshSchema, TokenSchema, RegisterResponseSchema, RefreshResponseSchema
from app.infra.uow import UnitOfWork, get_uow
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth.auth_service import AuthService
from app.core.exceptions.base import BaseException as AppException

router = APIRouter(prefix="/auth", tags=["auth"])


# 依赖函数，创建AuthService
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db=db)

# 注册
@router.post("/register", response_model=RegisterResponseSchema)
async def register(
    body: RegisterSchema, 
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.register(db, name=body.name, email=body.email, password=body.password)
        # 注册后直接登录，使用相同的密码
        access_token, refresh = await auth_service.login(db, user.email, body.password)
        # 使用201状态码, 表示资源创建成功
        return RegisterResponseSchema(id=user.id, email=user.email, access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())

# 获得一个Guest用户和Mail用户
@router.post("/guest", response_model=TokenSchema)
@router.get("/guest", response_model=TokenSchema)
async def guest(
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.guest(db)
        access_token, refresh = await auth_service.guest(db)
        return TokenSchema(access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())

@router.post("/login", response_model=TokenSchema)
async def login(
    body: LoginSchema, 
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        access_token, refresh = await auth_service.login(db, body.email, body.password)
        # 使用200状态码, 表示请求成功
        return TokenSchema(access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())


@router.post("/refresh", response_model=RefreshResponseSchema)
async def refresh(
    body: RefreshSchema, 
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        access_token = await auth_service.refresh(db, refresh_token=body.refresh_token)
        # 使用200状态码, 表示请求成功
        return RefreshResponseSchema(access_token=access_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict()) 