"""Story service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.story import Story
from app.infra.repo.story_repository import StoryRepository
from app.infra.uow import UnitOfWork


class StoryService(BaseService[Story]):
    """Service for Story entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        super().__init__(StoryRepository(db=uow.db))

__all__ = ["StoryService"] 