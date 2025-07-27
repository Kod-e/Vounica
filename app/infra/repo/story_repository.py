from app.core.db.repository import Repository
from ..models import Story
from sqlalchemy.ext.asyncio import AsyncSession


class StoryRepository(Repository[Story]):
    """Repository class for Story model.
    これは Story model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Story)
        self.db = db 