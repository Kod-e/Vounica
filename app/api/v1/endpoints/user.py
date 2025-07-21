from fastapi import APIRouter, Depends, HTTPException, status
from app.infra.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse
from app.core.uow import UnitOfWork, get_uow
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth.auth_service import AuthService
from app.core.exceptions.base import BaseException as AppException

router = APIRouter(prefix="/auth", tags=["auth"])


auth_service = AuthService()


@router.post("/register", response_model=dict)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register(db, **body.model_dump())
        return {"id": user.id, "email": user.email}
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token, refresh = await auth_service.login(db, **body.model_dump())
        return TokenResponse(access_token=access_token, refresh_token=refresh)
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict())


@router.post("/refresh", response_model=dict)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token = await auth_service.refresh(db, refresh_token=body.refresh_token)
        return {"access_token": access_token}
    except AppException as exc:
        raise HTTPException(status_code=exc.code, detail=exc.to_dict()) 