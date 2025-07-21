from app.core.db.repository import Repository
from ..models.refresh_token import RefreshToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self):
        super().__init__(RefreshToken)

    async def get_by_token(self, db: AsyncSession, token: str):
        stmt = select(self.model).where(self.model.token == token)
        result = await db.execute(stmt)
        return result.scalars().first()

__all__ = ["RefreshTokenRepository"] 