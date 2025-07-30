from fastapi import APIRouter, Depends, Body, Query
from typing import List
from app.infra.schemas import GrammarSchema, GrammarCreateSchema, GrammarSchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common import BaseService
from app.infra.models.grammar import Grammar
from app.infra.context import uow_ctx
from app.infra.repo.grammar_repository import GrammarRepository

router = APIRouter(prefix="/grammar", tags=["grammar"])

# 服务依赖
async def get_grammar_service() -> BaseService[Grammar]:
    uow = uow_ctx.get()
    repo = GrammarRepository(db=uow.db)
    return BaseService[Grammar](repo)

# 创建新的grammar记录
@router.post("/create", response_model=GrammarSchema)
async def create_grammar(
    uow: UnitOfWork = Depends(get_uow),
    grammar_service: BaseService = Depends(get_grammar_service),
    grammar: GrammarCreateSchema = Body(...)
):
    grammar_obj = await grammar_service.create(grammar.model_dump())
    return GrammarSchema.model_validate(grammar_obj)

# 删除grammar
@router.delete("/delete", response_model=GrammarSchema)
async def delete_grammar(
    uow: UnitOfWork = Depends(get_uow),
    grammar_service: BaseService = Depends(get_grammar_service),
    grammar_id: int = Query(...)
):
    grammar_obj = await grammar_service.delete(grammar_id)
    return GrammarSchema.model_validate(grammar_obj)

# 更新grammar
@router.post("/update", response_model=GrammarSchema)
async def update_grammar(
    uow: UnitOfWork = Depends(get_uow),
    grammar_service: BaseService = Depends(get_grammar_service),
    grammar: GrammarSchema = Body(...)
):
    grammar_obj = await grammar_service.update(grammar.id, grammar.model_dump())
    return GrammarSchema.model_validate(grammar_obj)

# 获取grammar列表
@router.get("/page", response_model=List[GrammarSchema])
async def get_grammars(
    uow: UnitOfWork = Depends(get_uow),
    grammar_service: BaseService = Depends(get_grammar_service),
    limit: int = 50,
    offset: int = 0
):
    grammars = await grammar_service.list(skip=offset, limit=limit)
    # 使用TypeAdapter进行高效验证，但FastAPI要求response_model为标准类型
    return GrammarSchemaListAdapter.validate_python(grammars) 