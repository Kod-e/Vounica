from app.core.db.repository import Repository
from ..models import Grammar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class GrammarRepository(Repository[Grammar]):
    """Repository class for Grammar model.
    これは Grammar model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Grammar)
        self.db = db 
        
    # 获取用户有多少个记录的grammar, 必须传递language
    async def get_user_grammar_count(self, user_id: int, language: str) -> int:
        """Get the user's grammar count."""
        query = select(func.count(Grammar.id)).where(Grammar.user_id == user_id).where(Grammar.language == language)
        result = await self.db.execute(query)
        return result.scalar()