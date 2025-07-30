from app.core.db.repository import Repository
from ..models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

class UserRepository(Repository[User]):
    """
    Repository class for User model.
    これは User model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        # 初始化时接收db参数
        super().__init__(User)
        self.db = db

    async def get_by_id(self, user_id: int):
        stmt = select(self.model).where(self.model.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str):
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(self.model.id).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalar() is not None
        
    async def create(self, obj_in: Dict[str, Any]) -> User:
        """覆盖基类方法，使用self.db而不是参数db"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj 