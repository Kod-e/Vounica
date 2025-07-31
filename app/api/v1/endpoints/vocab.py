from fastapi import APIRouter, Depends, Body, Query
from typing import List
from app.infra.schemas import VocabSchema, VocabCreateSchema, VocabSchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.vocab import VocabService

router = APIRouter(prefix="/vocab", tags=["vocab"])

async def get_vocab_service() -> VocabService:
    return VocabService()

# 创建新的vocab记录
@router.post("/create", response_model=VocabSchema)
async def create_vocab(
    uow: UnitOfWork = Depends(get_uow),
    vocab_service: VocabService = Depends(get_vocab_service),
    vocab: VocabCreateSchema = Body(...)
):
    vocab_obj = await vocab_service.create(vocab.model_dump())
    return VocabSchema.model_validate(vocab_obj)

# 删除vocab
@router.delete("/delete", response_model=VocabSchema)
async def delete_vocab(
    uow: UnitOfWork = Depends(get_uow),
    vocab_service: VocabService = Depends(get_vocab_service),
    vocab_id: int = Query(...)
):
    vocab_obj = await vocab_service.delete(vocab_id)
    return VocabSchema.model_validate(vocab_obj)

# 更新vocab
@router.post("/update", response_model=VocabSchema)
async def update_vocab(
    uow: UnitOfWork = Depends(get_uow),
    vocab_service: VocabService = Depends(get_vocab_service),
    vocab: VocabSchema = Body(...)
):
    vocab_obj = await vocab_service.update(vocab.model_dump())
    return VocabSchema.model_validate(vocab_obj)

# 获取vocab列表
@router.get("/page", response_model=List[VocabSchema])
async def get_vocabs(
    uow: UnitOfWork = Depends(get_uow),
    vocab_service: VocabService = Depends(get_vocab_service),
    limit: int = 50,
    offset: int = 0
):
    vocabs = await vocab_service.get_user_vocabs(offset=offset, limit=limit)
    # 使用TypeAdapter进行高效验证，但FastAPI要求response_model为标准类型
    return VocabSchemaListAdapter.validate_python(vocabs) 