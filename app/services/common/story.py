"""Story service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.story import Story
from app.infra.repo.story_repository import StoryRepository


class StoryService(BaseService[Story]):
    """Service for Story entity."""

    def __init__(self):
        super().__init__(StoryRepository())

__all__ = ["StoryService"] 