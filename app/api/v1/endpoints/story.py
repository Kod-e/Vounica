from fastapi import APIRouter, Depends, Body, Query
from typing import List
from app.infra.schemas import StorySchema, StoryCreateSchema, StorySchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.story import StoryService

router = APIRouter(prefix="/story", tags=["story"])

async def get_story_service() -> StoryService:
    return StoryService()

# 创建新的story记录
@router.post("/create", response_model=StorySchema)
async def create_story(
    uow: UnitOfWork = Depends(get_uow),
    story_service: StoryService = Depends(get_story_service),
    story: StoryCreateSchema = Body(...)
):
    story_obj = await story_service.create(story.model_dump())
    return StorySchema.model_validate(story_obj)

# 删除story
@router.delete("/delete", response_model=StorySchema)
async def delete_story(
    uow: UnitOfWork = Depends(get_uow),
    story_service: StoryService = Depends(get_story_service),
    story_id: int = Query(...)
):
    story_obj = await story_service.delete(story_id)
    return StorySchema.model_validate(story_obj)

# 更新story
@router.post("/update", response_model=StorySchema)
async def update_story(
    uow: UnitOfWork = Depends(get_uow),
    story_service: StoryService = Depends(get_story_service),
    story: StorySchema = Body(...)
):
    story_obj = await story_service.update(story.model_dump())
    return StorySchema.model_validate(story_obj)

# 获取story列表
@router.get("/page", response_model=List[StorySchema])
async def get_stories(
    uow: UnitOfWork = Depends(get_uow),
    story_service: StoryService = Depends(get_story_service),
    limit: int = 50,
    offset: int = 0,
    only_target_language: bool = False
):
    stories = await story_service.get_user_stories(offset=offset, limit=limit, only_target_language=only_target_language)
    # 使用TypeAdapter进行高效验证，但FastAPI要求response_model为标准类型
    return StorySchemaListAdapter.validate_python(stories) 