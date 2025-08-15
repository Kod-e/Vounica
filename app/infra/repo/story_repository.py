from app.core.db.repository import Repository
from ..models import Story
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, desc, func
from typing import Dict

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
    
    # 获取用户的所有故事的category
    async def get_user_story_categories(self, user_id: int) -> List[str]:
        """Get the user's all story categories."""
        query = select(Story.category).where(Story.user_id == user_id).distinct()
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 从Category中获取故事list
    async def get_story_by_category(self, user_id: int, category: str, limit: int = 50, offset: int = 0) -> List[Story]:
        """Get the user's stories by category."""
        query = select(Story).where(Story.user_id == user_id, Story.category == category).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 获取用户的所有故事的category, 并且带上number, 方便AI理解,  返回结构是str:number
    async def get_category_counts(self, user_id: int) -> Dict[str, int]:
        """Get the user's story category counts."""
        query = select(Story.category, func.count(Story.id).label('count')).where(
            Story.user_id == user_id
        ).group_by(Story.category)
        result = await self.db.execute(query)
        return {row.category: row.count for row in result}
    
    # 从Story中获得256条以内的story
    # 首先按照story的language为target排序, 
    # 最后按照story的updated_at排序
    async def get_story_by_language(self, user_id: int, language: str, limit: int = 256) -> List[Story]:
        """Get the user's stories by language."""
        query = select(Story).where(Story.user_id == user_id, Story.language == language).order_by(desc(Story.updated_at)).limit(limit)
        result = await self.db.execute(query)
        count = len(result.scalars().all())
        # 如果result的length小于limit, 继续按照规则查询不为target的memory, 直到长度达到limit
        if count < limit:
            # 查询不为target的memory, limit为limit - count
            limit = limit - count
            query = select(Story).where(Story.user_id == user_id, Story.language != language).order_by(desc(Story.updated_at)).limit(limit)
            result = await self.db.execute(query)
        return result.scalars().all()

    