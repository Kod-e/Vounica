from app.core.db.repository import Repository
from ..models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository(Repository[User]):
    """
    Repository class for User model.
    これは User model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        # 初始化时仅传入模型类，Session 由具体调用方法时注入
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str):
        stmt = select(self.model).where(self.model.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def exists_by_email(self, db: AsyncSession, email: str) -> bool:
        stmt = select(self.model.id).where(self.model.email == email)
        result = await db.execute(stmt)
        return result.scalar() is not None 