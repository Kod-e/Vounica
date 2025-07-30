from fastapi import APIRouter, Depends, Body, Query
from app.infra.schemas import MistakeSchema, MistakeCreateSchema, MistakeSchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.mistake import MistakeService
from typing import List

router = APIRouter(prefix="/mistake", tags=["mistake"])

# 服务依赖
async def get_mistake_service() -> MistakeService:
    return MistakeService()

# 创建新的mistake记录
@router.post("/create", response_model=MistakeSchema)
async def create_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake: MistakeCreateSchema = Body(...)
):
    mistake_obj = await mistake_service.create(mistake.model_dump())
    return MistakeSchema.model_validate(mistake_obj)

# 删除mistake
@router.delete("/delete", response_model=MistakeSchema)
async def delete_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake_id: int = Query(...)
):
    mistake_obj = await mistake_service.delete(mistake_id)
    return MistakeSchema.model_validate(mistake_obj)

# 更新mistake
@router.post("/update", response_model=MistakeSchema)
async def update_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake: MistakeSchema = Body(...)
):
    mistake_obj = await mistake_service.update(mistake.id, mistake.model_dump())
    return MistakeSchema.model_validate(mistake_obj)

# 获取mistake列表
@router.get("/page", response_model=MistakeSchemaListAdapter)
async def get_mistakes(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    limit: int = 50,
    offset: int = 0
):
    mistakes = await mistake_service.list(skip=offset, limit=limit)
    return MistakeSchemaListAdapter.validate_python(mistakes)

# 获取用户最近错题
@router.get("/recent", response_model=MistakeSchemaListAdapter)
async def get_recent_mistakes(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    limit: int = 5,
    offset: int = 0
):
    mistakes = await mistake_service.get_user_mistakes(limit=limit, offset=offset)
    return MistakeSchemaListAdapter.validate_python(mistakes) 