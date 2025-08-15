from app.core.db.repository import Repository
from ..models import Mistake
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, func

class MistakeRepository(Repository[Mistake]):
    """Repository class for Mistake model.
    これは Mistake model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Mistake)
        self.db = db 
        
        
    # 获得用户最近的几套错题, 并且必须传递language
    async def get_user_mistakes(self, user_id: int,language: str, limit: int = 5,offset: int = 0) -> List[Mistake]:
        """Get the user's recent mistakes."""
        query = select(Mistake).where(Mistake.user_id == user_id).where(Mistake.language == language).order_by(Mistake.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 获取用户有多少道错题, 必须传递language
    async def get_user_mistake_count(self, user_id: int, language: str) -> int:
        """Get the user's mistake count."""
        query = select(func.count(Mistake.id)).where(Mistake.user_id == user_id).where(Mistake.language == language)
        result = await self.db.execute(query)
        return result.scalar()