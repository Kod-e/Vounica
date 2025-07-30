from app.core.db.repository import Repository
from ..models.refresh_token import RefreshToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken)
        self.db = db

    async def get_by_token(self, token: str):
        stmt = select(self.model).where(self.model.token == token)
        result = await self.db.execute(stmt)
        return result.scalars().first()
        
    async def create(self, obj_in: Dict[str, Any]) -> RefreshToken:
        """覆盖基类方法，使用self.db而不是参数db"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

__all__ = ["RefreshTokenRepository"] 