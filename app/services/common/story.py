"""Story service wrapper."""
from typing import List
from app.services.common.common_base import BaseService
from app.infra.models.story import Story
from app.infra.repo.story_repository import StoryRepository
from app.infra.context import uow_ctx


class StoryService(BaseService[Story]):
    """Service for Story entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo : StoryRepository = StoryRepository(db=self._uow.db)
        super().__init__(self._repo)
        
    async def get_user_stories(self, offset: int = 0, limit: int = 100, only_target_language: bool = False) -> List[Story]:
        """Get the user's stories."""
        return await self._repo.get_user_stories(
            user_id=self._uow.current_user.id,
            offset=offset,
            limit=limit,
            language=self._uow.target_language if only_target_language else None
        )

__all__ = ["StoryService"] 