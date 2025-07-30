from fastapi import APIRouter, Depends, HTTPException, status
from app.infra.schemas import Memory
from app.infra.uow  import UnitOfWork, get_uow
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth.auth_service import AuthService
from app.core.exceptions.base import BaseException as AppException
from app.services.common.memory import MemoryService
from typing import List

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/", response_model=List[Memory])
async def get_memories(db: AsyncSession = Depends(get_db)):
    return await MemoryService.get_user_memories(db)