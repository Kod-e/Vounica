from fastapi import APIRouter, Depends, Body, Query
from typing import List, Dict
from app.infra.schemas import MemorySchema, MemoryCreateSchema, MemoryUpdateSchema, MemorySchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.memory import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])

async def get_memory_service() -> MemoryService:
    return MemoryService()

# 创建新的记忆
@router.post("/create", response_model=MemorySchema)
async def create_memory(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service),
    memory: MemoryCreateSchema = Body(...)
):
    memory = await memory_service.create_memory(memory)
    return MemorySchema.model_validate(memory)


# 删除一个记忆
@router.delete("/delete", response_model=MemorySchema)
async def delete_memory(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service),
    memory_id: int = Query(...)
):
    memory = await memory_service.delete_memory(memory_id)
    return MemorySchema.model_validate(memory)

# 更新一个记忆
@router.post("/update", response_model=MemorySchema)
async def update_memory(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service),
    memory: MemoryUpdateSchema = Body(...)
):
    memory = await memory_service.update_memory(memory)
    return MemorySchema.model_validate(memory)

# 获取用户记忆的页面
@router.get("/page", response_model=List[MemorySchema])
async def get_memories(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service),
    limit: int = 50,
    offset: int = 0
):
    memories = await memory_service.get_user_memories(limit, offset)
    # 使用TypeAdapter进行高效验证
    return MemorySchemaListAdapter.validate_python(memories)

# 获取所有的记忆的category的string
@router.get("/categories", response_model=List[str])
async def get_memory_categories(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service)
):
    return await memory_service.get_user_memory_categories()

# 从Category中获取记忆list
@router.get("/category/page", response_model=List[MemorySchema])
async def get_memory_by_category(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service),
    category: str = Query(...),
    limit: int = 50,
    offset: int = 0
):
    memories = await memory_service.get_memory_by_category(category, limit, offset)
    # 使用TypeAdapter进行高效验证
    return MemorySchemaListAdapter.validate_python(memories)

# 获取用户的记忆的category的string, 并且带上number
@router.get("/categories/number", response_model=Dict[str, int])
async def get_memory_categories_with_number(
    uow: UnitOfWork = Depends(get_uow),
    memory_service: MemoryService = Depends(get_memory_service)
):
    memory_categories = await memory_service.get_user_memory_categories_with_number()
    return memory_categories
