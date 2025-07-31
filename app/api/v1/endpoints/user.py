from fastapi import APIRouter, Depends
from app.infra.schemas import UserSchema
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.common import UserService
from app.infra.uow import UnitOfWork, get_uow

router = APIRouter(prefix="/user", tags=["user"])


# 依赖函数，创建AuthService
async def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService()


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_current_user()
    return UserSchema.model_validate(user)