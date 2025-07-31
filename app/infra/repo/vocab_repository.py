from app.core.db.repository import Repository
from ..models import Vocab
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class VocabRepository(Repository[Vocab]):
    """Repository class for Vocab model.
    これは Vocab model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Vocab)
        self.db = db 
        
    async def get_user_vocabs(self, user_id: int, offset: int = 0, limit: int = 100,language: str = None) -> List[Vocab]:
        """Get the user's vocabs."""
        query = select(Vocab).where(Vocab.user_id == user_id)
        if language:
            query = query.where(Vocab.language == language)
        vocabs = await self.db.execute(query.offset(offset).limit(limit))
        return vocabs.scalars().all()
    
    