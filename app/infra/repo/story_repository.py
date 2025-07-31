from app.core.db.repository import Repository
from ..models import Story
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

class StoryRepository(Repository[Story]):
    """Repository class for Story model.
    これは Story model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Story)
        self.db = db 
        
    async def get_user_stories(self, user_id: int, offset: int = 0, limit: int = 100,language: str = None) -> List[Story]:
        """Get the user's stories."""
        query = select(Story).where(Story.user_id == user_id)
        if language:
            query = query.where(Story.language == language)
        stories = await self.db.execute(query.offset(offset).limit(limit))
        return stories.scalars().all()