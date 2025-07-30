from fastapi import APIRouter, Depends, Body, Query
from app.infra.schemas import StorySchema, StoryCreateSchema, StorySchemaListAdapter
from app.infra.uow import UnitOfWork, get_uow
from app.services.common.story import StoryService
from typing import List

router = APIRouter(prefix="/story", tags=["story"])

# 服务依赖
async def get_story_service() -> StoryService:
    return StoryService()

# 创建新的story
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
    story_obj = await story_service.update(story.id, story.model_dump())
    return StorySchema.model_validate(story_obj)

# 获取story列表
@router.get("/page", response_model=StorySchemaListAdapter)
async def get_stories(
    uow: UnitOfWork = Depends(get_uow),
    story_service: StoryService = Depends(get_story_service),
    limit: int = 50,
    offset: int = 0
):
    stories = await story_service.list(skip=offset, limit=limit)
    return StorySchemaListAdapter.validate_python(stories) 