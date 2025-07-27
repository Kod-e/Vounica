"""Story service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.story import Story
from app.infra.repo.story_repository import StoryRepository
from app.infra.uow import UnitOfWork


class StoryService(BaseService[Story]):
    """Service for Story entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._repo : StoryRepository = StoryRepository(db=uow.db)
        super().__init__(self._repo)

__all__ = ["StoryService"] 