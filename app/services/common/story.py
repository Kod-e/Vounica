"""Story service wrapper."""

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

__all__ = ["StoryService"] 