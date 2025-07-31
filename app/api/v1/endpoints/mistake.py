from fastapi import APIRouter, Depends, Body, Query
from typing import List
from app.infra.schemas import MistakeSchema, MistakeCreateSchema, MistakeSchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.mistake import MistakeService

router = APIRouter(prefix="/mistake", tags=["mistake"])

async def get_mistake_service() -> MistakeService:
    return MistakeService()

# 创建新的错题记录
@router.post("/create", response_model=MistakeSchema)
async def create_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake: MistakeCreateSchema = Body(...)
):
    mistake = await mistake_service.create(mistake.model_dump())
    return MistakeSchema.model_validate(mistake)


# 删除一个错题
@router.delete("/delete", response_model=MistakeSchema)
async def delete_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake_id: int = Query(...)
):
    mistake = await mistake_service.delete(mistake_id)
    return MistakeSchema.model_validate(mistake)

# 更新一个错题
@router.post("/update", response_model=MistakeSchema)
async def update_mistake(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    mistake: MistakeSchema = Body(...)
):
    mistake = await mistake_service.update(mistake.model_dump())
    return MistakeSchema.model_validate(mistake)

# 获取用户错题的页面
@router.get("/page", response_model=List[MistakeSchema])
async def get_mistakes(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    limit: int = 50,
    offset: int = 0
):
    mistakes = await mistake_service.get_user_mistakes(offset=offset, limit=limit)
    # 使用TypeAdapter进行高效验证，但FastAPI要求response_model为标准类型
    return MistakeSchemaListAdapter.validate_python(mistakes)

# 获取用户最近的错题
@router.get("/recent", response_model=List[MistakeSchema])
async def get_recent_mistakes(
    uow: UnitOfWork = Depends(get_uow),
    mistake_service: MistakeService = Depends(get_mistake_service),
    limit: int = 50,
    offset: int = 0
):
    mistakes = await mistake_service.get_user_mistakes(limit, offset)
    # 使用TypeAdapter进行高效验证，但FastAPI要求response_model为标准类型
    return MistakeSchemaListAdapter.validate_python(mistakes) 